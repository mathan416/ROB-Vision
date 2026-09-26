"""Batocera-specific configuration for the shared R.O.B. Vision receiver."""

import ctypes
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.identify_game import identify, load_registry

CONFIG = Path("/userdata/system/batocera.conf")
RETROARCH_CONFIG = Path("/userdata/system/configs/retroarch/retroarchcustom.cfg")
PAD_NAME = "R.O.B. Vision Controller 2"


def select_games(config=CONFIG, roms=Path("/userdata/roms/nes")):
    """Select the proxy for exact known ROMs, preserving unrelated settings."""
    original = config.read_text()
    lines = original.splitlines()
    registry = load_registry()
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


def pad_index():
    """Find the pad in RetroArch's joystick order, not Linux's jsN order."""
    try:
        sdl = ctypes.CDLL("libSDL2-2.0.so.0")
    except OSError as exc:
        raise RuntimeError("Batocera's SDL2 joystick library is required.") from exc
    sdl.SDL_Init.argtypes = [ctypes.c_uint32]
    sdl.SDL_Init.restype = ctypes.c_int
    sdl.SDL_NumJoysticks.restype = ctypes.c_int
    sdl.SDL_JoystickNameForIndex.argtypes = [ctypes.c_int]
    sdl.SDL_JoystickNameForIndex.restype = ctypes.c_char_p
    if sdl.SDL_Init(0x200) != 0:
        raise RuntimeError("Could not enumerate Batocera joysticks.")
    try:
        found = [i for i in range(sdl.SDL_NumJoysticks())
                 if (sdl.SDL_JoystickNameForIndex(i) or b"").decode(errors="replace") == PAD_NAME]
    finally:
        sdl.SDL_QuitSubSystem(0x200)
    if len(found) != 1:
        raise RuntimeError("Start the receiver before launching Gyromite; exactly one virtual pad is required.")
    return found[0]


def configure_player2_overrides(config=CONFIG, roms=Path("/userdata/roms/nes"), index=None):
    """Apply Batocera's persistent per-ROM RetroArch overrides before configgen runs."""
    if index is None:
        deadline = time.monotonic() + 3.0
        while True:
            try:
                index = pad_index()
                break
            except RuntimeError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(.1)
    if not 0 <= index <= 15:
        raise ValueError("Invalid virtual pad index")
    original = config.read_text()
    lines = original.splitlines()
    registry = load_registry()
    values = {"input_libretro_device_p2": "1",
              "input_player2_joypad_index": str(index),
              "input_player2_a_btn": "1", "input_player2_b_btn": "0"}
    for rom in sorted(roms.iterdir()):
        if not rom.is_file() or identify("nes", rom.name, registry) != "gyromite":
            continue
        prefix = 'nes["{}"].retroarch.'.format(rom.name)
        for key, value in values.items():
            setting = prefix + key
            matches = [i for i, line in enumerate(lines) if line.startswith(setting + "=")]
            if matches:
                lines[matches[0]] = setting + "=" + value
                for i in reversed(matches[1:]):
                    del lines[i]
            else:
                lines.append(setting + "=" + value)
    updated = "\n".join(lines) + "\n"
    if updated != original:
        backup = config.with_name(config.name + ".before-rob-vision")
        if not backup.exists():
            shutil.copy2(config, backup)
        config.write_text(updated)
    return index


def map_player2(config=RETROARCH_CONFIG, index=None):
    """Batocera regenerates this file at launch. Alter only Gyromite's P2 keys."""
    index = pad_index() if index is None else index
    if not 0 <= index <= 15:
        raise ValueError("Invalid virtual pad index")
    original = config.read_text()
    values = {"input_libretro_device_p2": "1",
              "input_player2_joypad_index": str(index),
              "input_player2_a_btn": "1", "input_player2_b_btn": "0"}
    lines = original.splitlines()
    for key, value in values.items():
        indices = [i for i, line in enumerate(lines) if re.match(r"^\s*" + key + r"\s*=", line)]
        if indices:
            lines[indices[0]] = key + ' = "' + value + '"'
            for i in reversed(indices[1:]):
                del lines[i]
        else:
            lines.append(key + ' = "' + value + '"')
    updated = "\n".join(lines) + "\n"
    if updated != original:
        config.write_text(updated)
    return index


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("select", "player2", "configure"))
    args = parser.parse_args()
    print(select_games() if args.action == "select" else
          configure_player2_overrides() if args.action == "configure" else map_player2())
