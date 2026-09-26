"""Resolve console .local names through the UNO Q host's Avahi socket."""

import ipaddress
import os
import socket
import time
from pathlib import Path

APP_SOCKET = Path(__file__).resolve().parents[1] / "data/.avahi-resolver.sock"
HOST_SOCKET = Path("/run/avahi-daemon/socket")
_cache = {}


def resolve_ipv4(host: str) -> str:
    """Return a fresh IPv4 address; cache Avahi answers for at most five seconds."""
    name = host.rstrip(".")
    try:
        return str(ipaddress.IPv4Address(name))
    except ipaddress.AddressValueError:
        pass
    if not name.lower().endswith(".local"):
        return socket.gethostbyname(host)
    if not name.isascii() or any(char.isspace() for char in name) or len(name) > 253:
        raise socket.gaierror("Invalid .local console name")
    endpoint = APP_SOCKET if APP_SOCKET.exists() else HOST_SOCKET
    if not endpoint.exists():
        if os.environ.get("APP_HOME"):
            raise socket.gaierror("UNO Q local-name resolver is unavailable; restart R.O.B. Vision in App Lab")
        return socket.gethostbyname(host)
    cached = _cache.get(name.casefold())
    now = time.monotonic()
    if cached and cached[0] > now:
        return cached[1]
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(0.7)
        connection.connect(str(endpoint))
        connection.sendall(("RESOLVE-HOSTNAME-IPV4 " + name + "\n").encode("ascii"))
        response = b""
        while b"\n" not in response and len(response) < 1024:
            chunk = connection.recv(1024 - len(response))
            if not chunk:
                break
            response += chunk
    fields = response.decode("ascii", "replace").split()
    if len(fields) != 5 or fields[0] != "+" or fields[3].lower().rstrip(".") != name.lower():
        raise socket.gaierror("Avahi could not resolve " + name)
    try:
        address = str(ipaddress.IPv4Address(fields[4]))
    except ValueError:
        raise socket.gaierror("Avahi returned an invalid IPv4 address") from None
    if len(_cache) >= 256:
        _cache.clear()
    _cache[name.casefold()] = (now + 5.0, address)
    return address
