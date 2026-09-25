#!/usr/bin/env python3
"""Optional RetroPie hook helper. Never blocks game launch on a controller failure."""

import argparse
import json
import os
import sys
from time import sleep
from pathlib import Path
from urllib.request import Request, urlopen

from identify_game import event, load_registry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("start", "end"))
    parser.add_argument("system", nargs="?", default="")
    parser.add_argument("emulator", nargs="?", default="")
    parser.add_argument("rom", nargs="?", default="")
    parser.add_argument("command", nargs="?", default="")
    parser.add_argument("--url", default=os.environ.get("ROB_VISION_URL", "http://127.0.0.1:8766"))
    parser.add_argument("--token-file", type=Path, default=os.environ.get("ROB_VISION_TOKEN_FILE"))
    parser.add_argument("--timeout", type=float, default=0.8)
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args()
    if args.timeout <= 0 or args.attempts < 1:
        parser.error("timeout and attempts must be positive")
    try:
        token = os.environ.get("ROB_VISION_TOKEN", "")
        if not token and args.token_file:
            token = args.token_file.read_text().strip()
        if not token:
            raise ValueError("Controller token is not configured")
        payload = event(args.action, args.system, args.rom, load_registry() if args.action == "start" else {})
        request = Request(args.url.rstrip("/") + "/api/launch", data=json.dumps(payload).encode(),
                          headers={"Content-Type": "application/json", "Authorization": "Bearer " + token,
                                   "X-ROB-Receiver": os.environ.get("ROB_VISION_RECEIVER", "retropie")}, method="POST")
        for attempt in range(args.attempts):
            try:
                with urlopen(request, timeout=args.timeout) as response:
                    response.read()
                break
            except OSError:
                if attempt + 1 == args.attempts:
                    raise
                sleep(.1)
    except Exception as exc:
        print(f"R.O.B. Vision launch notification unavailable: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
