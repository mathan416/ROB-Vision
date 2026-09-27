"""Batocera-specific configuration for the shared R.O.B. Vision receiver."""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.identify_game import DEFAULT_REGISTRY, identify, load_registry

CONFIG = Path("/userdata/system/batocera.conf")


def select_games(config=CONFIG, roms=Path("/userdata/roms/nes"), available=("fceumm", "nestopia"),
                 registry_path=DEFAULT_REGISTRY):
    """Select the proxy for exact known ROMs, preserving unrelated settings."""
    original = config.read_text()
    lines = original.splitlines()
    registry = load_registry(registry_path)
    chosen = []
    for rom in sorted(roms.iterdir()):
        if not rom.is_file() or not identify("nes", rom.name, registry):
            continue
        key = 'nes["{}"]'.format(rom.name)
        core_key = key + ".core"
        emu_key = key + ".emulator"
        existing = next((line.partition("=")[2].strip() for line in lines
                         if line.startswith(core_key + "=")), "")
        if existing and existing not in ("fceumm", "nestopia", "robvision_fceumm", "robvision_nestopia"):
            continue
        core = "nestopia" if existing.endswith("nestopia") else "fceumm"
        if core not in available:
            core = available[0]
        for setting, value in ((core_key, "robvision_" + core), (emu_key, "libretro")):
            match = next((i for i, line in enumerate(lines) if line.startswith(setting + "=")), None)
            if match is None:
                lines.append(setting + "=" + value)
            else:
                lines[match] = setting + "=" + value
        chosen.append(rom.name)
    updated = "\n".join(lines) + "\n"
    if updated != original:
        backup = config.with_name(config.name + ".before-rob-vision")
        if not backup.exists():
            shutil.copy2(config, backup)
        config.write_text(updated)
    return chosen


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.parse_args()
    print(select_games())
