#!/usr/bin/env python3
"""Install the Batocera receiver, cores, launch hook and exact ROM selections.

Run on Batocera as root from a staged checkout:
    python3 scripts/install_batocera.py --controller arduiain.local
"""

import argparse
import ctypes
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.install import copy_file, copy_tree_merge, unlink_if_exists, valid_controller, write_file, validate_receiver_source
from tools.batocera import select_games
from tools.identify_game import load_registry

DEST = Path("/userdata/system/rob-vision")
CONFIG = Path("/userdata/system/batocera.conf")
SERVICES = Path("/userdata/system/services")
SCRIPTS = Path("/userdata/system/scripts")
ES_SERVICE = Path("/etc/init.d/S31emulationstation")
STOCK_CORES = Path("/usr/lib/libretro")
CORE_INFO = Path("/usr/share/libretro/info")


def suspend_menu():
    if subprocess.run(["pidof", "emulationstation"], stdout=subprocess.DEVNULL).returncode:
        return False
    if not ES_SERVICE.is_file():
        raise RuntimeError("EmulationStation is running but its Batocera service was not found.")
    subprocess.run([str(ES_SERVICE), "suspend"], check=True)
    try:
        deadline = time.monotonic() + 12
        while subprocess.run(["pidof", "emulationstation"], stdout=subprocess.DEVNULL).returncode == 0:
            if time.monotonic() >= deadline:
                raise RuntimeError("EmulationStation did not suspend; installation stopped before receiver restart.")
            time.sleep(.2)
    except Exception:
        resume_menu()
        raise
    return True


def resume_menu():
    if subprocess.run(["pidof", "emulationstation"], stdout=subprocess.DEVNULL).returncode == 0:
        Path("/tmp/suspend.please").unlink(missing_ok=True)
        return
    try:
        subprocess.run([str(ES_SERVICE), "resume"], check=True, timeout=8)
    except subprocess.TimeoutExpired as exc:
        if subprocess.run(["pidof", "emulationstation"], stdout=subprocess.DEVNULL).returncode == 0:
            Path("/tmp/suspend.please").unlink(missing_ok=True)
            return
        raise RuntimeError("EmulationStation did not resume after installation.") from exc


def available_cores(core_dir=STOCK_CORES, info_dir=CORE_INFO):
    """Install only wrappers for NES cores actually supplied by this Batocera image."""
    cores = [core for core in ("fceumm", "nestopia")
             if (core_dir / f"{core}_libretro.so").is_file()
             and (info_dir / f"{core}_libretro.info").is_file()]
    if not cores:
        raise RuntimeError("Batocera needs an installed FCEUmm or Nestopia libretro core and its info file.")
    return cores


def wrapper_arch(machine):
    """Map Linux machine names to the ABI directories in the release package."""
    aliases = {"amd64": "x86_64", "i386": "x86", "i486": "x86", "i586": "x86",
               "i686": "x86", "arm64": "aarch64", "armv7": "armv7l",
               "armv8l": "armv7l", "armv6": "armv6l"}
    return aliases.get(machine.lower(), machine.lower())


def prepare_wrappers(source, build_dir, cores, machine=None):
    """Use a native package or compile for this machine before changing the installation."""
    machine = wrapper_arch(machine or platform.machine())
    bundled = source / "deploy/batocera/cores" / machine
    compiler = shutil.which("gcc") or shutil.which("cc")
    proxy_source = source / "deploy/retropie/rob_vision_fceumm_proxy.c"
    prepared = {}
    for core in cores:
        name = f"robvision_{core}_libretro.so"
        packaged = bundled / name
        if packaged.is_file():
            try:
                ctypes.CDLL(str(packaged))
            except OSError:
                if not compiler:
                    raise RuntimeError(f"The bundled {machine} {core} wrapper cannot load on this Batocera build; a native C compiler is required.")
            else:
                prepared[core] = packaged
                continue
        if not compiler:
            raise RuntimeError(f"No {machine} {core} wrapper is bundled and this Batocera image has no C compiler. No files were changed.")
        if not proxy_source.is_file():
            raise RuntimeError("The frame wrapper source is missing from the release package.")
        output = build_dir / name
        command = [compiler, "-std=gnu11", "-O2", "-fPIC", "-shared", "-Wall", "-Wextra"]
        if core == "nestopia":
            command.append("-DROB_USE_NESTOPIA")
        command.extend((f'-DROB_REAL_CORE_PATH="/usr/lib/libretro/{core}_libretro.so"',
                        "-o", str(output), str(proxy_source), "-ldl"))
        subprocess.run(command, check=True)
        ctypes.CDLL(str(output))
        prepared[core] = output
    return prepared


def install(source=ROOT, destination=DEST, controller=None):
    if sys.platform != "linux" or os.geteuid() != 0:
        raise RuntimeError("Run this installer as root on Batocera.")
    if sys.version_info < (3, 9):
        raise RuntimeError("Python 3.9 or newer is required on Batocera.")
    if not CONFIG.is_file() or not Path("/usr/lib/libretro").is_dir():
        raise RuntimeError("Batocera configuration and Libretro paths are required.")
    if not shutil.which("batocera-services"):
        raise RuntimeError("Batocera service manager is missing.")
    if not shutil.which("openssl"):
        raise RuntimeError("OpenSSL is required for first-time pairing.")
    try:
        ctypes.CDLL("libSDL2-2.0.so.0")
    except OSError as exc:
        raise RuntimeError("Batocera's SDL2 joystick library is required.") from exc
    cores = available_cores()
    if subprocess.run(["pgrep", "-x", "retroarch"], stdout=subprocess.DEVNULL).returncode == 0:
        raise RuntimeError("Exit the running game before installing.")
    validate_receiver_source(source)
    load_registry(destination / "config/games.json" if (destination / "config/games.json").is_file()
                  else source / "config/games.json")
    old_url = destination / "controller.url"
    if controller is None and old_url.is_file():
        controller = old_url.read_text().strip().removeprefix("http://")
    if not controller:
        raise ValueError("Provide --controller with the UNO Q hostname or IP.")
    valid_controller(controller)
    with tempfile.TemporaryDirectory(prefix="rob-vision-cores-") as build:
        libraries = prepare_wrappers(source, Path(build), cores)
        menu_suspended = suspend_menu()
        try:
            if (SERVICES / "ROBVision").is_file():
                subprocess.run(["batocera-services", "stop", "ROBVision"], check=True)
            destination.mkdir(parents=True, exist_ok=True)
            for folder in ("tools", "controller", "config"):
                copy_tree_merge(source / folder, destination / folder,
                                preserve_registry=(folder == "config"))
            for library in libraries.values():
                copy_file(library, destination / "build" / library.name, 0o755)
            for core in ("fceumm", "nestopia"):
                if core not in libraries:
                    unlink_if_exists(destination / "build" / f"robvision_{core}_libretro.so")
            write_file(old_url, f"http://{controller}\n", 0o600)
            copy_file(source / "deploy/batocera/ROBVision", SERVICES / "ROBVision", 0o755)
            copy_file(source / "deploy/batocera/zz-robvision-game", SCRIPTS / "zz-robvision-game", 0o755)
            copy_file(source / "deploy/batocera/retroarch-joypad.cfg",
                      Path("/userdata/system/configs/retroarch/inputs/R.O.B. Vision Controller 2.cfg"))
            chosen = select_games(CONFIG, Path("/userdata/roms/nes"), available=cores,
                                  registry_path=destination / "config/games.json")
            subprocess.run(["batocera-services", "enable", "ROBVision"], check=True)
            subprocess.run(["batocera-services", "restart", "ROBVision"], check=True)
        finally:
            if menu_suspended:
                resume_menu()
    print("Installed R.O.B. Vision for:", ", ".join(chosen) or "no registered ROMs present")
    if not (destination / "token").is_file():
        print("Pair on the UNO Q Setup page using:")
        print("  python3 /userdata/system/rob-vision/tools/retropie_pair.py --platform batocera")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller", help="UNO Q hostname or LAN IP")
    args = parser.parse_args()
    try:
        install(controller=args.controller)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        parser.exit(1, "Installation stopped: {}\n".format(exc))


if __name__ == "__main__":
    main()
