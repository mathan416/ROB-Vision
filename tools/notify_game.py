#!/usr/bin/env python3
"""Optional RetroPie hook helper. Never blocks game launch on a controller failure."""

import argparse
import json
import os
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
    args = parser.parse_args()
    payload = event(args.action, args.system, args.rom, load_registry() if args.action == "start" else {})
    request = Request(args.url.rstrip("/") + "/api/launch", data=json.dumps(payload).encode(),
                      headers={"Content-Type": "application/json", "Authorization": "Bearer " + os.environ.get("ROB_VISION_TOKEN", "")}, method="POST")
    try:
        with urlopen(request, timeout=.35) as response:
            response.read()
    except Exception as exc:
        print(f"R.O.B. Vision launch notification unavailable: {exc}", file=__import__("sys").stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
