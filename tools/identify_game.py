#!/usr/bin/env python3
"""Resolve RetroPie launch metadata to a R.O.B. Vision game ID.

This local helper does not contact a robot or change RetroPie hooks. A future
installer can use its result as input to a paired launch-event sender.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "config" / "games.json"
SUPPORTED_GAMES = frozenset({"gyromite", "stack_up"})
SUPPORTED_SYSTEMS = frozenset({"nes", "famicom"})
SUPPORTED_EXTENSIONS = frozenset({".nes", ".zip", ".7z"})


def parse_registry(text: str) -> dict[str, str]:
    """Validate a registry document and return case-insensitive ROM mappings."""
    if not isinstance(text, str):
        raise ValueError("Game registry must be JSON text")
    if len(text.encode("utf-8")) > 65536:
        raise ValueError("Game registry exceeds 64 KiB")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    data = json.loads(text, object_pairs_hook=unique)
    if not isinstance(data, dict) or data.get("schema") != 1 or not isinstance(data.get("games"), dict):
        raise ValueError("Expected a schema 1 games registry")
    result: dict[str, str] = {}
    overrides: dict[str, str] = {}
    for filename, game in data["games"].items():
        if (not isinstance(filename, str) or not filename or Path(filename).name != filename
                or any(ord(char) < 32 for char in filename)
                or Path(filename).suffix.casefold() not in SUPPORTED_EXTENSIONS):
            raise ValueError(f"Invalid ROM basename: {filename!r}")
        if game not in SUPPORTED_GAMES:
            raise ValueError(f"Unsupported game ID for {filename!r}: {game!r}")
        key = filename.casefold()
        if key in result:
            raise ValueError(f"Duplicate ROM basename: {filename!r}")
        override = retropie_override_key(filename)
        if override in overrides and overrides[override] != game:
            raise ValueError(f"RetroPie filename collision: {filename!r}")
        overrides[override] = game
        result[key] = game
    return result


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, str]:
    """Load exact, case-insensitive ROM basenames with no ambiguous entries."""
    return parse_registry(path.read_text(encoding="utf-8"))


def registry_roms(path: Path = DEFAULT_REGISTRY) -> dict[str, str]:
    """Return validated ROM names with their original spelling for console setup."""
    load_registry(path)
    return json.loads(path.read_text(encoding="utf-8"))["games"]


def identify(system: str, rom: str, registry: dict[str, str]) -> str | None:
    """Match only a launched NES/Famicom file's exact basename and extension."""
    if system.casefold() not in SUPPORTED_SYSTEMS or not rom:
        return None
    return registry.get(Path(rom).name.casefold())


def retropie_override_key(filename: str) -> str:
    """Match runcommand's clean_name("nes_${ROM_BN}") for per-ROM choices."""
    return re.sub(r"[^A-Za-z0-9_-]", "", "nes_" + Path(filename).stem)


def event(action: str, system: str = "", rom: str = "",
          registry: dict[str, str] | None = None) -> dict[str, str | None]:
    """Describe a launch or exit; unknown games and exits clear game state."""
    if action not in {"start", "end"}:
        raise ValueError("Action must be start or end")
    game = identify(system, rom, registry or {}) if action == "start" else None
    return {
        "event": action,
        "state": "recognized" if game else "idle",
        "game": game,
        "system": system.casefold() if action == "start" else "",
        "rom": Path(rom).name if action == "start" and rom else "",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "end"))
    parser.add_argument("system", nargs="?", default="")
    parser.add_argument("emulator", nargs="?", default="")
    parser.add_argument("rom", nargs="?", default="")
    parser.add_argument("command", nargs="?", default="")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()
    try:
        registry = load_registry(args.registry) if args.action == "start" else {}
        result = event(args.action, args.system, args.rom, registry)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Cannot identify game: {exc}\n")
    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
