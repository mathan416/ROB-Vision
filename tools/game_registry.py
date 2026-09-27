"""Edit a paired console's installed ROM registry from the UNO Q Setup page."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from tools.identify_game import parse_registry
from tools.controller_router_setup import paths as router_paths
from router_shared.controller_router import RouterStore

MAX_DOCUMENT = 65536
PORT = 8769


def atomic_write(path: Path, document: str, reference: Path | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stat = (path if path.exists() else reference).stat()
    fd, temporary = tempfile.mkstemp(prefix=".games-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            os.fchmod(stream.fileno(), stat.st_mode & 0o777)
            os.fchown(stream.fileno(), stat.st_uid, stat.st_gid)
            stream.write(document)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class RegistryStore:
    def __init__(self, path: Path, platform: str, apply=None, game_running=None):
        self.path = Path(path)
        self.platform = platform
        self.backup = self.path.with_name("games.previous.json")
        self.lock = threading.RLock()
        self.apply = apply or self._apply
        self.game_running = game_running or (lambda: subprocess.run(
            ["pgrep", "-x", "retroarch"], stdout=subprocess.DEVNULL).returncode == 0)

    def snapshot(self) -> dict:
        raw = self.path.read_bytes()
        if len(raw) > MAX_DOCUMENT:
            raise ValueError("Game registry exceeds 64 KiB")
        document = raw.decode("utf-8")
        parse_registry(document)
        return {"document": document, "revision": hashlib.sha256(raw).hexdigest(),
                "has_backup": self.backup.is_file()}

    def _apply(self):
        if self.platform == "batocera":
            from tools.batocera import select_games
            root = self.path.parents[1]
            available = [core for core in ("fceumm", "nestopia")
                         if (root / "build" / f"robvision_{core}_libretro.so").is_file()]
            if not available:
                raise RuntimeError("No installed R.O.B. Vision NES wrapper is available.")
            select_games(available=available, registry_path=self.path)
        else:
            from tools.install_retropie_frame_hook import install
            install(Path("/opt/retropie/configs"), registry_path=self.path)

    def operate(self, action: str, payload: dict) -> dict:
        with self.lock:
            current = self.snapshot()
            if action == "read":
                return current
            if action == "validate":
                parse_registry(payload.get("document", ""))
                return {"valid": True}
            if action not in ("save", "restore"):
                raise ValueError("Unknown registry action.")
            if payload.get("revision") != current["revision"]:
                raise ValueError("The registry changed elsewhere. Reload before saving.")
            if self.game_running():
                raise ValueError("Exit the running game before changing its registry.")
            if action == "restore":
                document = self.backup.read_text(encoding="utf-8")
            else:
                document = payload.get("document")
            if not isinstance(document, str):
                raise ValueError("Enter a JSON game registry.")
            parse_registry(document)
            atomic_write(self.backup, current["document"], reference=self.path)
            atomic_write(self.path, document)
            try:
                self.apply()
            except Exception:
                atomic_write(self.path, current["document"])
                raise
            return self.snapshot()


def serve(store: RegistryStore, token_file: Path, host="0.0.0.0", port=PORT,
          router_store: RouterStore | None = None):
    """Start a bounded token-protected endpoint on the paired console."""
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def setup(self):
            super().setup()
            self.connection.settimeout(3)

        def do_POST(self):
            if self.path not in ("/registry", "/router") or self.headers.get("Origin"):
                return self.reply(404, {"error": "Unknown endpoint."})
            try:
                offered = self.headers.get("Authorization", "")
                expected = token_file.read_text().strip()
                if not expected or not secrets.compare_digest(offered, "Bearer " + expected):
                    return self.reply(403, {"error": "Console pairing is required."})
                size = int(self.headers.get("Content-Length", "0"))
                if size < 1 or size > 262144:
                    raise ValueError("Console request is too large.")
                payload = json.loads(self.rfile.read(size))
                if not isinstance(payload, dict):
                    raise ValueError("Console request must be a JSON object.")
                if self.path == "/router":
                    if router_store is None:
                        raise ValueError("Controller Router is not installed on this console.")
                    if payload.get("action") == "save":
                        current = router_store.read()["config"]
                        buddy_ids = {source["id"] for entry in current["players"]
                                     for source in entry["sources"]
                                     if source["name"] == "R.O.B. Vision Controller 2"}
                        proposed = payload.get("config")
                        slots = proposed.get("players", []) if isinstance(proposed, dict) else []
                        proposed_buddy = {identity for entry in slots if isinstance(entry, dict)
                                          and entry.get("player") == 2
                                          for identity in entry.get("sources", [])}
                        if not buddy_ids or not buddy_ids <= proposed_buddy:
                            raise ValueError("Buddy must remain assigned to Player 2.")
                    if payload.get("action") == "rollback" and router_store.backup.exists():
                        previous = json.loads(router_store.backup.read_text())
                        if not any(entry.get("player") == 2 and any(
                                source.get("name") == "R.O.B. Vision Controller 2"
                                for source in entry.get("sources", []))
                                for entry in previous.get("players", [])):
                            raise ValueError("The previous snapshot predates Buddy. Save assignments instead.")
                    result = router_store.operate(payload.get("action"), payload)
                else:
                    result = store.operate(payload.get("action"), payload)
                self.reply(200, result)
            except (OSError, ValueError, TypeError, RuntimeError, UnicodeError, json.JSONDecodeError) as exc:
                self.reply(400, {"error": str(exc)})

        def reply(self, status, result):
            body = json.dumps(result).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = HTTPServer((host, port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def router_store_for(platform: str) -> RouterStore:
    config, es_inputs = router_paths(platform)
    return RouterStore(config, platform, es_inputs)
