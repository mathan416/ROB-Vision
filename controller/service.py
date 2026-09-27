"""Local HTTP controller for R.O.B. Vision's RetroPie game-frame link."""

import argparse
import json
import os
import hashlib
import http.client
import ipaddress
import re
import socket
import ssl
import threading
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from time import monotonic, time
from urllib.parse import urlsplit
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

from .model import GyroState, StackState
from .optical import ALLOWED, PATTERNS
from .pairings import PairingStore, PLATFORMS
from .resolver import resolve_ipv4
from tools.identify_game import SUPPORTED_EXTENSIONS, SUPPORTED_GAMES, SUPPORTED_SYSTEMS, identify, load_registry

ROOT = Path(__file__).resolve().parents[1]
READY_LIGHT_SECONDS = 1.0
MIME = {".html": "text/html", ".js": "text/javascript", ".css": "text/css",
        ".svg": "image/svg+xml", ".pdf": "application/pdf", ".png": "image/png",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".ttf": "font/ttf"}


def router_lease_active():
    """Older standalone installs have no lease; shared Router installs fail closed."""
    path = ROOT / "data/controller-router-lease.json"
    if not path.exists():
        return True
    try:
        record = json.loads(path.read_text())
        boot = Path("/proc/sys/kernel/random/boot_id")
        boot_id = boot.read_text().strip() if boot.exists() else "development"
        return (record.get("schema") == 1 and record.get("boot_id") == boot_id and
                record.get("active") is True and
                isinstance(record.get("until"), (int, float)) and monotonic() < record["until"])
    except (OSError, ValueError, TypeError):
        return False


def game_from_launch(data):
    """Accept a known game asserted by a paired console's validated registry."""
    if data.get("event") != "start":
        return None
    system, rom, reported = data.get("system"), data.get("rom"), data.get("game")
    if (isinstance(system, str) and system.casefold() in SUPPORTED_SYSTEMS
            and isinstance(rom, str) and rom == Path(rom).name
            and Path(rom).suffix.casefold() in SUPPORTED_EXTENSIONS
            and isinstance(reported, str) and reported in SUPPORTED_GAMES):
        return reported
    if isinstance(system, str) and isinstance(rom, str):
        return identify(system, rom, load_registry())
    return None


def console_registry(pairings, console_id, action, document=None, revision=None):
    """Proxy a bounded registry edit to one paired console without exposing its token."""
    with pairings.lock:
        record = dict(pairings.records.get(console_id, {})) if isinstance(console_id, str) else {}
        observed = (pairings.last_address.get(console_id)
                    if monotonic() - pairings.last_seen.get(console_id, 0) < 10 else None)
    if not record:
        raise ValueError("Choose a paired console from the list.")
    host = record["host"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]{0,252}", host):
        raise ValueError("The paired console address is invalid.")
    if action not in ("read", "validate", "save", "restore"):
        raise ValueError("Unknown registry action.")
    payload = {"action": action, "revision": revision}
    if action in ("validate", "save"):
        payload["document"] = document
    body = json.dumps(payload).encode()
    if len(body) > 70000:
        raise ValueError("Game registry exceeds 64 KiB.")
    addresses = [observed] if observed else []
    try:
        resolved = resolve_ipv4(host)
        if resolved not in addresses:
            addresses.append(resolved)
    except OSError:
        if not addresses:
            raise ValueError("The paired console name cannot be resolved from this UNO Q.") from None
    opener = build_opener(ProxyHandler({}))
    answer = None
    for address in addresses:
        if not ipaddress.ip_address(address).is_private:
            continue
        request = Request(f"http://{address}:8769/registry", data=body, method="POST",
                          headers={"Authorization": "Bearer " + record["token"],
                                   "Content-Type": "application/json"})
        try:
            with opener.open(request, timeout=3) as response:
                answer = response.read(70001)
            break
        except HTTPError as exc:
            try:
                raise ValueError(json.loads(exc.read(4096)).get("error", "Console rejected the registry change.")) from exc
            except (json.JSONDecodeError, AttributeError):
                raise ValueError("Console rejected the registry change.") from exc
        except OSError:
            continue
    if answer is None:
        raise ValueError("The paired console's registry editor is unavailable. Update its R.O.B. Vision receiver, then check the link.")
    if len(answer) > 70000:
        raise ValueError("Console registry response is too large.")
    return json.loads(answer)


def console_router(pairings, console_id, action, config=None, revision=None, watch_ms=0):
    """Proxy Router controls through a saved console pairing."""
    if action not in ("read", "inventory", "check", "save", "rollback"):
        raise ValueError("Unknown Controller Router action.")
    with pairings.lock:
        record = dict(pairings.records.get(console_id, {})) if isinstance(console_id, str) else {}
        observed = (pairings.last_address.get(console_id)
                    if monotonic() - pairings.last_seen.get(console_id, 0) < 10 else None)
    if not record:
        raise ValueError("Choose a paired console from the list.")
    host = record["host"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]{0,252}", host):
        raise ValueError("The paired console address is invalid.")
    payload = {"action": action, "revision": revision}
    if action == "save":
        payload["config"] = config
    if action == "check":
        payload["watch_ms"] = min(10000, max(0, int(watch_ms)))
    body = json.dumps(payload).encode()
    if len(body) > 262144:
        raise ValueError("Controller assignments are too large.")
    addresses = [observed] if observed else []
    try:
        resolved = resolve_ipv4(host)
        if resolved not in addresses:
            addresses.append(resolved)
    except OSError:
        if not addresses:
            raise ValueError("The paired console name cannot be resolved from this UNO Q.") from None
    opener = build_opener(ProxyHandler({}))
    for address in addresses:
        if not ipaddress.ip_address(address).is_private:
            continue
        request = Request(f"http://{address}:8769/router", data=body, method="POST",
                          headers={"Authorization": "Bearer " + record["token"],
                                   "Content-Type": "application/json"})
        try:
            with opener.open(request, timeout=14 if action == "check" else 4) as response:
                answer = response.read(262145)
            if len(answer) > 262144:
                raise ValueError("Controller Router response is too large.")
            return json.loads(answer)
        except HTTPError as exc:
            try:
                raise ValueError(json.loads(exc.read(4096)).get("error", "Console rejected Controller Router request.")) from exc
            except (json.JSONDecodeError, AttributeError):
                raise ValueError("Console rejected Controller Router request.") from exc
        except OSError:
            continue
    raise ValueError("The paired console's Controller Router is unavailable. Update its receiver and check the link.")
def controller_url_from_host(host):
    """Use the address the browser used to reach this UNO Q for its console link."""
    if not isinstance(host, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.:-]{0,258}", host):
        raise ValueError("Open Setup using this UNO Q's LAN hostname or IP address before pairing.")
    parsed = urlsplit("http://" + host)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid UNO Q address for pairing.") from exc
    if not parsed.hostname or parsed.hostname.lower() == "localhost" or (port is not None and not 1 <= port <= 65535):
        raise ValueError("Open Setup using this UNO Q's LAN hostname or IP address before pairing.")
    try:
        address = ipaddress.ip_address(parsed.hostname)
    except ValueError:
        pass
    else:
        if not address.is_private or address.is_loopback or address.is_link_local:
            raise ValueError("Pairing requires this UNO Q's private LAN address.")
    return "http://" + parsed.hostname + ":8766"


def pair_retropie(host, code, fingerprint, token, console_id, port=8768, controller_url=None):
    """Send the controller token only after checking the console's TLS fingerprint."""
    if not isinstance(host, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]{0,252}", host):
        raise ValueError("Enter a console hostname or local IP address.")
    if not isinstance(code, str) or not re.fullmatch(r"[0-9]{6}", code):
        raise ValueError("Enter the six-digit code shown on the console.")
    fingerprint = re.sub(r"[^0-9a-fA-F]", "", str(fingerprint)).lower()
    if len(fingerprint) != 64:
        raise ValueError("Enter the console's 64-character SHA-256 fingerprint.")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("Invalid pairing port.")
    if not token:
        raise ValueError("Configure a controller token before pairing.")
    addresses = ([resolve_ipv4(host)] if host.lower().endswith(".local") else
                 [item[4][0] for item in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)])
    if not addresses or any(not ipaddress.ip_address(address).is_private for address in addresses):
        raise ValueError("Pairing is available only on a private network.")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    connection = http.client.HTTPSConnection(addresses[0], port, context=context, timeout=8)
    try:
        connection.connect()
        actual = hashlib.sha256(connection.sock.getpeercert(binary_form=True)).hexdigest()
        if actual != fingerprint:
            raise ValueError("Console fingerprint does not match. Pairing stopped before sending the token.")
        body = json.dumps({"code": code, "token": token, "console_id": console_id,
                           "controller_url": controller_url}).encode()
        connection.request("POST", "/pair", body=body, headers={"Content-Type": "application/json"})
        response = connection.getresponse()
        result = json.load(response)
        if response.status != 200 or result.get("paired") is not True:
            raise ValueError(result.get("error", "Console did not confirm pairing."))
        platform = result.get("platform")
        if platform not in PLATFORMS or result.get("console_id") != console_id:
            raise ValueError("Update the console receiver before pairing it again.")
        return {"paired": True, "host": host, "platform": platform, "id": console_id}
    finally:
        connection.close()


class Controller:
    def __init__(self, pairings=None):
        self.lock = threading.RLock()
        self.game = None
        self.stack = StackState()
        self.gyro = GyroState()
        self.sequence = 0
        self.events = []
        self.receiver_last_seen = 0.0
        self.receiver_name = None
        self.active_receiver = None
        self.active_console_id = None
        self.pairings = pairings
        self.frame_hook_last_seen = 0.0
        self.frame_hook_game = None
        self.frame_hook_commands = deque(maxlen=128)
        self.test_ready_at = 0.0
        self.test_flash_seen_at = 0.0

    def event(self, kind, message, command=None):
        self.sequence += 1
        self.events.append({"seq": self.sequence, "time": time(), "kind": kind, "message": message, "command": command})
        self.events = self.events[-30:]

    def snapshot(self):
        with self.lock:
            if self.game == "gyromite":
                for color in self.gyro.expire_assist():
                    self.event("assist", f"{color.title()} Gate Assist timed out; button released.")
            active = router_lease_active()
            robot = self.stack.snapshot() if self.game == "stack_up" else self.gyro.snapshot() if self.game == "gyromite" else None
            if not active and self.game == "gyromite" and robot:
                robot["pads"] = {"red": False, "blue": False}
            return {"schema": 1, "sequence": self.sequence, "game": self.game,
                    "live_game_active": bool(self.game and self.active_console_id),
                    "controller_selected": active,
                    "robot": robot,
                    "events": list(self.events),
                    "link": {"online": monotonic() - self.receiver_last_seen < 3.0,
                             "receiver": self.receiver_name,
                             "consoles": self.pairings.list_public(self.active_console_id) if self.pairings else []},
                    "input": {"frame_hook": self.frame_hook_active()},
                    "test": {"ready": self.test_ready_at > 0 and
                             monotonic() - self.test_ready_at < READY_LIGHT_SECONDS and self.frame_hook_active(),
                             "ready_at": self.test_ready_at,
                             "flash_active": self.frame_hook_active() and
                             monotonic() - self.test_flash_seen_at < .25}}

    def frame_hook_active(self):
        return self.frame_hook_game == self.game and monotonic() - self.frame_hook_last_seen < 1.0

    def receiver_seen(self, name, frame_hook_game=None, test_signal_game=None, console_id=None):
        with self.lock:
            if self.active_console_id and console_id != self.active_console_id:
                return
            if self.active_receiver and name.casefold() != self.active_receiver:
                return
            if (not self.active_receiver and self.receiver_name and name != self.receiver_name
                    and monotonic() - self.receiver_last_seen < 3.0):
                return
            self.receiver_name = name[:64]
            self.receiver_last_seen = monotonic()
            if frame_hook_game == self.game and frame_hook_game in ("gyromite", "stack_up"):
                self.frame_hook_game = frame_hook_game
                self.frame_hook_last_seen = monotonic()
                if test_signal_game == self.game:
                    now = monotonic()
                    if now - self.test_flash_seen_at > .5:
                        self.event("test", "Game-frame Test signal detected; R.O.B. light blinking.")
                    self.test_flash_seen_at = now

    def emulator_command(self, game, pattern, sender_pid, frame_index, receiver="retropie", console_id=None):
        with self.lock:
            if not router_lease_active():
                raise ValueError("Select R.O.B. Vision in Controller Router before playing.")
            if self.active_console_id and console_id != self.active_console_id:
                raise ValueError("Frame command came from another console.")
            if self.active_receiver and receiver != self.active_receiver:
                raise ValueError("Frame command came from another console.")
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

    def select(self, game):
        if game not in (None, "gyromite", "stack_up"):
            raise ValueError("Choose Gyromite, Stack-Up, or no game.")
        with self.lock:
            self.game = game
            self.stack, self.gyro = StackState(), GyroState()
            self.frame_hook_game = None
            self.frame_hook_last_seen = 0.0
            self.frame_hook_commands.clear()
            self.test_ready_at = 0.0
            self.test_flash_seen_at = 0.0
            self.event("session", f"{game or 'No game'} selected; virtual pieces reset.")
            return self.snapshot()

    def command(self, command, source="manual"):
        with self.lock:
            if not router_lease_active() and source != "demo":
                raise ValueError("Select R.O.B. Vision in Controller Router before playing.")
            if self.game is None:
                raise ValueError("Select a game before sending commands.")
            if self.game == "gyromite" and any(self.gyro.assisted_until.values()) and command != "READY":
                raise ValueError("Release Gate Assist before moving R.O.B. with commands.")
            if command == "READY":
                if source == "emulator":
                    self.test_ready_at = monotonic()
                self.event("ready", "R.O.B. ready-light signal received; no movement.", command)
            else:
                normalized = command.removesuffix("_GYRO").removesuffix("_STACK")
                if source == "emulator" and command in ("UP_GYRO", "DOWN_GYRO") and self.game != "gyromite":
                    raise ValueError("Optical command does not belong to the selected game.")
                if source == "emulator" and command in ("UP_STACK", "DOWN_STACK") and self.game != "stack_up":
                    raise ValueError("Optical command does not belong to the selected game.")
                self.test_ready_at = self.test_flash_seen_at = 0.0
                model = self.stack if self.game == "stack_up" else self.gyro
                error = model.apply(normalized)
                if error:
                    self.event("blocked", f"{normalized} blocked: {error}", normalized)
                else:
                    self.event("action", f"{source.title()} command: {normalized}.", normalized)
            return self.snapshot()

    def gate_assist(self, color, pressed):
        with self.lock:
            if not router_lease_active():
                raise ValueError("Select R.O.B. Vision in Controller Router before using gates.")
            if self.game != "gyromite":
                raise ValueError("Gate Assist is only available in Gyromite.")
            if color == "all" and pressed is False:
                for gate in ("red", "blue"):
                    self.gyro.assist_gate(gate, False)
                self.event("assist", "Both Gate Assist buttons released.")
            else:
                self.gyro.assist_gate(color, pressed)
                self.event("assist", f"{color.title()} Gate Assist {'pressed' if pressed else 'released'}.")
            return self.snapshot()


def serve(host="127.0.0.1", port=8766, token=None, matrix=None, pairing_path=None):
    if host not in ("127.0.0.1", "localhost", "::1") and not token:
        raise ValueError("A bearer token is required when serving over the network.")
    pairings = PairingStore(pairing_path or ROOT / "data/paired-consoles.json", token or "")
    controller = Controller(pairings)
    matrix_stop = threading.Event()
    matrix_thread = None
    if matrix is not None:
        matrix_thread = threading.Thread(target=matrix.run, args=(controller.snapshot, matrix_stop), daemon=True)
        matrix_thread.start()

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
            self.console_identity = (pairings.verify(self.headers) if token else
                                     {"id": "legacy:retropie", "platform": "retropie", "host": ""})
            if self.console_identity is None:
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
                    identity = pairings.verify(self.headers) if token else None
                    if identity:
                        receiver = identity["platform"]
                        pairings.seen(identity["id"],
                                      self.headers.get("X-ROB-Console-Address") or self.client_address[0])
                        controller.receiver_seen("RetroPie" if receiver == "retropie" else "Batocera",
                                                 self.headers.get("X-ROB-Frame-Hook"),
                                                 self.headers.get("X-ROB-Test-Signal"), identity["id"])
                    return self.respond(200, controller.snapshot())
                if path == "/api/matrix/state":
                    return self.respond(200, matrix.status() if matrix is not None else
                                        {"available": False, "bridge_ok": False, "mode": None})
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
                if size < 0 or size > (70000 if path == "/api/games" else 4096):
                    raise ValueError("Request too large.")
                data = json.loads(self.rfile.read(size) or b"{}")
                if path == "/api/game":
                    result = controller.select(data.get("game"))
                    with controller.lock:
                        controller.active_receiver = None
                        controller.active_console_id = None
                elif path == "/api/launch":
                    receiver = self.console_identity["platform"]
                    console_id = self.console_identity["id"]
                    if data.get("event") == "end" and controller.active_console_id not in (None, console_id):
                        return self.respond(200, controller.snapshot())
                    game = game_from_launch(data)
                    result = controller.select(game)
                    with controller.lock:
                        controller.active_receiver = receiver if game else None
                        controller.active_console_id = console_id if game else None
                        controller.receiver_name = "RetroPie" if receiver == "retropie" else "Batocera"
                        controller.receiver_last_seen = 0.0
                elif path == "/api/command":
                    result = controller.command(data["command"])
                elif path == "/api/emulator/command":
                    result = controller.emulator_command(data["game"], data["pattern"],
                                                         data["sender_pid"], data["frame_index"],
                                                         self.console_identity["platform"], self.console_identity["id"])
                elif path == "/api/gate-assist":
                    result = controller.gate_assist(data["color"], data["pressed"])
                elif path == "/api/pair":
                    if matrix is not None:
                        matrix.show_pairing()
                    try:
                        console_id, console_token = pairings.new_credentials()
                        result = pair_retropie(data["host"], data["code"], data["fingerprint"],
                                               console_token, console_id,
                                               controller_url=controller_url_from_host(
                                                   self.headers.get("X-Rob-Original-Host") or
                                                   self.headers.get("Host")))
                        pairings.add(console_id, console_token, result["platform"], result["host"])
                    finally:
                        if matrix is not None:
                            matrix.clear_pairing()
                elif path == "/api/consoles/remove":
                    console_id = data.get("id")
                    if not isinstance(console_id, str):
                        raise ValueError("Choose a console to remove.")
                    pairings.remove(console_id)
                    with controller.lock:
                        if controller.active_console_id == console_id:
                            controller.select(None)
                            controller.active_console_id = None
                            controller.active_receiver = None
                            controller.receiver_name = None
                            controller.receiver_last_seen = 0.0
                    result = controller.snapshot()
                elif path == "/api/games":
                    result = console_registry(pairings, data.get("console_id"), data.get("action"),
                                              data.get("document"), data.get("revision"))
                elif path == "/api/router":
                    result = console_router(pairings, data.get("console_id"), data.get("action"),
                                            data.get("config"), data.get("revision"),
                                            data.get("watch_ms", 0))
                elif path == "/api/matrix/pairing":
                    if not isinstance(data.get("active"), bool):
                        raise ValueError("Choose whether pairing is active.")
                    if matrix is not None:
                        matrix.show_pairing() if data["active"] else matrix.clear_pairing()
                    result = controller.snapshot()
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
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--token", default=os.environ.get("ROB_VISION_TOKEN"))
    args = parser.parse_args()
    serve(args.host, args.port, args.token)
