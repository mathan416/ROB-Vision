"""Install Buddy as a source of the console's shared Player 2 router."""

from __future__ import annotations

import copy
import json
import os
import pwd
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from router_shared import controller_router as router
from router_shared.merged_gamepad import controller_candidates
from router_shared.storage import atomic_write

BUDDY = "R.O.B. Vision Controller 2"


def paths(platform: str):
    if platform == "retropie":
        return (Path("/etc/virtualglove/controller-router.json"),
                Path("/opt/retropie/configs/all/emulationstation/es_input.cfg"))
    if platform == "batocera":
        return (Path("/userdata/system/virtualglove/data/controller-router.json"),
                Path("/userdata/system/configs/emulationstation/es_input.cfg"))
    raise ValueError("Controller Router supports RetroPie and Batocera here.")


def source_file(platform: str) -> Path:
    if platform == "retropie":
        return Path("/home/pi/rob-vision/config/router_sources.json")
    if platform == "batocera":
        return Path("/userdata/system/rob-vision/config/router_sources.json")
    raise ValueError("Controller Router supports RetroPie and Batocera here.")


def proposed_config(current: dict | None, platform: str, candidates: list[dict]) -> dict:
    """Keep existing assignments, or seed known frontend controllers once."""
    if current is not None and current["platform"] != platform:
        raise ValueError("The installed Controller Router belongs to another platform.")
    if current is None:
        players = []
        physical = [item for item in candidates if item["name"] != BUDDY and
                    not item["name"].startswith("VirtualGlove Merged Player")]
        for number, item in enumerate(physical[:4], 1):
            players.append({"player": number, "sources": [router._saved_source(item)]})
        current = {"format": router.FORMAT, "platform": platform,
                   "players": players, "virtualglove_player": None,
                   "physical_scope": "nes"}
    else:
        current = copy.deepcopy(current)
    buddy = [item for item in candidates if item["name"] == BUDDY]
    if len(buddy) != 1:
        raise RuntimeError("Wait for the R.O.B. Vision receiver to publish one Buddy pad.")
    for entry in current["players"]:
        entry["sources"] = [source for source in entry["sources"]
                            if source["name"] != BUDDY or entry["player"] == 2]
    player2 = next((entry for entry in current["players"] if entry["player"] == 2), None)
    if player2 is None:
        player2 = {"player": 2, "sources": []}
        current["players"].append(player2)
    if not any(source["name"] == BUDDY for source in player2["sources"]):
        player2["sources"].append(router._saved_source(buddy[0]))
    return router.validate_config(current)


def ensure_buddy_frontend_mapping(path: Path, buddy: dict) -> bool:
    """Let an already-installed VirtualGlove Router discover Buddy too."""
    import xml.etree.ElementTree as ET
    if not path.is_file():
        raise RuntimeError("EmulationStation controller configuration is missing.")
    original = path.read_text()
    document = ET.fromstring(original)
    if document.tag != "inputList":
        raise ValueError("Unexpected EmulationStation controller configuration.")
    for entry in document.findall("inputConfig"):
        if entry.get("deviceName") == BUDDY and entry.get("deviceGUID", "").lower() == buddy["guid"]:
            return False
    if not buddy.get("guid") or not re.fullmatch(r"[0-9a-f]{32}", buddy["guid"]):
        raise ValueError("Buddy's SDL controller identity is unavailable.")
    closing = "</inputList>"
    if original.count(closing) != 1:
        raise ValueError("Cannot safely add Buddy to EmulationStation's controller list.")
    block = (f'  <inputConfig type="joystick" deviceName="{BUDDY}" '
             f'deviceGUID="{buddy["guid"]}">\n'
             '    <input name="a" type="button" id="0" value="1" code="304" />\n'
             '    <input name="b" type="button" id="1" value="1" code="305" />\n'
             '  </inputConfig>\n')
    backup = path.with_name(path.name + ".before-rob-vision-router")
    if not backup.exists():
        atomic_write(backup, original, path.stat().st_mode & 0o777)
    atomic_write(path, original.replace(closing, block + closing), path.stat().st_mode & 0o777)
    return True


def ensure(platform: str, *, config_path: Path | None = None,
           es_inputs: Path | None = None, sys_root: Path = Path("/sys/class/input"),
           dev_root: Path = Path("/dev/input"), wait_seconds: float = 8.0) -> bool:
    """Make one atomic, repeatable config update after the receiver starts."""
    default_config, default_es = paths(platform)
    path, es = config_path or default_config, es_inputs or default_es
    current = router.load_config(path) if path.exists() else None
    deadline = time.monotonic() + wait_seconds
    while True:
        descriptor = source_file(platform)
        candidates = controller_candidates(es, sys_root, dev_root,
                                           source_file=descriptor if descriptor.is_file() else None)
        if sum(item["name"] == BUDDY for item in candidates) == 1:
            break
        if time.monotonic() >= deadline:
            raise RuntimeError("Buddy's controller is not available; restart the R.O.B. Vision receiver.")
        time.sleep(0.1)
    if platform == "batocera" and Path(
            "/userdata/system/virtualglove/src/virtualglove/controller_router.py").is_file():
        ensure_buddy_frontend_mapping(es, next(item for item in candidates if item["name"] == BUDDY))
    updated = proposed_config(current, platform, candidates)
    if updated == current:
        return False
    if subprocess.run(["pgrep", "-x", "retroarch"], stdout=subprocess.DEVNULL).returncode == 0:
        raise RuntimeError("Exit the running game before changing controller assignments.")
    if path.exists():
        atomic_write(Path(str(path) + ".previous"), path.read_text())
    atomic_write(path, json.dumps(updated, indent=2) + "\n")
    return True


def retire_legacy_nes_override(path: Path = Path("/opt/retropie/configs/nes/retroarch.cfg")) -> bool:
    """One-time migration: Router now owns P2, so remove only our old block."""
    begin = "# BEGIN R.O.B. Vision (managed by installer)"
    end = "# END R.O.B. Vision (managed by installer)"
    if not path.is_file():
        raise RuntimeError("NES RetroArch configuration is missing.")
    original = path.read_text()
    pattern = re.compile(r"^" + re.escape(begin) + r"\n(.*?)^" +
                         re.escape(end) + r"\n?", re.DOTALL | re.MULTILINE)
    match = pattern.search(original)
    if not match:
        return False
    allowed = {"input_libretro_device_p2", "input_player2_joypad_index",
               "input_player2_a_btn", "input_player2_b_btn"}
    keys = {line.split("=", 1)[0].strip() for line in match.group(1).splitlines()
            if line.strip() and not line.lstrip().startswith("#")}
    if not keys <= allowed:
        raise ValueError("R.O.B. Vision's old NES block contains unfamiliar settings. Review it before migration.")
    backup = path.with_name(path.name + ".before-rob-vision-router")
    if not backup.exists():
        atomic_write(backup, original, path.stat().st_mode & 0o777)
    updated = original[:match.start()] + original[match.end():]
    atomic_write(path, updated, path.stat().st_mode & 0o777)
    if os.geteuid() == 0:
        account = pwd.getpwnam("pi")
        os.chown(path, account.pw_uid, account.pw_gid)
        os.chown(backup, account.pw_uid, account.pw_gid)
    return True


def retire_batocera_pad_overrides(
        path: Path = Path("/userdata/system/batocera.conf"),
        registry_path: Path = Path("/userdata/system/rob-vision/config/games.json")) -> bool:
    """Remove the old raw-pad P2 overrides after Router takes ownership."""
    if not path.is_file() or not registry_path.is_file():
        return False
    from tools.identify_game import registry_roms
    registry = registry_roms(registry_path)
    filenames = {name for name, game in registry.items()
                 if game in ("gyromite", "stack_up")}
    original = path.read_text()
    lines = original.splitlines(keepends=True)
    old_keys = {"input_libretro_device_p2", "input_player2_joypad_index",
                "input_player2_a_btn", "input_player2_b_btn"}
    remove = set()
    for filename in filenames:
        prefix = f'nes["{filename}"].retroarch.'
        found = {line[len(prefix):].split("=", 1)[0]: index
                 for index, line in enumerate(lines) if line.startswith(prefix) and "=" in line}
        if not old_keys <= set(found):
            continue
        if (lines[found["input_libretro_device_p2"]].split("=", 1)[1].strip() != "1" or
                lines[found["input_player2_a_btn"]].split("=", 1)[1].strip() != "0" or
                lines[found["input_player2_b_btn"]].split("=", 1)[1].strip() != "1"):
            continue
        remove.update(found[key] for key in old_keys)
    if not remove:
        return False
    backup = path.with_name(path.name + ".before-rob-vision-router")
    if not backup.exists():
        atomic_write(backup, original, path.stat().st_mode & 0o777)
    atomic_write(path, "".join(line for index, line in enumerate(lines) if index not in remove),
                 path.stat().st_mode & 0o777)
    return True


def activate(platform: str) -> None:
    config, _ = paths(platform)
    # Re-pairing an already configured console needs no Router restart or
    # migration. Keep its merged pads stable while EmulationStation is open.
    if platform == "retropie" and config.exists():
        current = router.load_config(config)
        buddy_players = [entry["player"] for entry in current["players"]
                         for source in entry["sources"] if source["name"] == BUDDY]
        if buddy_players == [2] and subprocess.run(
                ["systemctl", "is-active", "--quiet",
                 "virtualglove-controller-router.service"],
                stdout=subprocess.DEVNULL).returncode == 0:
            return
    if platform == "retropie" and any(
            subprocess.run(["pgrep", "-x", name],
                           stdout=subprocess.DEVNULL).returncode == 0
            for name in ("emulationstation", "emulationstatio")):
        raise RuntimeError("Exit EmulationStation before pairing or upgrading Controller Router.")
    previous = config.read_text() if config.exists() else None
    changed = ensure(platform)
    try:
        if platform == "retropie":
            subprocess.run(["systemctl", "enable", "--now",
                            "virtualglove-controller-router.service"], check=True)
            subprocess.run(["systemctl", "restart",
                            "virtualglove-controller-router.service"], check=True)
            socket_path = Path("/run/virtualglove/controller-router.sock")
            for _attempt in range(80):
                if socket_path.is_socket():
                    break
                time.sleep(0.1)
            else:
                raise RuntimeError("Controller Router did not become ready. Check its service log.")
            retire_legacy_nes_override()
        else:
            # Batocera's service manager has no systemd unit. The R.O.B.
            # service starts the shared Router when VirtualGlove has not.
            retire_batocera_pad_overrides()
            subprocess.run(["batocera-services", "restart", "ROBVision"], check=True)
    except Exception:
        if changed:
            if previous is None:
                try:
                    config.unlink()
                except FileNotFoundError:
                    pass
            else:
                atomic_write(config, previous)
        raise


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("platform", choices=("retropie", "batocera"))
    args = parser.parse_args()
    try:
        before, _ = paths(args.platform)
        previous = before.read_text() if before.exists() else None
        activate(args.platform)
        changed = previous != (before.read_text() if before.exists() else None)
        print("Buddy added to Player 2." if changed else "Buddy is already assigned to Player 2.")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Controller Router setup stopped: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
