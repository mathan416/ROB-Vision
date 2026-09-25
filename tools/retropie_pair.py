#!/usr/bin/env python3
"""One-time, fingerprint-checked pairing for a prepared RetroPie receiver."""

import argparse
import hashlib
import json
import os
import secrets
import ssl
import subprocess
import tempfile
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def install_token(token, destination):
    if not isinstance(token, str) or not 16 <= len(token) <= 256 or any(c.isspace() for c in token):
        raise ValueError("Invalid controller token.")
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".pairing-" + secrets.token_hex(6))
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as file:
            file.write(token + "\n")
        os.replace(temporary, destination)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def main():
    parser = argparse.ArgumentParser(description="Pair this RetroPie with R.O.B. Vision.")
    parser.add_argument("--port", type=int, default=8768)
    parser.add_argument("--token-file", type=Path, default=Path.home() / ".config/rob-vision/token")
    args = parser.parse_args()
    code = f"{secrets.randbelow(1_000_000):06d}"
    expires = time.monotonic() + 300
    with tempfile.TemporaryDirectory(prefix="rob-vision-pair-") as directory:
        cert, key = Path(directory) / "cert.pem", Path(directory) / "key.pem"
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                        "-keyout", str(key), "-out", str(cert), "-subj", "/CN=rob-vision-pair",
                        "-days", "1"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pem = cert.read_text()
        fingerprint = hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem)).hexdigest()

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                if self.path != "/pair" or time.monotonic() > expires:
                    return self.reply(403, {"error": "Pairing session expired."})
                try:
                    if self.server.failed_attempts >= 5:
                        return self.reply(429, {"error": "Too many attempts. Start pairing again."})
                    length = int(self.headers.get("Content-Length", "0"))
                    if length < 1 or length > 1024:
                        raise ValueError("Invalid request size.")
                    data = json.loads(self.rfile.read(length))
                    if not secrets.compare_digest(str(data.get("code", "")), code):
                        self.server.failed_attempts += 1
                        raise ValueError("Incorrect pairing code.")
                    install_token(data.get("token"), args.token_file)
                    try:
                        subprocess.run(["sudo", "-n", "systemctl", "restart", "rob-vision-controller2.service"],
                                       check=True, timeout=15, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except (OSError, subprocess.SubprocessError):
                        pass  # The receiver can also pick up the token on its next restart.
                    self.reply(200, {"paired": True})
                    self.server.paired = True
                except (ValueError, TypeError, json.JSONDecodeError) as exc:
                    self.reply(400, {"error": str(exc)})

            def reply(self, status, payload):
                body = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_args):
                pass

        server = HTTPServer(("0.0.0.0", args.port), Handler)
        server.timeout = 1
        server.paired = False
        server.failed_attempts = 0
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(cert), str(key))
        server.socket = context.wrap_socket(server.socket, server_side=True)
        print("Pairing is open for five minutes. Enter these on the R.O.B. Vision Setup page:", flush=True)
        print(f"Code: {code}\nSHA-256 fingerprint: {fingerprint}", flush=True)
        try:
            while time.monotonic() < expires and not server.paired:
                server.handle_request()
        finally:
            server.server_close()
        print("Pairing complete." if server.paired else "Pairing timed out.", flush=True)


if __name__ == "__main__":
    main()
