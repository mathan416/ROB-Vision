#!/usr/bin/env python3
"""Mirror R.O.B. Vision's Gyromite pads to a fail-safe Linux virtual gamepad.

Run as root on RetroPie so /dev/uinput is available. No third-party packages.
"""

import argparse
import fcntl
import ipaddress
import json
import os
import signal
import socket
import struct
import sys
import time
from collections import deque
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from identify_game import identify, load_registry
from tools.game_registry import RegistryStore, router_store_for, serve
from tools.retropie_frame_hook import BATOCERA_CONFIG, BATOCERA_PROXY_CORES, FrameHookServer


def ioctl_write(number, size):
    return (1 << 30) | (size << 16) | (ord("U") << 8) | number


UI_DEV_CREATE = (ord("U") << 8) | 1
UI_DEV_DESTROY = (ord("U") << 8) | 2
UI_DEV_SETUP = ioctl_write(3, 92)
UI_SET_EVBIT = ioctl_write(100, 4)
UI_SET_KEYBIT = ioctl_write(101, 4)
EV_SYN, EV_KEY, SYN_REPORT = 0, 1, 0
BTN_SOUTH, BTN_EAST = 304, 305


class VirtualPad:
    def __init__(self):
        self.fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
        self.pressed = {BTN_SOUTH: False, BTN_EAST: False}
        self.created = False
        try:
            fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_KEY)
            for code in self.pressed:
                fcntl.ioctl(self.fd, UI_SET_KEYBIT, code)
            name = b"R.O.B. Vision Controller 2"
            setup = struct.pack("=HHHH80sI", 0x06, 0x1209, 0x0001, 0x0001, name, 0)
            fcntl.ioctl(self.fd, UI_DEV_SETUP, setup)
            fcntl.ioctl(self.fd, UI_DEV_CREATE)
            self.created = True
        except Exception:
            os.close(self.fd)
            raise

    def event(self, kind, code, value):
        os.write(self.fd, struct.pack("@llHHi", 0, 0, kind, code, value))

    def update(self, red, blue, swap=False):
        desired = {BTN_SOUTH: bool(blue if swap else red),
                   BTN_EAST: bool(red if swap else blue)}
        changed = False
        for code, value in desired.items():
            if value != self.pressed[code]:
                self.event(EV_KEY, code, int(value))
                self.pressed[code] = value
                changed = True
        if changed:
            self.event(EV_SYN, SYN_REPORT, 0)

    def close(self):
        try:
            self.update(False, False)
        finally:
            if self.created:
                fcntl.ioctl(self.fd, UI_DEV_DESTROY)
            os.close(self.fd)


def controller_route_address(url):
    """Find the console's LAN address on the route used for this UNO Q."""
    try:
        host = urlsplit(url).hostname
        if not host:
            return ""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
            connection.connect((host, 9))
            address = connection.getsockname()[0]
        parsed = ipaddress.IPv4Address(address)
        return address if parsed.is_private and not (parsed.is_loopback or parsed.is_link_local) else ""
    except (OSError, ValueError):
        return ""


def fetch_state(url, token, timeout, frame_hook_game=None, test_signal_game=None,
                platform="retropie", console_id="", console_address=""):
    headers = {"Authorization": "Bearer " + token, "X-ROB-Receiver": platform}
    if console_id:
        headers["X-ROB-Console-ID"] = console_id
    if console_address:
        headers["X-ROB-Console-Address"] = console_address
    if frame_hook_game in ("gyromite", "stack_up"):
        headers["X-ROB-Frame-Hook"] = frame_hook_game
    if test_signal_game == frame_hook_game and test_signal_game in ("gyromite", "stack_up"):
        headers["X-ROB-Test-Signal"] = test_signal_game
    request = Request(url.rstrip("/") + "/api/state",
                      headers=headers)
    with urlopen(request, timeout=timeout) as response:
        state = json.load(response)
    if not isinstance(state, dict):
        raise ValueError("Controller response is not an object")
    if state.get("schema") != 1:
        raise ValueError("Unsupported controller state schema")
    return state


def pads_from_state(state):
    if state.get("game") != "gyromite":
        return False, False
    pads = (state.get("robot") or {}).get("pads") or {}
    if not isinstance(pads.get("red"), bool) or not isinstance(pads.get("blue"), bool):
        raise ValueError("Gyromite pad state is missing or invalid")
    return pads["red"], pads["blue"]


def source_selected(state, platform, console_id=""):
    link = state.get("link") or {}
    active = next((item.get("id") for item in link.get("consoles", []) if item.get("active")), None)
    if active:
        return active == (console_id or "legacy:" + platform)
    return str(link.get("receiver") or "").casefold() in ("", platform)


def running_game(registry, proc_root=Path("/proc"), platform="retropie"):
    """Read the active RetroArch command, never a background test run."""
    for pid in os.listdir(proc_root):
        if not pid.isdigit():
            continue
        try:
            arguments = (proc_root / pid / "cmdline").read_bytes().split(b"\0")
        except (OSError, PermissionError):
            continue
        if not arguments or Path(os.fsdecode(arguments[0])).name != "retroarch":
            continue
        if platform == "retropie" and b"/dev/shm/retroarch.cfg" not in arguments:
            continue
        if platform == "batocera" and BATOCERA_CONFIG not in arguments:
            continue
        if platform == "batocera" and not any(arguments[i] == b"-L" and
                arguments[i + 1] in BATOCERA_PROXY_CORES
                for i in range(len(arguments) - 1)):
            continue
        for argument in arguments[1:]:
            rom = os.fsdecode(argument)
            root = "/userdata/roms/" if platform == "batocera" else "/home/pi/retropie/roms/"
            if not rom.casefold().startswith(root):
                continue
            system = Path(rom).parent.name
            game = identify(system, rom, registry)
            if game:
                return game, system, rom
    return None


def sync_game(url, token, system, rom, timeout, platform="retropie", console_id="", game=None):
    """Replay a known launch after the UNO Q restarts mid-game."""
    payload = json.dumps({"event": "start", "system": system, "rom": Path(rom).name,
                          **({"game": game} if game else {})}).encode()
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token,
               "X-ROB-Receiver": platform}
    if console_id:
        headers["X-ROB-Console-ID"] = console_id
    request = Request(url.rstrip("/") + "/api/launch", data=payload, headers=headers, method="POST")
    with urlopen(request, timeout=timeout) as response:
        response.read()


def send_frame_command(url, token, item, timeout, platform="retropie", console_id=""):
    payload = json.dumps({key: item[key] for key in
                          ("game", "pattern", "sender_pid", "frame_index")}).encode()
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token,
               "X-ROB-Receiver": platform}
    if console_id:
        headers["X-ROB-Console-ID"] = console_id
    request = Request(url.rstrip("/") + "/api/emulator/command", data=payload,
                      headers=headers,
                      method="POST")
    with urlopen(request, timeout=timeout) as response:
        response.read()


def queued_frame_action(item, active_game, state, platform, console_id, now):
    """Keep the first flash while Router selects the game's controller."""
    if now - item["created_at"] > 3.0 or (active_game and active_game[0] != item["game"]):
        return "drop"
    if not active_game:
        return "wait"
    if not source_selected(state, platform, console_id):
        return "drop"
    return "send"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.environ.get("ROB_VISION_URL", "http://arduiain.local:8766"))
    parser.add_argument("--token-file", type=Path,
                        default=Path(os.environ.get("ROB_VISION_TOKEN_FILE", "/home/pi/.config/rob-vision/token")))
    parser.add_argument("--interval", type=float, default=0.05)
    parser.add_argument("--timeout", type=float, default=0.25)
    parser.add_argument("--stale-after", type=float, default=0.75)
    parser.add_argument("--swap-buttons", action="store_true")
    parser.add_argument("--platform", choices=("retropie", "batocera"), default="retropie")
    args = parser.parse_args()
    if args.interval <= 0 or args.timeout <= 0 or args.stale_after <= args.timeout:
        parser.error("interval/timeout must be positive and stale-after must exceed timeout")
    token = args.token_file.read_text().strip()
    if not token:
        parser.error("Controller token file is empty")
    console_id_path = args.token_file.with_name("console-id")
    console_id = console_id_path.read_text().strip() if console_id_path.exists() else ""
    running = True

    def stop(_signal, _frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    pad = VirtualPad()
    registry_path = Path(__file__).resolve().parents[1] / "config/games.json"
    registry = load_registry(registry_path)
    registry_mtime = registry_path.stat().st_mtime_ns
    hook = FrameHookServer(registry, platform=args.platform)
    hook.start()
    try:
        games_server = serve(RegistryStore(registry_path, args.platform), args.token_file,
                             router_store=router_store_for(args.platform))
    except OSError as exc:
        print(f"R.O.B. Vision registry editor unavailable: {exc}", file=sys.stderr)
        games_server = None
    desired = (False, False)
    last_good = 0.0
    active_game = None
    next_process_check = 0.0
    next_address_check = 0.0
    console_address = ""
    next_registry_check = 0.0
    next_sync = 0.0
    pending_frames = deque()
    state = {}
    try:
        while running:
            started = time.monotonic()
            if started >= next_address_check:
                console_address = controller_route_address(args.url)
                next_address_check = started + 15.0
            if started >= next_registry_check:
                next_registry_check = started + 1.0
                try:
                    modified = registry_path.stat().st_mtime_ns
                    if modified != registry_mtime:
                        registry = load_registry(registry_path)
                        hook.registry = registry
                        registry_mtime = modified
                except (OSError, ValueError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
                    print(f"R.O.B. Vision registry reload failed: {exc}", file=sys.stderr)
            if started >= next_process_check:
                active_game = running_game(registry, platform=args.platform)
                next_process_check = started + .25
            try:
                hook_game = hook.recent_game()
                state = fetch_state(args.url, token, args.timeout,
                                    hook_game if active_game and hook_game == active_game[0] else None,
                                    hook.recent_test_game(), platform=args.platform, console_id=console_id,
                                    console_address=console_address)
                selected_here = source_selected(state, args.platform, console_id)
                if not selected_here:
                    desired = (False, False)
                    hook_game = None
                else:
                    desired = pads_from_state(state)
                last_good = time.monotonic()
                if active_game and (selected_here or state.get("game") is None) and state.get("game") != active_game[0] and started >= next_sync:
                    next_sync = started + 2.0
                    try:
                        sync_game(args.url, token, active_game[1], active_game[2], args.timeout,
                                  args.platform, console_id, game=active_game[0])
                    except (OSError, ValueError):
                        pass
            except (OSError, ValueError, json.JSONDecodeError):
                if time.monotonic() - last_good > args.stale_after:
                    desired = (False, False)
            if not active_game or active_game[0] != "gyromite":
                desired = (False, False)
            pending_frames.extend(hook.take_pending())
            while pending_frames:
                item = pending_frames[0]
                action = queued_frame_action(item, active_game, state, args.platform,
                                             console_id, time.monotonic())
                if action == "drop":
                    pending_frames.popleft()
                    continue
                if action == "wait":
                    break
                if time.monotonic() < item.get("next_try", 0.0):
                    break
                try:
                    send_frame_command(args.url, token, item, args.timeout, args.platform, console_id)
                    pending_frames.popleft()
                except (OSError, ValueError):
                    item["next_try"] = time.monotonic() + .2
                    break
            pad.update(*desired, swap=args.swap_buttons)
            if running:
                time.sleep(max(0, args.interval - (time.monotonic() - started)))
    finally:
        if games_server is not None:
            games_server.shutdown()
            games_server.server_close()
        hook.stop()
        pad.close()


if __name__ == "__main__":
    main()
