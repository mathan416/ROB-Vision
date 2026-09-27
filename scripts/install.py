#!/usr/bin/env python3
"""Install R.O.B. Vision from a checked-out repository on the target device.

UNO Q: python3 scripts/install.py uno-q
RetroPie: sudo python3 scripts/install.py retropie --controller robvision.local
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import pwd
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen


SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from tools.identify_game import load_registry
from router_shared.retroarch_udev import retroarch_udev_event_nodes, retroarch_index_for_js
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


def copy_tree_merge(source: Path, destination: Path, preserve_registry: bool = False) -> None:
    for root, dirs, files in os.walk(source):
        dirs[:] = [name for name in dirs if name != "__pycache__" and not name.startswith("._")]
        target = destination / Path(root).relative_to(source)
        target.mkdir(parents=True, exist_ok=True)
        for name in files:
            if name.startswith("._") or name == ".DS_Store" or name.endswith((".pyc", ".pyo")):
                continue
            if preserve_registry and name == "games.json" and (target / name).is_file():
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
        previous_owner = path.stat() if path.exists() else None
        if original:
            backup = path.with_name(path.name + ".before-rob-vision")
            if not backup.exists():
                shutil.copy2(path, backup)
        write_file(path, changed, mode)
        if previous_owner is not None:
            os.chown(path, previous_owner.st_uid, previous_owner.st_gid)


def valid_controller(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]{0,252}", value):
        raise ValueError("Use a controller hostname or LAN IP address, without a scheme or port.")
    if value.startswith("-") or ".." in value:
        raise ValueError("Invalid controller hostname.")
    return value


def app_lab_status() -> tuple[str | None, bool]:
    result = subprocess.run(["arduino-app-cli", "app", "list", "--format", "json"],
                            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
    listing = json.loads(result.stdout)
    apps = listing.get("apps", [])
    status = next((app.get("status") for app in apps if app.get("name") == "R.O.B. Vision"), None)
    other_running = any(app.get("status") == "running" and app.get("name") != "R.O.B. Vision"
                        for app in apps)
    return status, other_running


def app_lab_action(action: str, destination: Path) -> None:
    run("arduino-app-cli", "app", action, str(destination))


def wait_for_uno(seconds: float = 30) -> None:
    deadline = time.monotonic() + seconds
    while True:
        try:
            with urlopen("http://127.0.0.1:8766/api/state", timeout=2) as response:
                if response.status == 200:
                    return
        except OSError:
            pass
        if time.monotonic() >= deadline:
            raise RuntimeError("App Lab started R.O.B. Vision, but its controller did not become ready.")
        time.sleep(0.5)


def uno_dashboard_urls(hostname: str, address_data: list[dict]) -> list[str]:
    """Return the mDNS URL and usable LAN IPv4 URLs for this UNO Q."""
    name = hostname.split(".", 1)[0].strip().lower()
    urls = [f"http://{name}.local/dashboard/"] if re.fullmatch(r"[a-z0-9][a-z0-9-]*", name) else []
    for interface in address_data:
        device = interface.get("ifname", "")
        if device.startswith(("docker", "br-", "veth", "virbr", "tun", "tap", "wg", "tailscale", "podman", "cni")):
            continue
        for address in interface.get("addr_info", []):
            if address.get("family") != "inet":
                continue
            try:
                ip = ipaddress.ip_address(address.get("local", ""))
            except ValueError:
                continue
            if ip.is_loopback or ip.is_link_local:
                continue
            url = f"http://{ip}/dashboard/"
            if url not in urls:
                urls.append(url)
    return urls


def print_uno_dashboard_urls() -> None:
    try:
        result = subprocess.run(["ip", "-j", "-4", "addr", "show", "up", "scope", "global"],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                universal_newlines=True)
        address_data = json.loads(result.stdout)
    except (OSError, subprocess.CalledProcessError, ValueError):
        address_data = []
    urls = uno_dashboard_urls(socket.gethostname(), address_data)
    if not urls:
        print("Open /dashboard/ on this UNO Q; check its hostname or LAN IP address.")
        return
    print("Open R.O.B. Vision on this network:")
    for url in urls:
        print(f"  Mission: {url}")
        print(f"  Setup:   {url}setup.html")


def install_uno(source: Path = SOURCE, destination: Path = UNO_DEST) -> None:
    if sys.version_info < (3, 9):
        raise RuntimeError("Python 3.9 or newer is required by the UNO Q controller.")
    if sys.platform != "linux" or os.geteuid() == 0 or pwd.getpwuid(os.geteuid()).pw_name != "arduino":
        raise RuntimeError("Run the UNO Q installer as the arduino user, without sudo.")
    if not destination.parent.is_dir():
        raise RuntimeError("ArduinoApps was not found. Install or enable UNO Q App Lab first.")
    if destination.is_symlink() or source.resolve() == destination.resolve():
        raise RuntimeError("Install from a separate checkout; the App Lab destination cannot be the source.")
    required_files = ["app.yaml", "python/main.py", "sketch/sketch.ino", "dashboard/index.html"]
    if (source / "app.yaml").is_file() and "local:avahi_resolver" in (source / "app.yaml").read_text():
        required_files.extend(("bricks/local/avahi_resolver/brick_config.yaml",
                               "bricks/local/avahi_resolver/brick_compose.yaml",
                               "scripts/avahi-resolver-service.py"))
    for required in required_files:
        if not (source / required).is_file():
            raise RuntimeError(f"Incomplete checkout: missing {required}")
    status, other_running = app_lab_status()
    if other_running:
        raise RuntimeError("Stop the other running App Lab app before installing R.O.B. Vision.")
    was_running = status == "running"
    backup = destination.with_name("rob-vision.previous")
    if backup.exists():
        backup = destination.with_name(f"rob-vision.previous-{os.getpid()}-{secrets.token_hex(3)}")
    replaced = False
    try:
        if was_running:
            print("Stopping R.O.B. Vision in App Lab.", flush=True)
            app_lab_action("stop", destination)
        # Stage a private sibling while the app is stopped, preserving its token and App Lab files.
        with tempfile.TemporaryDirectory(prefix=".rob-vision-stage-", dir=destination.parent) as directory:
            staged = Path(directory) / "rob-vision"
            staged.mkdir()
            shutil.copy2(source / "app.yaml", staged / "app.yaml")
            # Dashboard guides are already bundled under dashboard/guides.
            # Do not copy generated release archives into the running app.
            for name in ("controller", "python", "dashboard", "config", "tools", "sketch", "bricks"):
                if (source / name).exists():
                    shutil.copytree(source / name, staged / name,
                                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "._*"))
            if (source / "scripts/avahi-resolver-service.py").is_file():
                (staged / "scripts").mkdir(exist_ok=True)
                shutil.copy2(source / "scripts/avahi-resolver-service.py",
                             staged / "scripts/avahi-resolver-service.py")
            for name in ("data", ".deps", ".cache"):
                if (destination / name).is_dir():
                    shutil.copytree(destination / name, staged / name, symlinks=True,
                                    ignore=shutil.ignore_patterns(".avahi-resolver.sock") if name == "data" else None)
            data = staged / "data"
            data.mkdir(exist_ok=True)
            data.chmod(0o700)
            token = data / "controller-token"
            if not token.exists():
                write_file(token, secrets.token_urlsafe(48) + "\n", 0o600)
            else:
                token.chmod(0o600)
            if destination.exists():
                os.replace(destination, backup)
            try:
                os.replace(staged, destination)
            except Exception:
                if backup.exists():
                    os.replace(backup, destination)
                raise
            replaced = True
        print("Starting R.O.B. Vision in App Lab.", flush=True)
        app_lab_action("start", destination)
        wait_for_uno()
    except Exception as error:
        if replaced and backup.exists():
            try:
                app_lab_action("stop", destination)
            except (OSError, subprocess.CalledProcessError):
                pass
            failed = destination.with_name(f"rob-vision.failed-{os.getpid()}-{secrets.token_hex(3)}")
            os.replace(destination, failed)
            os.replace(backup, destination)
            if was_running:
                app_lab_action("start", destination)
                wait_for_uno()
            raise RuntimeError(f"Installation failed; previous app restored. Candidate retained at {failed}.") from error
        if was_running and destination.exists():
            if app_lab_status()[0] != "running":
                app_lab_action("start", destination)
                wait_for_uno()
        raise
    print(f"UNO Q app installed and running at {destination}")
    if backup.exists():
        print(f"Previous app retained at {backup}; remove it after checking the new app.")
    print_uno_dashboard_urls()


def pi_owned(path: Path, user: str = "pi") -> None:
    account = pwd.getpwnam(user)
    for root, dirs, files in os.walk(path):
        os.chown(root, account.pw_uid, account.pw_gid)
        for name in dirs + files:
            os.chown(os.path.join(root, name), account.pw_uid, account.pw_gid)


def installed_controller(path: Path = PI_CONFIG / "receiver.env") -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text().splitlines():
        if line.startswith("ROB_VISION_URL=http://"):
            return line[len("ROB_VISION_URL=http://"):]
    return None


def validate_receiver_source(source: Path) -> None:
    """Reject an incomplete source bundle before stopping the installed receiver."""
    result = subprocess.run(
        [sys.executable, str(source / "tools/retropie_controller2.py"), "--help"],
        cwd=source, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
    )
    if result.returncode:
        detail = (result.stderr.strip().splitlines() or ["import failed"])[-1]
        raise RuntimeError("Incomplete receiver module set: " + detail)


def install_retropie(source: Path = SOURCE, destination: Path = PI_DEST,
                     controller: str | None = None) -> None:
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
    if any(not (source / "deploy/retropie/router" /
                f"VirtualGlove Merged Player {player}.cfg").is_file()
           for player in range(1, 5)):
        raise RuntimeError("Incomplete checkout: Controller Router profiles are missing.")
    cores = [name for name, path in CORE_PATHS.items() if path.is_file()]
    if not cores:
        raise RuntimeError("Install lr-fceumm or lr-nestopia through RetroPie-Setup first.")
    if subprocess.run(["pgrep", "-x", "retroarch"], stdout=subprocess.DEVNULL).returncode == 0:
        raise RuntimeError("Exit the running NES game before installing or upgrading.")
    if any(subprocess.run(["pgrep", "-x", name], stdout=subprocess.DEVNULL).returncode == 0
           for name in ("emulationstation", "emulationstatio")):
        raise RuntimeError("Exit EmulationStation before installing; restarting the virtual joystick while it runs can crash its input manager.")
    validate_receiver_source(source)
    load_registry(destination / "config/games.json" if (destination / "config/games.json").is_file()
                  else source / "config/games.json")
    for action in ("launch", "end"):
        hook = RUNCOMMAND / f"runcommand-on{action}.sh"
        if hook.exists():
            managed_text(remove_legacy_hook(hook.read_text(), hook_event(action)),
                         "true", "#!/bin/sh")
    managed_text(NES_CONFIG.read_text(), 'input_libretro_device_p2 = "1"')
    run("modprobe", "uinput")
    if not Path("/dev/uinput").exists():
        raise RuntimeError("/dev/uinput is unavailable after loading the uinput module.")
    # Avoid loading a mixed module set if an earlier update was interrupted.
    if SERVICE.exists():
        run("systemctl", "stop", "rob-vision-controller2.service")
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("tools", "controller", "config", "scripts", "router_shared"):
        copy_tree_merge(source / name, destination / name, preserve_registry=(name == "config"))
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
    Path("/etc/virtualglove").mkdir(mode=0o755, parents=True, exist_ok=True)
    copy_file(source / "deploy/retropie/rob-vision-controller2.service", SERVICE)
    shared_unit = Path("/etc/systemd/system/virtualglove-controller-router.service")
    if not shared_unit.exists():
        copy_file(source / "deploy/retropie/virtualglove-controller-router.service", shared_unit)
    override = Path("/etc/systemd/system/virtualglove-controller-router.service.d/rob-vision.conf")
    copy_file(source / "deploy/retropie/rob-vision-router.conf", override)
    copy_file(source / "deploy/retropie/retroarch-joypad.cfg",
              Path("/opt/retropie/configs/all/retroarch/autoconfig/udev/R.O.B. Vision Controller 2.cfg"))
    for profile in (source / "deploy/retropie/router").glob("VirtualGlove Merged Player *.cfg"):
        target = Path("/opt/retropie/configs/all/retroarch/autoconfig/udev") / profile.name
        if not target.exists():
            copy_file(profile, target)
            account = pwd.getpwnam("pi")
            os.chown(target, account.pw_uid, account.pw_gid)
    # Older releases placed this profile where RetroArch's udev driver does
    # not search. Retire those project-owned copies during an upgrade.
    unlink_if_exists(Path("/opt/retropie/configs/all/retroarch-joypads/R.O.B. Vision Controller 2.cfg"))
    unlink_if_exists(Path("/opt/retropie/configs/all/retroarch/autoconfig/R.O.B. Vision Controller 2.cfg"))
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
    install(Path("/opt/retropie/configs"), registry_path=destination / "config/games.json")
    run("systemctl", "daemon-reload")
    token = PI_CONFIG / "token"
    run("systemctl", "enable", "rob-vision-controller2.service")
    if token.exists():
        run("systemctl", "restart", "rob-vision-controller2.service")
        from tools.controller_router_setup import activate
        activate("retropie")
        print("Controller Router assigns Buddy to Player 2.")
        print("Receiver restarted. Open Setup on the UNO Q and select Check Link.")
    else:
        print("Receiver installed and will start automatically when pairing completes.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="target", required=True)
    sub.add_parser("uno-q", help="Install the UNO Q App Lab app as arduino")
    retro = sub.add_parser("retropie", help="Install the receiver and frame choices as root")
    retro.add_argument("--controller", help="UNO Q LAN hostname or IP; retained on upgrades")
    args = parser.parse_args()
    try:
        if args.target == "uno-q":
            install_uno()
        elif args.target == "retropie":
            install_retropie(controller=args.controller)
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Installation stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
