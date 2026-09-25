"""Arduino App Lab entry point for the R.O.B. Vision controller."""

from __future__ import annotations

import os
import sys
import threading
import math
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
HOP_HEADERS = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
               "te", "trailers", "transfer-encoding", "upgrade", "host"}


def controller_token() -> str:
    token = os.environ.get("ROB_VISION_TOKEN", "")
    if token:
        return token
    token_file = ROOT / "data" / "controller-token"
    try:
        return token_file.read_text().strip()
    except FileNotFoundError:
        raise RuntimeError(f"Controller token missing from {token_file}") from None


def preferred_camera_roi() -> list[float] | None:
    """Load the saved sampling box without requiring camera capture at boot."""
    value = os.environ.get("ROB_VISION_CAMERA_ROI")
    if not value:
        try:
            value = (ROOT / "data" / "camera-roi").read_text().strip()
        except FileNotFoundError:
            return None
    try:
        roi = [float(part) for part in value.split(",")]
        if (len(roi) != 4 or any(not math.isfinite(part) or not 0 <= part <= 1 for part in roi)
                or roi[2] <= 0 or roi[3] <= 0
                or roi[0] + roi[2] > 1 or roi[1] + roi[3] > 1):
            raise ValueError
        return roi
    except ValueError:
        print("Ignoring invalid saved camera sampling box.", flush=True)
        return None


class DeviceNameHandler(BaseHTTPRequestHandler):
    """Forward the ordinary device URL to the same controller on port 8766."""

    def do_GET(self) -> None:
        self.forward()

    def do_POST(self) -> None:
        self.forward()

    def forward(self) -> None:
        if self.headers.get("Transfer-Encoding"):
            self.send_error(400, "Chunked requests are not supported")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > 4096:
                self.send_error(413, "Request too large")
                return
            body = self.rfile.read(length) if length else None
            headers = {key: value for key, value in self.headers.items()
                       if key.lower() not in HOP_HEADERS}
            headers["X-Rob-Original-Host"] = self.headers.get("Host", "")
            connection = HTTPConnection("127.0.0.1", 8766, timeout=10)
            try:
                connection.request(self.command, self.path, body=body, headers=headers)
                response = connection.getresponse()
                data = response.read()
                self.send_response(response.status)
                for key, value in response.getheaders():
                    if key.lower() not in HOP_HEADERS | {"content-length", "server", "date"}:
                        self.send_header(key, value)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            finally:
                connection.close()
        except (OSError, ValueError) as exc:
            self.send_error(502, f"Controller unavailable: {exc}")

    def log_message(self, format: str, *args: object) -> None:
        if args and "GET /api/state " in str(args[0]):
            return
        super().log_message(format, *args)


def main() -> None:
    from controller.service import serve
    from controller.matrix import MatrixDisplay, MatrixMode

    matrix = MatrixDisplay()
    matrix.send(MatrixMode.LOADING, force=True)
    token = controller_token()
    if not token:
        raise RuntimeError("Controller token is empty")
    gateway = ThreadingHTTPServer(("0.0.0.0", 80), DeviceNameHandler)
    thread = threading.Thread(target=gateway.serve_forever, daemon=True)
    thread.start()
    try:
        serve("0.0.0.0", 8766, token, None, preferred_camera_roi(), matrix=matrix)
    finally:
        gateway.shutdown()
        gateway.server_close()


if __name__ == "__main__":
    main()
