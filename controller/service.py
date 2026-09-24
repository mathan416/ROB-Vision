"""Local HTTP controller and optional OpenCV camera capture for R.O.B. Vision."""

import argparse
import json
import os
import glob
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from time import monotonic, time
from urllib.parse import urlsplit

from .model import GyroState, StackState
from .optical import OpticalDecoder
from tools.identify_game import identify, load_registry

ROOT = Path(__file__).resolve().parents[1]
MIME = {".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml"}


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


class Controller:
    def __init__(self):
        self.lock = threading.RLock()
        self.game = None
        self.stack = StackState()
        self.gyro = GyroState()
        self.decoder = OpticalDecoder()
        self.sequence = 0
        self.events = []
        self.camera = {"state": "offline", "fps": 0, "brightness": 0, "last_frame": None,
                       "devices": capture_devices(), "platform": sys.platform, "message": "Camera not started."}
        self.devices_checked_at = monotonic()
        self.capture_stop = threading.Event()
        self.capture_thread = None
        self.preview_frame = None

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
                    "camera": dict(self.camera), "events": list(self.events)}

    def select(self, game):
        if game not in (None, "gyromite", "stack_up"):
            raise ValueError("Choose Gyromite, Stack-Up, or no game.")
        with self.lock:
            self.game = game
            self.stack, self.gyro = StackState(), GyroState()
            self.decoder.reset()
            self.event("session", f"{game or 'No game'} selected; virtual pieces reset.")
            return self.snapshot()

    def command(self, command, source="manual", pattern=None):
        with self.lock:
            if self.game is None:
                raise ValueError("Select a game before sending commands.")
            if self.game == "gyromite" and any(self.gyro.assisted_until.values()) and command != "READY":
                raise ValueError("Release Gate Assist before moving R.O.B. with commands.")
            if command == "READY":
                self.event("ready", "R.O.B. ready-light signal received; no movement.", command)
            else:
                normalized = command.removesuffix("_GYRO").removesuffix("_STACK")
                if source == "camera" and command in ("UP_GYRO", "DOWN_GYRO") and self.game != "gyromite":
                    raise ValueError("Optical command does not belong to the selected game.")
                if source == "camera" and command in ("UP_STACK", "DOWN_STACK") and self.game != "stack_up":
                    raise ValueError("Optical command does not belong to the selected game.")
                model = self.stack if self.game == "stack_up" else self.gyro
                error = model.apply(normalized)
                if error:
                    self.event("blocked", f"{normalized} blocked: {error}", normalized)
                else:
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
            self.camera["brightness"] = round(brightness, 3)
            self.camera["last_frame"] = time()
            detection = self.decoder.feed(timestamp, brightness, self.game)
            if detection:
                self.event("decoded", f"Flash decoded: {detection.command} ({detection.pattern}).", detection.command)
                self.command(detection.command, "camera", detection.pattern)
            return detection

    def start_camera(self, index=0, roi=None):
        if self.capture_thread and self.capture_thread.is_alive():
            return self.snapshot()
        with self.lock:
            if self.game == "gyromite" and any(self.gyro.assisted_until.values()):
                for color in ("red", "blue"):
                    self.gyro.assist_gate(color, False)
                self.event("assist", "Gate Assist released before camera capture.")
        if roi is not None and (not isinstance(roi, list) or len(roi) != 4 or
                                any(not isinstance(value, (int, float)) for value in roi)):
            raise ValueError("ROI must contain four normalized numbers.")
        if roi is not None and (min(roi) < 0 or max(roi) > 1 or roi[2] <= 0 or roi[3] <= 0 or
                                roi[0] + roi[2] > 1 or roi[1] + roi[3] > 1):
            raise ValueError("ROI must fit inside the camera frame.")
        devices = capture_devices()
        if os.name == "posix" and Path("/sys/class/video4linux").exists():
            if not devices:
                with self.lock:
                    self.camera.update(state="fault", message="No camera capture device is attached. Video codec nodes are not cameras.")
                    self.event("fault", self.camera["message"])
                raise RuntimeError(self.camera["message"])
            if index == 0:
                index = devices[0]["path"]
        try:
            import cv2
        except ImportError as exc:
            with self.lock:
                self.camera.update(state="fault", message="OpenCV is not installed on this controller.")
                self.event("fault", self.camera["message"])
            raise RuntimeError("OpenCV is needed for camera capture. Install opencv-python on the controller.") from exc
        capture = cv2.VideoCapture(index)
        if not capture.isOpened():
            capture.release()
            with self.lock:
                self.camera.update(state="fault", message=f"Camera {index} could not be opened.")
                self.event("fault", self.camera["message"])
            raise RuntimeError(f"Camera {index} could not be opened.")
        capture.set(cv2.CAP_PROP_FPS, 120)
        self.capture_stop.clear()
        with self.lock:
            self.decoder.reset()
            self.camera.update(state="capturing", message="Measuring frame timing; aim at the flash area.", fps=0)
            self.event("camera", f"Camera {index} opened.")

        def capture_loop():
            previous = None
            fps = 0.0
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
                    # Green exceeds red on the NES command frame. Measure both
                    # brightness and green dominance to reject neutral room light.
                    b, g, r, _ = cv2.mean(crop)
                    brightness = max(0.0, min(1.0, ((g - max(r, b) * .45) / 255)))
                    if previous is not None:
                        measured = 1 / max(timestamp - previous, .0001)
                        fps = measured if fps == 0 else fps * .9 + measured * .1
                    previous = timestamp
                    with self.lock:
                        self.camera["fps"] = round(fps, 1)
                        self.camera["message"] = "Frame rate below 120 fps; optical commands may be missed." if fps and fps < 110 else "Watching for complete optical commands."
                    self.sample(timestamp, brightness)
                    if timestamp - last_preview >= .5:
                        preview = frame.copy()
                        x0, y0 = int(x * width), int(y * height)
                        x1, y1 = int((x + w) * width), int((y + h) * height)
                        cv2.rectangle(preview, (x0, y0), (x1, y1), (84, 225, 117), 2)
                        ok_jpeg, encoded = cv2.imencode(".jpg", preview, [cv2.IMWRITE_JPEG_QUALITY, 68])
                        if ok_jpeg:
                            with self.lock:
                                self.preview_frame = encoded.tobytes()
                        last_preview = timestamp
            except Exception as exc:
                with self.lock:
                    self.preview_frame = None
                    self.camera.update(state="fault", message=str(exc))
                    self.event("fault", f"Camera fault: {exc}")
            finally:
                capture.release()
                with self.lock:
                    self.preview_frame = None
                    if self.camera["state"] != "fault":
                        self.camera.update(state="offline", message="Camera stopped.")
                        self.event("camera", "Camera stopped.")

        self.capture_thread = threading.Thread(target=capture_loop, daemon=True)
        self.capture_thread.start()
        return self.snapshot()

    def stop_camera(self):
        self.capture_stop.set()
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        self.decoder.reset()
        return self.snapshot()


def serve(host="127.0.0.1", port=8766, token=None, camera_index=None, camera_roi=None):
    if host not in ("127.0.0.1", "localhost", "::1") and not token:
        raise ValueError("A bearer token is required when serving over the network.")
    controller = Controller()
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

        def do_GET(self):
            path = urlsplit(self.path).path
            if path.startswith("/api/"):
                if not self.authorized():
                    return
                if path == "/api/state":
                    return self.respond(200, controller.snapshot())
                if path == "/api/camera/frame":
                    with controller.lock:
                        frame = controller.preview_frame
                    if frame is None:
                        self.send_response(204)
                        self.end_headers()
                        return
                    self.send_response(200)
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Length", str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    return
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
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if not self.authorized():
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size > 4096:
                    raise ValueError("Request too large.")
                data = json.loads(self.rfile.read(size) or b"{}")
                path = urlsplit(self.path).path
                if path == "/api/game":
                    result = controller.select(data.get("game"))
                elif path == "/api/launch":
                    game = identify(data.get("system", ""), data.get("rom", ""), load_registry()) if data.get("event") == "start" else None
                    result = controller.select(game)
                elif path == "/api/command":
                    result = controller.command(data["command"])
                elif path == "/api/gate-assist":
                    result = controller.gate_assist(data["color"], data["pressed"])
                elif path == "/api/camera/start":
                    result = controller.start_camera(int(data.get("index", 0)), data.get("roi"))
                elif path == "/api/camera/stop":
                    result = controller.stop_camera()
                else:
                    return self.respond(404, {"error": "Unknown endpoint."})
                self.respond(200, result)
            except (ValueError, KeyError, TypeError, RuntimeError) as exc:
                self.respond(400, {"error": str(exc)})

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"R.O.B. Vision controller: http://{host}:{port}/dashboard/", flush=True)
    try:
        server.serve_forever()
    finally:
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
    roi = [float(value) for value in args.camera_roi.split(",")] if args.camera_roi else None
    serve(args.host, args.port, args.token, args.camera_index, roi)
