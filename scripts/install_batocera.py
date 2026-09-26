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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.install import copy_file, copy_tree_merge, valid_controller, write_file
from tools.batocera import select_games

DEST = Path("/userdata/system/rob-vision")
CONFIG = Path("/userdata/system/batocera.conf")
SERVICES = Path("/userdata/system/services")
SCRIPTS = Path("/userdata/system/scripts")
VERSION_FILE = Path("/usr/share/batocera/batocera.version")


def supported_hardware(machine=None, version_file=VERSION_FILE):
    machine = machine or platform.machine()
    version = version_file.read_text().split()[0] if version_file.is_file() else "unknown"
    if machine != "x86_64" or version != "43.1":
        raise RuntimeError(
            f"Batocera {version} on {machine} has no validated R.O.B. Vision 0.1.0 build; "
            "supported: Batocera 43.1 x86_64. No files were changed."
        )


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
    supported_hardware()
    if not Path("/usr/lib/libretro/fceumm_libretro.so").is_file():
        raise RuntimeError("The stock Batocera FCEUmm core is required before installation.")
    libraries = source / "deploy/batocera/cores/x86_64"
    if any(not (libraries / f"robvision_{core}_libretro.so").is_file()
           for core in ("fceumm", "nestopia")):
        raise RuntimeError("Both bundled x86_64 Batocera frame wrappers are required.")
    if subprocess.run(["pgrep", "-x", "retroarch"], stdout=subprocess.DEVNULL).returncode == 0:
        raise RuntimeError("Exit the running game before installing.")
    old_url = destination / "controller.url"
    if controller is None and old_url.is_file():
        controller = old_url.read_text().strip().removeprefix("http://")
    if not controller:
        raise ValueError("Provide --controller with the UNO Q hostname or IP.")
    valid_controller(controller)
    destination.mkdir(parents=True, exist_ok=True)
    for folder in ("tools", "controller", "config"):
        copy_tree_merge(source / folder, destination / folder)
    for core in ("fceumm", "nestopia"):
        library = libraries / f"robvision_{core}_libretro.so"
        ctypes.CDLL(str(library))
        copy_file(library, destination / "build" / library.name, 0o755)
    write_file(old_url, f"http://{controller}\n", 0o600)
    copy_file(source / "deploy/batocera/ROBVision", SERVICES / "ROBVision", 0o755)
    copy_file(source / "deploy/batocera/zz-robvision-game", SCRIPTS / "zz-robvision-game", 0o755)
    chosen = select_games(CONFIG, Path("/userdata/roms/nes"))
    subprocess.run(["batocera-services", "enable", "ROBVision"], check=True)
    subprocess.run(["batocera-services", "restart", "ROBVision"], check=True)
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
