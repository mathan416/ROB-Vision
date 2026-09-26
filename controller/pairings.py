"""Persistent, independently revocable game-console credentials."""

import json
import ipaddress
import os
import secrets
import tempfile
import threading
from pathlib import Path
from time import monotonic

PLATFORMS = {"retropie": "RetroPie", "batocera": "Batocera"}


class PairingStore:
    def __init__(self, path: Path, legacy_token: str = ""):
        self.path = Path(path)
        self.legacy_token = legacy_token
        self.lock = threading.RLock()
        self.records = {}
        self.last_seen = {}
        self.last_address = {}
        self.legacy_seen = set()
        self.blocked_legacy = set()
        if self.path.exists():
            data = json.loads(self.path.read_text())
            if data.get("schema") != 1 or not isinstance(data.get("consoles"), list):
                raise ValueError("Invalid paired-console registry")
            for record in data["consoles"]:
                if (record.get("platform") not in PLATFORMS or
                        not isinstance(record.get("id"), str) or
                        not isinstance(record.get("token"), str) or
                        len(record["id"]) != 32 or len(record["token"]) < 16):
                    raise ValueError("Invalid paired-console record")
                self.records[record["id"]] = record
            self.blocked_legacy = set(data.get("blocked_legacy", [])) & PLATFORMS.keys()

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"schema": 1, "consoles": list(self.records.values()),
                   "blocked_legacy": sorted(self.blocked_legacy)}
        fd, temporary = tempfile.mkstemp(prefix=".paired-consoles-", dir=self.path.parent)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w") as file:
                json.dump(payload, file, separators=(",", ":"))
                file.write("\n")
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def new_credentials(self):
        return secrets.token_hex(16), secrets.token_urlsafe(48)

    def add(self, console_id, token, platform, host):
        if platform not in PLATFORMS or not isinstance(host, str) or not host:
            raise ValueError("Invalid console identity")
        with self.lock:
            for old_id, record in list(self.records.items()):
                if record["host"].casefold() == host.casefold():
                    del self.records[old_id]
                    self.last_seen.pop(old_id, None)
                    self.last_address.pop(old_id, None)
            self.records[console_id] = {"id": console_id, "token": token,
                                        "platform": platform, "host": host}
            self.blocked_legacy.add(platform)
            self.legacy_seen.discard(platform)
            self._save()

    def verify(self, headers):
        console_id = headers.get("X-ROB-Console-ID", "")
        platform = headers.get("X-ROB-Receiver", "")
        bearer = headers.get("Authorization", "")
        if not bearer.startswith("Bearer "):
            return None
        offered = bearer[7:]
        with self.lock:
            record = self.records.get(console_id)
            if (record and record["platform"] == platform and
                    secrets.compare_digest(offered, record["token"])):
                return {key: record[key] for key in ("id", "platform", "host")}
            if (not console_id and platform in PLATFORMS and platform not in self.blocked_legacy
                    and self.legacy_token and secrets.compare_digest(offered, self.legacy_token)):
                self.legacy_seen.add(platform)
                return {"id": "legacy:" + platform, "platform": platform, "host": ""}
        return None

    def seen(self, console_id, address=None):
        with self.lock:
            self.last_seen[console_id] = monotonic()
            try:
                ip = ipaddress.IPv4Address(address)
            except (ipaddress.AddressValueError, TypeError):
                return
            if ip.is_private and not (ip.is_loopback or ip.is_link_local):
                self.last_address[console_id] = str(ip)

    def list_public(self, active_id=None):
        with self.lock:
            rows = []
            for record in self.records.values():
                rows.append({"id": record["id"], "name": PLATFORMS[record["platform"]],
                             "host": record["host"],
                             "online": monotonic() - self.last_seen.get(record["id"], 0) < 3,
                             "active": record["id"] == active_id, "legacy": False})
            for platform in sorted(self.legacy_seen):
                identifier = "legacy:" + platform
                rows.append({"id": identifier, "name": PLATFORMS[platform], "host": "",
                             "online": monotonic() - self.last_seen.get(identifier, 0) < 3,
                             "active": identifier == active_id, "legacy": True})
            return sorted(rows, key=lambda row: (not row["active"], row["name"], row["host"]))

    def remove(self, console_id):
        with self.lock:
            if console_id.startswith("legacy:"):
                platform = console_id.partition(":")[2]
                if platform not in self.legacy_seen:
                    raise ValueError("Console pairing was not found.")
                self.legacy_seen.discard(platform)
                self.blocked_legacy.add(platform)
            elif console_id in self.records:
                del self.records[console_id]
            else:
                raise ValueError("Console pairing was not found.")
            self.last_seen.pop(console_id, None)
            self.last_address.pop(console_id, None)
            self._save()
