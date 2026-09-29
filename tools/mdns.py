"""Resolve local controller names on consoles without an NSS mDNS module."""

import ipaddress
import socket
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def resolve_host(host):
    if not host.lower().rstrip('.').endswith('.local'):
        return host
    name = host.rstrip('.')
    if not name.isascii() or any(char.isspace() for char in name) or len(name) > 253:
        raise socket.gaierror('Invalid local hostname')
    endpoint = Path('/run/avahi-daemon/socket')
    if not endpoint.is_socket():
        return socket.gethostbyname(host)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(1)
        connection.connect(str(endpoint))
        connection.sendall(('RESOLVE-HOSTNAME-IPV4 ' + name + '\n').encode('ascii'))
        response = b''
        while b'\n' not in response and len(response) < 1024:
            chunk = connection.recv(1024 - len(response))
            if not chunk:
                break
            response += chunk
    fields = response.decode('ascii', 'replace').split()
    if len(fields) != 5 or fields[0] != '+' or fields[3].lower().rstrip('.') != name.lower():
        raise socket.gaierror('Avahi could not resolve ' + name)
    try:
        return str(ipaddress.IPv4Address(fields[4]))
    except ValueError:
        raise socket.gaierror('Avahi returned an invalid IPv4 address') from None


def resolved_url(url):
    parsed = urlsplit(url)
    if parsed.scheme != 'http' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Expected a local HTTP controller URL')
    address = resolve_host(parsed.hostname)
    return urlunsplit((parsed.scheme, address + (':' + str(parsed.port) if parsed.port else ''),
                       parsed.path, parsed.query, parsed.fragment))
