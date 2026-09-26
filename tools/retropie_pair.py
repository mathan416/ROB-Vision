#!/usr/bin/env python3
"""One-time, fingerprint-checked pairing for a prepared console receiver."""

import argparse
import hashlib
import json
import os
import re
import secrets
import ssl
import subprocess
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def activate_receiver(platform):
    """Finish first pairing before reporting success to the Uno Q."""
    if platform == "batocera":
        commands = [["batocera-services", "restart", "ROBVision"]]
    else:
        prefix = [] if os.geteuid() == 0 else ["sudo", "-n"]
        service = "rob-vision-controller2.service"
        commands = [prefix + ["systemctl", "enable", service],
                    prefix + ["systemctl", "restart", service],
                    prefix + ["/usr/bin/python3", "/home/pi/rob-vision/scripts/install.py", "player2"]]
    for command in commands:
        subprocess.run(command, check=True, timeout=30, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)


def install_token(token, destination):
    if not isinstance(token, str) or not 16 <= len(token) <= 256 or any(c.isspace() for c in token):
        raise ValueError("Invalid controller token.")
    owner = destination.stat() if destination.exists() else None
    restore_file(destination, (token + "\n").encode("utf-8"), owner)
    if owner is None and os.geteuid() == 0:
        parent = destination.parent.stat()
        os.chown(destination, parent.st_uid, parent.st_gid)


def install_console_id(console_id, destination):
    if (not isinstance(console_id, str) or len(console_id) != 32 or
            any(char not in "0123456789abcdef" for char in console_id)):
        raise ValueError("Invalid console ID.")
    install_token(console_id, destination)


def controller_target(platform, token_file, url):
    """Prepare the installed receiver address supplied by the paired UNO Q."""
    if url is None:  # Compatibility with UNO Q controllers installed before this update.
        return None, None
    if not isinstance(url, str) or not re.fullmatch(r"http://[A-Za-z0-9][A-Za-z0-9.:-]{0,258}", url):
        raise ValueError("Invalid UNO Q receiver address.")
    parsed = urlsplit(url)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid UNO Q receiver port.") from exc
    if (not parsed.hostname or parsed.hostname.lower() == "localhost" or
            port is not None and not 1 <= port <= 65535):
        raise ValueError("Invalid UNO Q receiver address.")
    path = token_file.with_name("controller.url" if platform == "batocera" else "receiver.env")
    original = path.read_text(encoding="utf-8")
    if platform == "batocera":
        return path, url + "\n"
    updated, count = re.subn(r"(?m)^ROB_VISION_URL=[^\n]*$", "ROB_VISION_URL=" + url,
                             original)
    if count != 1:
        raise ValueError("RetroPie receiver configuration is missing its UNO Q address.")
    return path, updated


def restore_file(path, content, stat=None):
    """Atomically write or restore a pairing file without leaving partial data."""
    if content is None:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        return
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".pairing-" + secrets.token_hex(6))
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as file:
            if stat is not None:
                os.fchmod(file.fileno(), stat.st_mode & 0o777)
                if os.geteuid() == 0:
                    os.fchown(file.fileno(), stat.st_uid, stat.st_gid)
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def apply_pairing(platform, token_file, console_id, token, controller_url):
    """Change credentials and destination together, restoring the old link on failure."""
    target, new_target = controller_target(platform, token_file, controller_url)
    identifier = token_file.with_name("console-id")
    paths = [identifier, token_file] + ([target] if target else [])
    previous = [(path, path.read_bytes() if path.exists() else None,
                 path.stat() if path.exists() else None) for path in paths]
    try:
        install_console_id(console_id, identifier)
        install_token(token, token_file)
        if target:
            restore_file(target, new_target.encode("utf-8"), previous[-1][2])
        activate_receiver(platform)
    except Exception:
        for path, content, stat in previous:
            restore_file(path, content, stat)
        try:
            activate_receiver(platform)
        except (OSError, subprocess.SubprocessError):
            pass
        raise


def detect_platform():
    """Select the console's service manager when the helper is run directly."""
    if Path("/userdata/system/batocera.conf").is_file() and Path("/usr/lib/libretro").is_dir():
        return "batocera"
    if Path("/opt/retropie/configs").is_dir():
        return "retropie"
    raise ValueError("This console is neither a RetroPie nor Batocera installation.")


def main():
    parser = argparse.ArgumentParser(description="Pair this console with R.O.B. Vision.")
    parser.add_argument("--port", type=int, default=8768)
    parser.add_argument("--platform", choices=("retropie", "batocera"),
                        help="Console platform; detected automatically when omitted")
    parser.add_argument("--token-file", type=Path)
    args = parser.parse_args()
    detected = detect_platform()
    if args.platform and args.platform != detected:
        parser.error(f"This is {detected}, not {args.platform}.")
    args.platform = detected
    if args.token_file is None:
        args.token_file = (Path("/userdata/system/rob-vision/token") if args.platform == "batocera"
                           else Path.home() / ".config/rob-vision/token")
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
                    console_id = data.get("console_id")
                    offered_token = data.get("token")
                    if (not isinstance(offered_token, str) or not 16 <= len(offered_token) <= 256 or
                            any(char.isspace() for char in offered_token)):
                        raise ValueError("Invalid controller token.")
                    apply_pairing(args.platform, args.token_file, console_id,
                                  offered_token, data.get("controller_url"))
                    self.reply(200, {"paired": True, "platform": args.platform,
                                     "console_id": console_id})
                    self.server.paired = True
                except (ValueError, TypeError, json.JSONDecodeError, OSError,
                        subprocess.SubprocessError) as exc:
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
        return server.paired


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
