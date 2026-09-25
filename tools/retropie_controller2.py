#!/usr/bin/env python3
"""Mirror R.O.B. Vision's Gyromite pads to a fail-safe Linux virtual gamepad.

Run as root on RetroPie so /dev/uinput is available. No third-party packages.
"""

import argparse
import fcntl
import json
import os
import signal
import struct
import sys
import time
from collections import deque
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from identify_game import identify, load_registry
from tools.retropie_frame_hook import FrameHookServer


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


def fetch_state(url, token, timeout, frame_hook_game=None):
    headers = {"Authorization": "Bearer " + token, "X-ROB-Receiver": "retropie"}
    if frame_hook_game in ("gyromite", "stack_up"):
        headers["X-ROB-Frame-Hook"] = frame_hook_game
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


def running_game(registry, proc_root=Path("/proc")):
    """Read the active RetroPie RetroArch command, never a background test run."""
    for pid in os.listdir(proc_root):
        if not pid.isdigit():
            continue
        try:
            arguments = (proc_root / pid / "cmdline").read_bytes().split(b"\0")
        except (OSError, PermissionError):
            continue
        if not arguments or Path(os.fsdecode(arguments[0])).name != "retroarch":
            continue
        if b"/dev/shm/retroarch.cfg" not in arguments:
            continue
        for argument in arguments[1:]:
            rom = os.fsdecode(argument)
            if not rom.casefold().startswith("/home/pi/retropie/roms/"):
                continue
            system = Path(rom).parent.name
            game = identify(system, rom, registry)
            if game:
                return game, system, rom
    return None


def sync_game(url, token, system, rom, timeout):
    """Replay a known launch after the UNO Q restarts mid-game."""
    payload = json.dumps({"event": "start", "system": system, "rom": Path(rom).name}).encode()
    request = Request(url.rstrip("/") + "/api/launch", data=payload,
                      headers={"Content-Type": "application/json", "Authorization": "Bearer " + token}, method="POST")
    with urlopen(request, timeout=timeout) as response:
        response.read()


def send_frame_command(url, token, item, timeout):
    payload = json.dumps({key: item[key] for key in
                          ("game", "pattern", "sender_pid", "frame_index")}).encode()
    request = Request(url.rstrip("/") + "/api/emulator/command", data=payload,
                      headers={"Content-Type": "application/json", "Authorization": "Bearer " + token},
                      method="POST")
    with urlopen(request, timeout=timeout) as response:
        response.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://arduiain.local")
    parser.add_argument("--token-file", type=Path, default=Path("/home/pi/.config/rob-vision/token"))
    parser.add_argument("--interval", type=float, default=0.05)
    parser.add_argument("--timeout", type=float, default=0.25)
    parser.add_argument("--stale-after", type=float, default=0.75)
    parser.add_argument("--swap-buttons", action="store_true")
    args = parser.parse_args()
    if args.interval <= 0 or args.timeout <= 0 or args.stale_after <= args.timeout:
        parser.error("interval/timeout must be positive and stale-after must exceed timeout")
    token = args.token_file.read_text().strip()
    if not token:
        parser.error("Controller token file is empty")
    running = True

    def stop(_signal, _frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    pad = VirtualPad()
    registry = load_registry()
    hook = FrameHookServer(registry)
    hook.start()
    desired = (False, False)
    last_good = 0.0
    active_game = None
    next_process_check = 0.0
    next_sync = 0.0
    pending_frames = deque()
    try:
        while running:
            started = time.monotonic()
            if started >= next_process_check:
                active_game = running_game(registry)
                next_process_check = started + .25
            try:
                hook_game = hook.recent_game()
                state = fetch_state(args.url, token, args.timeout,
                                    hook_game if active_game and hook_game == active_game[0] else None)
                desired = pads_from_state(state)
                last_good = time.monotonic()
                if active_game and state.get("game") != active_game[0] and started >= next_sync:
                    next_sync = started + 2.0
                    try:
                        sync_game(args.url, token, active_game[1], active_game[2], args.timeout)
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
                if (not active_game or active_game[0] != item["game"] or
                        time.monotonic() - item["created_at"] > 1.0):
                    pending_frames.popleft()
                    continue
                if time.monotonic() < item.get("next_try", 0.0):
                    break
                try:
                    send_frame_command(args.url, token, item, args.timeout)
                    pending_frames.popleft()
                except (OSError, ValueError):
                    item["next_try"] = time.monotonic() + .2
                    break
            pad.update(*desired, swap=args.swap_buttons)
            if running:
                time.sleep(max(0, args.interval - (time.monotonic() - started)))
    finally:
        hook.stop()
        pad.close()


if __name__ == "__main__":
    main()
