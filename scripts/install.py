#!/usr/bin/env python3
"""Install R.O.B. Vision from a checked-out repository on the target device.

UNO Q: python3 scripts/install.py uno-q
RetroPie: sudo python3 scripts/install.py retropie --controller robvision.local
"""

from __future__ import annotations

import argparse
import os
import pwd
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
BEGIN = "# BEGIN R.O.B. Vision (managed by installer)"
END = "# END R.O.B. Vision (managed by installer)"
UNO_DEST = Path("/home/arduino/ArduinoApps/rob-vision")
PI_DEST = Path("/home/pi/rob-vision")
PI_CONFIG = Path("/home/pi/.config/rob-vision")
RUNCOMMAND = Path("/opt/retropie/configs/all")
NES_CONFIG = Path("/opt/retropie/configs/nes/retroarch.cfg")
SERVICE = Path("/etc/systemd/system/rob-vision-controller2.service")
CORE_PATHS = {
    "fceumm": Path("/opt/retropie/libretrocores/lr-fceumm/fceumm_libretro.so"),
    "nestopia": Path("/opt/retropie/libretrocores/lr-nestopia/nestopia_libretro.so"),
}


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def unlink_if_exists(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def copy_tree_merge(source: Path, destination: Path) -> None:
    for root, dirs, files in os.walk(source):
        dirs[:] = [name for name in dirs if name != "__pycache__" and not name.startswith("._")]
        target = destination / Path(root).relative_to(source)
        target.mkdir(parents=True, exist_ok=True)
        for name in files:
            if name.startswith("._") or name == ".DS_Store" or name.endswith((".pyc", ".pyo")):
                continue
            copy_file(Path(root) / name, target / name)


def copy_file(source: Path, destination: Path, mode: int | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".rob-vision-", delete=False) as file:
        temporary = Path(file.name)
    try:
        shutil.copy2(source, temporary)
        if mode is not None:
            temporary.chmod(mode)
        os.replace(temporary, destination)
    finally:
        unlink_if_exists(temporary)


def write_file(destination: Path, content: str, mode: int = 0o644) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                                     prefix=".rob-vision-", delete=False) as file:
        file.write(content)
        temporary = Path(file.name)
    try:
        temporary.chmod(mode)
        os.replace(temporary, destination)
    finally:
        unlink_if_exists(temporary)


def managed_text(existing: str, body: str, shebang: str | None = None,
                 before_include: bool = False) -> str:
    """Replace only our marked section and leave other projects' hooks intact."""
    if existing.count(BEGIN) != existing.count(END) or existing.count(BEGIN) > 1:
        raise ValueError("The existing R.O.B. Vision managed section is damaged; inspect it manually.")
    if BEGIN in existing:
        start = existing.index(BEGIN)
        finish = existing.index(END, start) + len(END)
        existing = existing[:start] + existing[finish:]
    if shebang and not existing.strip():
        existing = shebang + "\n"
    section = BEGIN + "\n" + body.rstrip() + "\n" + END + "\n"
    if shebang:
        lines = existing.splitlines(keepends=True)
        if lines and lines[0].startswith("#!"):
            return lines[0] + section + "".join(lines[1:]).lstrip("\n")
        return shebang + "\n" + section + existing.lstrip("\n")
    if before_include:
        match = re.search(r"(?m)^#include\b", existing)
        if match:
            return existing[:match.start()].rstrip() + "\n" + section + existing[match.start():]
    return existing.rstrip() + "\n" + section


def remove_legacy_hook(existing: str, action: str) -> str:
    """Upgrade the original standalone notification hook without running it twice."""
    if BEGIN in existing or "notify_game.py" not in existing:
        return existing
    pattern = (r"(?m)^ROB_VISION_URL=[^\n]*\\\n"
               r"ROB_VISION_TOKEN_FILE=[^\n]*\\\n"
               r"[ \t]*/usr/bin/python3 /home/pi/rob-vision/tools/notify_game\.py "
               + re.escape(action) + r' "\$@" >/dev/null \|\| :\n?')
    cleaned, count = re.subn(pattern, "", existing)
    if count != 1 or "notify_game.py" in cleaned:
        raise ValueError("An existing R.O.B. Vision launch hook needs manual review before installing.")
    return cleaned


def hook_event(action: str) -> str:
    return {"launch": "start", "end": "end"}[action]


def update_managed(path: Path, body: str, shebang: str | None = None,
                   mode: int = 0o644, legacy_action: str | None = None,
                   before_include: bool = False, remove_player2: bool = False) -> None:
    original = path.read_text() if path.exists() else ""
    prepared = remove_legacy_hook(original, legacy_action) if legacy_action else original
    if remove_player2 and BEGIN not in prepared:
        keys = ("input_libretro_device_p2", "input_player2_joypad_index",
                "input_player2_a_btn", "input_player2_b_btn")
        prepared = "".join(line for line in prepared.splitlines(keepends=True)
                           if not any(re.match(r"\s*" + key + r"\s*=", line) for key in keys))
    changed = managed_text(prepared, body, shebang, before_include)
    if changed != original:
        if original:
            backup = path.with_name(path.name + ".before-rob-vision")
            if not backup.exists():
                shutil.copy2(path, backup)
        write_file(path, changed, mode)


def valid_controller(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]{0,252}", value):
        raise ValueError("Use a controller hostname or LAN IP address, without a scheme or port.")
    if value.startswith("-") or ".." in value:
        raise ValueError("Invalid controller hostname.")
    return value


def install_uno(source: Path = SOURCE, destination: Path = UNO_DEST) -> None:
    if sys.version_info < (3, 9):
        raise RuntimeError("Python 3.9 or newer is required by the UNO Q controller.")
    if sys.platform != "linux" or os.geteuid() == 0 or pwd.getpwuid(os.geteuid()).pw_name != "arduino":
        raise RuntimeError("Run the UNO Q installer as the arduino user, without sudo.")
    if not destination.parent.is_dir():
        raise RuntimeError("ArduinoApps was not found. Install or enable UNO Q App Lab first.")
    if destination.is_symlink() or source.resolve() == destination.resolve():
        raise RuntimeError("Install from a separate checkout; the App Lab destination cannot be the source.")
    for required in ("app.yaml", "python/main.py", "sketch/sketch.ino", "dashboard/index.html"):
        if not (source / required).is_file():
            raise RuntimeError(f"Incomplete checkout: missing {required}")
    # A private sibling is staged before replacing the App Lab app. Preserve its token.
    with tempfile.TemporaryDirectory(prefix=".rob-vision-stage-", dir=destination.parent) as directory:
        staged = Path(directory) / "rob-vision"
        staged.mkdir()
        for name in ("app.yaml",):
            shutil.copy2(source / name, staged / name)
        for name in ("controller", "python", "dashboard", "config", "tools", "sketch", "docs", "output"):
            if (source / name).exists():
                shutil.copytree(source / name, staged / name,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "._*"))
        data = staged / "data"
        if (destination / "data").is_dir():
            shutil.copytree(destination / "data", data)
        else:
            data.mkdir()
        data.chmod(0o700)
        token = data / "controller-token"
        if not token.exists():
            write_file(token, secrets.token_urlsafe(48) + "\n", 0o600)
        else:
            token.chmod(0o600)
        backup = destination.with_name("rob-vision.previous")
        if backup.exists():
            backup = destination.with_name(f"rob-vision.previous-{os.getpid()}-{secrets.token_hex(3)}")
        if destination.exists():
            os.replace(destination, backup)
        try:
            os.replace(staged, destination)
        except Exception:
            if backup.exists():
                os.replace(backup, destination)
            raise
    print(f"UNO Q app installed at {destination}")
    if backup.exists():
        print(f"Previous app retained at {backup}; remove it after checking the new app.")
    print("Start R.O.B. Vision in App Lab, then open /dashboard/setup.html on your UNO Q.")


def pi_owned(path: Path, user: str = "pi") -> None:
    account = pwd.getpwnam(user)
    for root, dirs, files in os.walk(path):
        os.chown(root, account.pw_uid, account.pw_gid)
        for name in dirs + files:
            os.chown(os.path.join(root, name), account.pw_uid, account.pw_gid)


def configure_player2(index: int | None = None, sys_root: Path = Path("/sys/class/input"),
                      config: Path = NES_CONFIG, wait_seconds: float = 5.0) -> int:
    if index is None:
        deadline = time.monotonic() + wait_seconds
        while True:
            matches = []
            for path in sys_root.glob("js*/device/name"):
                try:
                    if path.read_text().strip() == "R.O.B. Vision Controller 2":
                        matches.append(int(path.parents[1].name[2:]))
                except FileNotFoundError:
                    continue  # A joystick may disappear during receiver restart.
            if len(matches) == 1:
                index = matches[0]
                break
            if len(matches) > 1 or time.monotonic() >= deadline:
                raise RuntimeError("Start the paired receiver, then retry; one R.O.B. Vision virtual pad must be visible.")
            time.sleep(0.1)
    if not 0 <= index <= 15:
        raise ValueError("Player 2 joystick index must be between 0 and 15.")
    if not config.is_file():
        raise RuntimeError(f"NES RetroArch configuration is missing: {config}")
    update_managed(config, '\n'.join((
        'input_libretro_device_p2 = "1"',
        f'input_player2_joypad_index = "{index}"',
        'input_player2_a_btn = "1"',
        'input_player2_b_btn = "0"',
    )), before_include=True, remove_player2=True)
    return index


def installed_controller(path: Path = PI_CONFIG / "receiver.env") -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text().splitlines():
        if line.startswith("ROB_VISION_URL=http://"):
            return line[len("ROB_VISION_URL=http://"):]
    return None


def install_retropie(source: Path = SOURCE, destination: Path = PI_DEST,
                     controller: str | None = None, player2_index: int | None = None) -> None:
    if sys.version_info < (3, 7):
        raise RuntimeError("Python 3.7 or newer is required by the RetroPie receiver.")
    if sys.platform != "linux" or os.geteuid() != 0:
        raise RuntimeError("Run the RetroPie installer with sudo on the RetroPie machine.")
    controller = controller or installed_controller()
    if not controller:
        raise ValueError("Provide --controller with the UNO Q LAN hostname or IP on first installation.")
    valid_controller(controller)
    if destination.is_symlink() or source.resolve() == destination.resolve():
        raise RuntimeError("Install from a separate checkout; the RetroPie destination cannot be the source.")
    pwd.getpwnam("pi")
    if not RUNCOMMAND.is_dir() or not NES_CONFIG.is_file():
        raise RuntimeError("Standard RetroPie configuration is missing under /opt/retropie/configs.")
    if any(not shutil.which(command) for command in ("gcc", "systemctl", "modprobe", "openssl")):
        raise RuntimeError("gcc, systemctl, modprobe, and openssl are required. Install missing tools and retry.")
    if not (source / "deploy/retropie/rob_vision_fceumm_proxy.c").is_file():
        raise RuntimeError("Incomplete checkout: frame proxy source is missing.")
    cores = [name for name, path in CORE_PATHS.items() if path.is_file()]
    if not cores:
        raise RuntimeError("Install lr-fceumm or lr-nestopia through RetroPie-Setup first.")
    if subprocess.run(["pgrep", "-x", "retroarch"], stdout=subprocess.DEVNULL).returncode == 0:
        raise RuntimeError("Exit the running NES game before installing or upgrading.")
    for action in ("launch", "end"):
        hook = RUNCOMMAND / f"runcommand-on{action}.sh"
        if hook.exists():
            managed_text(remove_legacy_hook(hook.read_text(), hook_event(action)),
                         "true", "#!/bin/sh")
    managed_text(NES_CONFIG.read_text(), 'input_libretro_device_p2 = "1"')
    run("modprobe", "uinput")
    if not Path("/dev/uinput").exists():
        raise RuntimeError("/dev/uinput is unavailable after loading the uinput module.")
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("tools", "controller", "config"):
        copy_tree_merge(source / name, destination / name)
    build = destination / "build"
    build.mkdir(exist_ok=True)
    proxy_source = source / "deploy/retropie/rob_vision_fceumm_proxy.c"
    for name in cores:
        output = build / f"rob_vision_{name}_libretro.so"
        with tempfile.NamedTemporaryFile(dir=build, suffix=".so", delete=False) as file:
            temporary = Path(file.name)
        try:
            command = ["gcc", "-std=gnu11", "-O2", "-fPIC", "-shared", "-Wall", "-Wextra"]
            if name == "nestopia":
                command.append("-DROB_USE_NESTOPIA")
            run(*command, "-o", str(temporary), str(proxy_source), "-ldl")
            temporary.chmod(0o755)
            os.replace(temporary, output)
        finally:
            unlink_if_exists(temporary)
    pi_owned(destination)
    PI_CONFIG.mkdir(mode=0o700, parents=True, exist_ok=True)
    PI_CONFIG.chmod(0o700)
    env = PI_CONFIG / "receiver.env"
    write_file(env, f"ROB_VISION_URL=http://{controller}\n"
                    "ROB_VISION_TOKEN_FILE=/home/pi/.config/rob-vision/token\n", 0o600)
    pi_owned(PI_CONFIG)
    write_file(Path("/etc/modules-load.d/rob-vision.conf"), "uinput\n")
    copy_file(source / "deploy/retropie/rob-vision-controller2.service", SERVICE)
    for action in ("launch", "end"):
        target = RUNCOMMAND / f"runcommand-on{action}.sh"
        body = ("/bin/sh /home/pi/rob-vision/deploy/retropie/"
                f"runcommand-on{action}.sh \"$@\" || :")
        update_managed(target, body, "#!/bin/sh", 0o755,
                       legacy_action=hook_event(action))
    (destination / "deploy/retropie").mkdir(parents=True, exist_ok=True)
    for action in ("launch", "end"):
        copy_file(source / f"deploy/retropie/runcommand-on{action}.sh",
                  destination / f"deploy/retropie/runcommand-on{action}.sh", 0o755)
    pi_owned(destination)
    # Reuse the existing selective installer: only the two registered games get wrappers.
    from tools.install_retropie_frame_hook import install
    install(Path("/opt/retropie/configs"))
    if player2_index is not None:
        configure_player2(player2_index)
    run("systemctl", "daemon-reload")
    token = PI_CONFIG / "token"
    if token.exists():
        run("systemctl", "enable", "rob-vision-controller2.service")
        run("systemctl", "restart", "rob-vision-controller2.service")
        print("Receiver restarted. Open Setup on the UNO Q and select Check Link.")
    else:
        print("Receiver installed but awaiting pairing. Run as pi:")
        print("  python3 /home/pi/rob-vision/tools/retropie_pair.py")
        print("Enter the code and fingerprint on the UNO Q Setup page, then run:")
        print("  sudo systemctl enable --now rob-vision-controller2.service")
    if player2_index is None:
        print("After pairing, run: sudo python3 scripts/install.py player2")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="target", required=True)
    sub.add_parser("uno-q", help="Install the UNO Q App Lab app as arduino")
    retro = sub.add_parser("retropie", help="Install the receiver and frame choices as root")
    retro.add_argument("--controller", help="UNO Q LAN hostname or IP; retained on upgrades")
    retro.add_argument("--player2-index", type=int, help="RetroArch joystick index for virtual Controller 2")
    sub.add_parser("player2", help="Detect the running virtual pad and configure NES Controller 2")
    args = parser.parse_args()
    try:
        if args.target == "uno-q":
            install_uno()
        elif args.target == "retropie":
            install_retropie(controller=args.controller, player2_index=args.player2_index)
        else:
            if os.geteuid() != 0:
                raise RuntimeError("Run this configuration step with sudo on RetroPie.")
            index = configure_player2()
            print(f"NES Controller 2 mapped to R.O.B. Vision joystick {index}. Restart the game to apply it.")
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Installation stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
