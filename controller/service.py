"""Local HTTP controller and optional OpenCV camera capture for R.O.B. Vision."""

import argparse
import json
import os
import glob
import hashlib
import http.client
import ipaddress
import math
import re
import socket
import ssl
import sys
import threading
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from time import monotonic, time
from urllib.parse import urlsplit

from .model import GyroState, StackState
from .optical import ALLOWED, PATTERNS, OpticalDecoder, TestFlashDetector
from .kiyo_camera import configure_kiyo_pro
from tools.identify_game import identify, load_registry

ROOT = Path(__file__).resolve().parents[1]
MIME = {".html": "text/html", ".js": "text/javascript", ".css": "text/css",
        ".svg": "image/svg+xml", ".pdf": "application/pdf", ".png": "image/png",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".ttf": "font/ttf"}
KIYO_CAPTURE_MODES = {"mjpg480": ("MJPG", 640, 480), "yuyv720": ("YUYV", 1280, 720)}


def preferred_kiyo_capture_mode():
    """Read an optional device-local mode; fall back to the known 480p mode."""
    try:
        mode = (ROOT / "data" / "camera-mode").read_text().strip().lower()
    except OSError:
        mode = "mjpg480"
    return mode if mode in KIYO_CAPTURE_MODES else "mjpg480"


def capture_devices():
    """List likely V4L2 cameras, omitting the UNO Q's video codec nodes."""
    devices = []
    for path in sorted(glob.glob("/dev/video*")):
        name_file = Path("/sys/class/video4linux") / Path(path).name / "name"
        try:
            name = name_file.read_text().strip()
        except OSError:
            name = Path(path).name
        if any(word in name.casefold() for word in ("encoder", "decoder", "codec")):
            continue
        devices.append({"path": path, "name": name})
    return devices


def pair_retropie(host, code, fingerprint, token, port=8768):
    """Send the controller token only after checking the console's TLS fingerprint."""
    if not isinstance(host, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]{0,252}", host):
        raise ValueError("Enter a RetroPie hostname or local IP address.")
    if not isinstance(code, str) or not re.fullmatch(r"[0-9]{6}", code):
        raise ValueError("Enter the six-digit code shown on RetroPie.")
    fingerprint = re.sub(r"[^0-9a-fA-F]", "", str(fingerprint)).lower()
    if len(fingerprint) != 64:
        raise ValueError("Enter the console's 64-character SHA-256 fingerprint.")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("Invalid pairing port.")
    if not token:
        raise ValueError("Configure a controller token before pairing.")
    addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_private for item in addresses):
        raise ValueError("Pairing is available only on a private network.")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    connection = http.client.HTTPSConnection(addresses[0][4][0], port, context=context, timeout=8)
    try:
        connection.connect()
        actual = hashlib.sha256(connection.sock.getpeercert(binary_form=True)).hexdigest()
        if actual != fingerprint:
            raise ValueError("Console fingerprint does not match. Pairing stopped before sending the token.")
        body = json.dumps({"code": code, "token": token}).encode()
        connection.request("POST", "/pair", body=body, headers={"Content-Type": "application/json"})
        response = connection.getresponse()
        result = json.load(response)
        if response.status != 200 or result.get("paired") is not True:
            raise ValueError(result.get("error", "Console did not confirm pairing."))
        return {"paired": True, "host": host}
    finally:
        connection.close()


class Controller:
    def __init__(self, camera_roi=None):
        self.lock = threading.RLock()
        self.game = None
        self.stack = StackState()
        self.gyro = GyroState()
        self.decoder = OpticalDecoder()
        self.test_flash_detector = TestFlashDetector()
        self.sequence = 0
        self.events = []
        self.camera = {"state": "offline", "fps": 0, "brightness": 0, "last_frame": None,
                       "devices": capture_devices(), "platform": sys.platform, "message": "Camera not started."}
        self.devices_checked_at = monotonic()
        self.capture_stop = threading.Event()
        self.capture_thread = None
        self.camera_control_lock = threading.Lock()
        self.camera_index = 0
        self.camera_roi = camera_roi
        self.preview_frame = None
        self.camera_trace = deque(maxlen=1800)
        self.receiver_last_seen = 0.0
        self.receiver_name = None
        self.frame_hook_last_seen = 0.0
        self.frame_hook_game = None
        self.frame_hook_commands = deque(maxlen=128)
        self.test_armed_at = 0.0
        self.test_ready_at = 0.0
        self.test_flash_seen_at = 0.0
        self.test_signal_announced = False

    def event(self, kind, message, command=None):
        self.sequence += 1
        self.events.append({"seq": self.sequence, "time": time(), "kind": kind, "message": message, "command": command})
        self.events = self.events[-30:]

    def snapshot(self):
        with self.lock:
            if self.game == "gyromite":
                for color in self.gyro.expire_assist():
                    self.event("assist", f"{color.title()} Gate Assist timed out; button released.")
            if monotonic() - self.devices_checked_at > 5:
                self.camera["devices"] = capture_devices()
                self.devices_checked_at = monotonic()
            return {"schema": 1, "sequence": self.sequence, "game": self.game,
                    "robot": self.stack.snapshot() if self.game == "stack_up" else self.gyro.snapshot() if self.game == "gyromite" else None,
                    "camera": dict(self.camera), "events": list(self.events),
                    "link": {"online": monotonic() - self.receiver_last_seen < 3.0,
                             "receiver": self.receiver_name},
                    "input": {"frame_hook": self.frame_hook_active()},
                    "test": {"armed": bool(self.test_armed_at), "ready": self.test_ready_at >= self.test_armed_at > 0,
                             "ready_at": self.test_ready_at,
                             "flash_active": self.camera["state"] == "capturing" and self.test_armed_at > 0 and
                             monotonic() - self.test_flash_seen_at < .25}}

    def frame_hook_active(self):
        return self.frame_hook_game == self.game and monotonic() - self.frame_hook_last_seen < 1.0

    def receiver_seen(self, name, frame_hook_game=None):
        with self.lock:
            self.receiver_name = name[:64]
            self.receiver_last_seen = monotonic()
            if frame_hook_game == self.game and frame_hook_game in ("gyromite", "stack_up"):
                self.frame_hook_game = frame_hook_game
                self.frame_hook_last_seen = monotonic()

    def emulator_command(self, game, pattern, sender_pid, frame_index):
        with self.lock:
            if game != self.game or game not in ALLOWED:
                raise ValueError("Frame command does not match the selected game.")
            command = PATTERNS.get(pattern)
            if command not in ALLOWED[game]:
                raise ValueError("Frame command does not match a complete game pattern.")
            if type(sender_pid) is not int or not 1 <= sender_pid <= 2**31 - 1:
                raise ValueError("Invalid frame sender.")
            if type(frame_index) is not int or not 1 <= frame_index <= 2**32 - 1:
                raise ValueError("Invalid frame number.")
            key = (sender_pid, frame_index)
            if key in self.frame_hook_commands:
                return self.snapshot()
            if game == "gyromite" and command != "READY" and any(self.gyro.assisted_until.values()):
                raise ValueError("Release Gate Assist before moving R.O.B. with commands.")
            self.frame_hook_commands.append(key)
            self.frame_hook_game = game
            self.frame_hook_last_seen = monotonic()
            self.event("decoded", f"Game frame decoded: {command} ({pattern}).", command)
            return self.command(command, "emulator")

    def arm_test(self):
        with self.lock:
            if self.game is None:
                raise ValueError("Select Gyromite or Stack-Up before arming the test.")
            self.test_armed_at = monotonic()
            self.test_ready_at = 0.0
            self.test_flash_seen_at = 0.0
            self.test_signal_announced = False
            self.test_flash_detector.reset()
            self.event("test", "Watching for the game's Test-mode optical signal or ready-light command.")
            return self.snapshot()

    def select(self, game):
        if game not in (None, "gyromite", "stack_up"):
            raise ValueError("Choose Gyromite, Stack-Up, or no game.")
        with self.lock:
            self.game = game
            self.stack, self.gyro = StackState(), GyroState()
            self.frame_hook_game = None
            self.frame_hook_last_seen = 0.0
            self.frame_hook_commands.clear()
            self.decoder.reset()
            self.test_flash_detector.reset()
            self.test_armed_at = self.test_ready_at = 0.0
            self.test_flash_seen_at = 0.0
            self.test_signal_announced = False
            self.event("session", f"{game or 'No game'} selected; virtual pieces reset.")
            return self.snapshot()

    def command(self, command, source="manual"):
        with self.lock:
            if self.game is None:
                raise ValueError("Select a game before sending commands.")
            if self.game == "gyromite" and any(self.gyro.assisted_until.values()) and command != "READY":
                raise ValueError("Release Gate Assist before moving R.O.B. with commands.")
            if command == "READY":
                if source in ("camera", "emulator") and self.test_armed_at:
                    self.test_ready_at = monotonic()
                self.event("ready", "R.O.B. ready-light signal received; no movement.", command)
            else:
                normalized = command.removesuffix("_GYRO").removesuffix("_STACK")
                if source in ("camera", "emulator") and command in ("UP_GYRO", "DOWN_GYRO") and self.game != "gyromite":
                    raise ValueError("Optical command does not belong to the selected game.")
                if source in ("camera", "emulator") and command in ("UP_STACK", "DOWN_STACK") and self.game != "stack_up":
                    raise ValueError("Optical command does not belong to the selected game.")
                model = self.stack if self.game == "stack_up" else self.gyro
                error = model.apply(normalized)
                if error:
                    self.event("blocked", f"{normalized} blocked: {error}", normalized)
                else:
                    if self.test_armed_at:
                        self.test_armed_at = self.test_ready_at = self.test_flash_seen_at = 0.0
                        self.test_signal_announced = False
                        self.test_flash_detector.reset()
                    self.event("action", f"{source.title()} command: {normalized}.", normalized)
            return self.snapshot()

    def gate_assist(self, color, pressed):
        with self.lock:
            if self.game != "gyromite":
                raise ValueError("Gate Assist is only available in Gyromite.")
            if self.camera["state"] == "capturing":
                raise ValueError("Stop the camera before using manual Gate Assist.")
            if color == "all" and pressed is False:
                for gate in ("red", "blue"):
                    self.gyro.assist_gate(gate, False)
                self.event("assist", "Both Gate Assist buttons released.")
            else:
                self.gyro.assist_gate(color, pressed)
                self.event("assist", f"{color.title()} Gate Assist {'pressed' if pressed else 'released'}.")
            return self.snapshot()

    def sample(self, timestamp, brightness):
        with self.lock:
            self.camera_trace.append((round(timestamp, 6), round(brightness, 4)))
            self.camera["brightness"] = round(brightness, 3)
            self.camera["last_frame"] = time()
            if self.test_armed_at and self.test_flash_detector.feed(timestamp, brightness):
                if not self.test_signal_announced:
                    self.event("test", "Test-mode optical signal detected; R.O.B. light blinking.")
                    self.test_signal_announced = True
                self.test_flash_seen_at = monotonic()
            if self.frame_hook_active():
                self.decoder.reset()
                return None
            detection = self.decoder.feed(timestamp, brightness, self.game)
            if detection:
                self.event("decoded", f"Flash decoded: {detection.command} ({detection.pattern}).", detection.command)
                self.command(detection.command, "camera")
            return detection

    def start_camera(self, index=0, roi=None):
        with self.camera_control_lock:
            return self._start_camera(index, roi)

    def _start_camera(self, index=0, roi=None):
        if roi is None:
            roi = self.camera_roi
        if self.capture_thread and self.capture_thread.is_alive():
            if self.camera["state"] == "capturing":
                return self.snapshot()
            raise RuntimeError("The previous camera session is still closing. Try reconnecting again.")
        with self.lock:
            if self.game == "gyromite" and any(self.gyro.assisted_until.values()):
                for color in ("red", "blue"):
                    self.gyro.assist_gate(color, False)
                self.event("assist", "Gate Assist released before camera capture.")
        if roi is not None and (not isinstance(roi, list) or len(roi) != 4 or
                                any(type(value) not in (int, float) or not math.isfinite(value)
                                    for value in roi)):
            raise ValueError("ROI must contain four normalized numbers.")
        if roi is not None and (min(roi) < 0 or max(roi) > 1 or roi[2] <= 0 or roi[3] <= 0 or
                                roi[0] + roi[2] > 1 or roi[1] + roi[3] > 1):
            raise ValueError("ROI must fit inside the camera frame.")
        self.camera_index = index
        self.camera_roi = roi
        devices = capture_devices()
        with self.lock:
            self.camera["devices"] = devices
            self.devices_checked_at = monotonic()
        if os.name == "posix" and Path("/sys/class/video4linux").exists():
            if not devices:
                with self.lock:
                    self.camera.update(state="fault", fps=0, brightness=0, last_frame=None,
                                       message="No camera capture device is attached. Video codec nodes are not cameras.")
                    self.event("fault", self.camera["message"])
                raise RuntimeError(self.camera["message"])
            if index == 0:
                index = devices[0]["path"]
        try:
            import cv2
        except ImportError as exc:
            with self.lock:
                self.camera.update(state="fault", fps=0, brightness=0, last_frame=None,
                                   message="OpenCV is not installed on this controller.")
                self.event("fault", self.camera["message"])
            raise RuntimeError("OpenCV is needed for camera capture. Install opencv-python on the controller.") from exc
        kiyo_configured = False
        try:
            kiyo_configured = configure_kiyo_pro(index)
        except (OSError, ValueError, RuntimeError) as exc:
            with self.lock:
                self.event("camera", f"Kiyo Pro 60 fps setting unavailable: {exc}")
        capture = cv2.VideoCapture(index)
        if not capture.isOpened():
            capture.release()
            with self.lock:
                self.camera.update(state="fault", fps=0, brightness=0, last_frame=None,
                                   message=f"Camera {index} could not be opened.")
                self.event("fault", self.camera["message"])
            raise RuntimeError(f"Camera {index} could not be opened.")
        if kiyo_configured:
            capture_mode = preferred_kiyo_capture_mode()
            fourcc, capture_width, capture_height = KIYO_CAPTURE_MODES[capture_mode]
            capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, capture_width)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, capture_height)
            with self.lock:
                self.camera["mode"] = capture_mode
        # This is a best-effort request; report measured timing below.
        capture.set(cv2.CAP_PROP_FPS, 60)
        self.capture_stop.clear()
        with self.lock:
            self.decoder.reset()
            self.test_flash_detector.reset()
            self.test_flash_seen_at = 0.0
            self.preview_frame = None
            self.camera_trace.clear()
            self.camera.update(state="capturing", message="Measuring frame timing; aim at the flash area.",
                               fps=0, brightness=0, last_frame=None)
            self.event("camera", f"Camera {index} opened.")

        def capture_loop():
            frame_times = deque()
            last_preview = 0.0
            try:
                while not self.capture_stop.is_set():
                    ok, frame = capture.read()
                    timestamp = monotonic()
                    if not ok:
                        raise RuntimeError("Camera stopped delivering frames.")
                    height, width = frame.shape[:2]
                    x, y, w, h = roi or (0.2, 0.2, 0.6, 0.6)
                    crop = frame[int(y * height):int((y + h) * height), int(x * width):int((x + w) * width)]
                    if crop.size == 0:
                        raise RuntimeError("Camera region is empty.")
                    # White and green command frames have similar luminance on
                    # this display. Measure green above both other channels.
                    b, g, r, _ = cv2.mean(crop)
                    brightness = max(0.0, min(1.0, (g - max(r, b)) / 255))
                    frame_times.append(timestamp)
                    while frame_times and timestamp - frame_times[0] > 4:
                        frame_times.popleft()
                    fps = ((len(frame_times) - 1) / (frame_times[-1] - frame_times[0])
                           if len(frame_times) > 1 and frame_times[-1] > frame_times[0] else 0.0)
                    with self.lock:
                        self.camera["fps"] = round(fps, 1)
                        self.camera["message"] = (
                            "Below 60 delivered fps: one-frame game flashes cannot be captured reliably."
                            if fps and fps < 55 else
                            "Near 60 fps: timing drift can still miss a one-frame flash; verify commands in Test mode."
                            if fps else "Measuring camera frame rate."
                        )
                    self.sample(timestamp, brightness)
                    if timestamp - last_preview >= .5:
                        x0, y0 = int(x * width), int(y * height)
                        x1, y1 = int((x + w) * width), int((y + h) * height)
                        with self.lock:
                            self.preview_frame = (frame.copy(), (x0, y0, x1, y1))
                        last_preview = timestamp
            except Exception as exc:
                with self.lock:
                    self.preview_frame = None
                    self.camera.update(state="fault", fps=0, brightness=0, last_frame=None, message=str(exc))
                    self.event("fault", f"Camera fault: {exc}")
            finally:
                capture.release()
                with self.lock:
                    self.preview_frame = None
                    if self.camera["state"] != "fault":
                        self.camera.update(state="offline", fps=0, brightness=0, last_frame=None, message="Camera stopped.")
                        self.event("camera", "Camera stopped.")

        self.capture_thread = threading.Thread(target=capture_loop, daemon=True)
        self.capture_thread.start()
        return self.snapshot()

    def stop_camera(self):
        with self.camera_control_lock:
            return self._stop_camera()

    def _stop_camera(self):
        self.capture_stop.set()
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
            if self.capture_thread.is_alive():
                with self.lock:
                    self.camera.update(state="fault", message="Camera did not stop. Check the connection and try again.")
                    self.event("fault", self.camera["message"])
                raise RuntimeError(self.camera["message"])
        with self.lock:
            self.preview_frame = None
            self.decoder.reset()
            self.test_flash_detector.reset()
            self.test_flash_seen_at = 0.0
            self.camera.update(state="offline", fps=0, brightness=0, last_frame=None,
                               devices=capture_devices(), message="Camera stopped. Reconnect to scan for a camera again.")
            self.devices_checked_at = monotonic()
        return self.snapshot()

    def reconnect_camera(self):
        with self.camera_control_lock:
            index, roi = self.camera_index, self.camera_roi
            self._stop_camera()
            return self._start_camera(index, roi)


def serve(host="127.0.0.1", port=8766, token=None, camera_index=None, camera_roi=None, matrix=None):
    if host not in ("127.0.0.1", "localhost", "::1") and not token:
        raise ValueError("A bearer token is required when serving over the network.")
    controller = Controller(camera_roi)
    matrix_stop = threading.Event()
    matrix_thread = None
    if matrix is not None:
        matrix_thread = threading.Thread(target=matrix.run, args=(controller.snapshot, matrix_stop), daemon=True)
        matrix_thread.start()
    if camera_index is not None:
        try:
            controller.start_camera(camera_index, camera_roi)
        except RuntimeError as exc:
            print(f"Camera startup failed: {exc}", flush=True)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            if args and "GET /api/state " in str(args[0]):
                return
            super().log_message(format, *args)

        def respond(self, status, value):
            body = json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def authorized(self):
            if token and self.headers.get("Authorization") != f"Bearer {token}":
                self.respond(401, {"error": "Controller token required."})
                return False
            return True

        def browser_request(self):
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                self.respond(415, {"error": "JSON requests are required."})
                return False
            if self.headers.get("Sec-Fetch-Site", "same-origin") not in ("same-origin", "none"):
                self.respond(403, {"error": "Cross-site controls are not allowed."})
                return False
            origin = self.headers.get("Origin")
            if origin:
                parsed = urlsplit(origin)
                hosts = {self.headers.get("Host", "").lower(),
                         self.headers.get("X-Rob-Original-Host", "").lower()}
                if parsed.scheme not in ("http", "https") or parsed.netloc.lower() not in hosts:
                    self.respond(403, {"error": "Cross-site controls are not allowed."})
                    return False
            return True

        def do_GET(self):
            path = urlsplit(self.path).path
            if path.startswith("/api/"):
                if path == "/api/state":
                    if self.headers.get("X-ROB-Receiver") == "retropie" and token and self.headers.get("Authorization") == f"Bearer {token}":
                        controller.receiver_seen("RetroPie", self.headers.get("X-ROB-Frame-Hook"))
                    return self.respond(200, controller.snapshot())
                if path == "/api/matrix/state":
                    return self.respond(200, matrix.status() if matrix is not None else
                                        {"available": False, "bridge_ok": False, "mode": None})
                if path == "/api/camera/frame":
                    with controller.lock:
                        preview = controller.preview_frame
                    if preview is None:
                        self.send_response(204)
                        self.end_headers()
                        return
                    import cv2
                    frame, (x0, y0, x1, y1) = preview
                    frame = frame.copy()
                    cv2.rectangle(frame, (x0, y0), (x1, y1), (84, 225, 117), 2)
                    ok_jpeg, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 68])
                    if not ok_jpeg:
                        self.send_response(204)
                        self.end_headers()
                        return
                    frame = encoded.tobytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Length", str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    return
                if path == "/api/camera/trace":
                    with controller.lock:
                        trace = list(controller.camera_trace)
                    return self.respond(200, {"samples": trace, "roi": controller.camera_roi})
                return self.respond(404, {"error": "Unknown endpoint."})
            if path == "/":
                self.send_response(302)
                self.send_header("Location", "/dashboard/")
                self.end_headers()
                return
            if path == "/dashboard/":
                path = "/dashboard/index.html"
            file = (ROOT / path.lstrip("/")).resolve()
            if not file.is_relative_to(ROOT / "dashboard") or not file.is_file() or not path.startswith("/dashboard/"):
                self.send_error(404)
                return
            body = file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", MIME.get(file.suffix, "application/octet-stream"))
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            path = urlsplit(self.path).path
            if not self.browser_request():
                return
            if path in ("/api/launch", "/api/emulator/command") and not self.authorized():
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size < 0 or size > 4096:
                    raise ValueError("Request too large.")
                data = json.loads(self.rfile.read(size) or b"{}")
                if path == "/api/game":
                    result = controller.select(data.get("game"))
                elif path == "/api/launch":
                    game = identify(data.get("system", ""), data.get("rom", ""), load_registry()) if data.get("event") == "start" else None
                    result = controller.select(game)
                elif path == "/api/command":
                    result = controller.command(data["command"])
                elif path == "/api/emulator/command":
                    result = controller.emulator_command(data["game"], data["pattern"],
                                                         data["sender_pid"], data["frame_index"])
                elif path == "/api/gate-assist":
                    result = controller.gate_assist(data["color"], data["pressed"])
                elif path == "/api/test/arm":
                    result = controller.arm_test()
                elif path == "/api/pair":
                    if matrix is not None:
                        matrix.show_pairing()
                    try:
                        result = pair_retropie(data["host"], data["code"], data["fingerprint"], token)
                    finally:
                        if matrix is not None:
                            matrix.clear_pairing()
                elif path == "/api/matrix/pairing":
                    if not isinstance(data.get("active"), bool):
                        raise ValueError("Choose whether pairing is active.")
                    if matrix is not None:
                        matrix.show_pairing() if data["active"] else matrix.clear_pairing()
                    result = controller.snapshot()
                elif path == "/api/camera/start":
                    result = controller.start_camera(int(data.get("index", 0)), data.get("roi"))
                elif path == "/api/camera/stop":
                    result = controller.stop_camera()
                elif path == "/api/camera/reconnect":
                    result = controller.reconnect_camera()
                else:
                    return self.respond(404, {"error": "Unknown endpoint."})
                self.respond(200, result)
            except (ValueError, KeyError, TypeError, RuntimeError, OSError, http.client.HTTPException) as exc:
                self.respond(400, {"error": str(exc)})

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"R.O.B. Vision controller: http://{host}:{port}/dashboard/", flush=True)
    try:
        server.serve_forever()
    finally:
        matrix_stop.set()
        if matrix_thread is not None:
            matrix_thread.join(timeout=2)
        controller.stop_camera()
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--token", default=os.environ.get("ROB_VISION_TOKEN"))
    parser.add_argument("--camera-index", type=int, help="Open this camera on the main thread at startup (useful on macOS).")
    parser.add_argument("--camera-roi", help="Normalized x,y,width,height crop, e.g. 0.2,0.2,0.6,0.6")
    args = parser.parse_args()
    configured_roi = args.camera_roi or os.environ.get("ROB_VISION_CAMERA_ROI")
    roi = [float(value) for value in configured_roi.split(",")] if configured_roi else None
    serve(args.host, args.port, args.token, args.camera_index, roi)
