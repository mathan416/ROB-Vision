#!/usr/bin/env python3
"""Expose bounded host Avahi lookups to the App Lab container over a Unix socket."""

import os
import re
import socket
import socketserver
import stat
from pathlib import Path

ENDPOINT = Path("/app/data/.avahi-resolver.sock")
HOST_AVAHI = "/run/avahi-daemon/socket"
QUERY = re.compile(rb"RESOLVE-HOSTNAME-IPV4 [A-Za-z0-9][A-Za-z0-9.-]{0,246}\.local\n", re.I)


def lookup(request):
    if not QUERY.fullmatch(request):
        return b"-1 Invalid local query\n"
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as upstream:
        upstream.settimeout(0.5)
        upstream.connect(HOST_AVAHI)
        upstream.sendall(request)
        response = b""
        while b"\n" not in response and len(response) < 1024:
            chunk = upstream.recv(1024 - len(response))
            if not chunk:
                break
            response += chunk
    return response if response.endswith(b"\n") else b"-1 Invalid Avahi response\n"


class Handler(socketserver.StreamRequestHandler):
    timeout = 0.6

    def handle(self):
        try:
            answer = lookup(self.rfile.readline(300))
        except OSError:
            answer = b"-1 Avahi unavailable\n"
        self.wfile.write(answer)


def main():
    ENDPOINT.parent.mkdir(parents=True, exist_ok=True)
    if ENDPOINT.exists() or ENDPOINT.is_symlink():
        if not stat.S_ISSOCK(ENDPOINT.lstat().st_mode):
            raise RuntimeError("Refusing to replace a non-socket resolver path")
        ENDPOINT.unlink()
    os.umask(0o117)
    with socketserver.UnixStreamServer(str(ENDPOINT), Handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
