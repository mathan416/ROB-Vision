"""Arduino App Lab entry point for the R.O.B. Vision controller."""

from __future__ import annotations

import os
import signal
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = Path.home() / ".config/rob-vision/environment"
URL = "http://127.0.0.1:8766/api/state"


def controller_token() -> str:
    token = os.environ.get("ROB_VISION_TOKEN", "")
    if token:
        return token
    try:
        for line in ENV_FILE.read_text().splitlines():
            if line.startswith("ROB_VISION_TOKEN="):
                return line.partition("=")[2].strip().strip('"\'')
    except FileNotFoundError:
        pass
    return ""


def controller_is_ready(token: str) -> bool:
    request = urllib.request.Request(URL)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=1) as response:
            return response.status == 200
    except urllib.error.HTTPError as exc:
        return exc.code == 401
    except OSError:
        return False


def main() -> int:
    token = controller_token()
    if not token:
        raise RuntimeError("Set ROB_VISION_TOKEN in ~/.config/rob-vision/environment before starting R.O.B. Vision.")
    process: subprocess.Popen | None = None
    stopping = False

    def stop(_signum: int, _frame: object) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        while not stopping:
            if not controller_is_ready(token):
                if process is None or process.poll() is not None:
                    env = os.environ.copy()
                    env["ROB_VISION_TOKEN"] = token
                    env["PYTHONPATH"] = os.pathsep.join((str(ROOT / ".deps"), str(ROOT)))
                    process = subprocess.Popen(
                        ["/usr/bin/python3", "-m", "controller.service", "--host", "0.0.0.0", "--port", "8766"],
                        cwd=ROOT,
                        env=env,
                    )
            time.sleep(2)
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
