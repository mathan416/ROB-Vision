"""Check installer edits without touching system services or game files."""

import tempfile
import os
import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.install import (app_lab_status, copy_tree_merge, hook_event, install_uno, installed_controller, managed_text,
                             retroarch_index_for_js,
                             uno_dashboard_urls,
                             remove_legacy_hook, update_managed, valid_controller)
from scripts.install import validate_receiver_source


class InstallerTests(unittest.TestCase):
    def test_uno_urls_show_mdns_and_lan_addresses_without_container_bridges(self):
        interfaces = [
            {"ifname": "eth0", "addr_info": [{"family": "inet", "local": "10.0.2.84"}]},
            {"ifname": "wlan0", "addr_info": [{"family": "inet", "local": "10.0.2.86"}]},
            {"ifname": "docker0", "addr_info": [{"family": "inet", "local": "172.17.0.1"}]},
        ]
        self.assertEqual(uno_dashboard_urls("virtualglove", interfaces), [
            "http://virtualglove.local:8101/dashboard/",
            "http://10.0.2.84:8101/dashboard/",
            "http://10.0.2.86:8101/dashboard/",
        ])

    def test_receiver_source_is_importable_before_installation(self):
        validate_receiver_source(Path(__file__).resolve().parents[1])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tools = root / "tools"
            tools.mkdir()
            (tools / "__init__.py").touch()
            (tools / "retropie_frame_hook.py").write_text("# incomplete older module\n")
            (tools / "retropie_controller2.py").write_text(
                "from tools.retropie_frame_hook import BATOCERA_CONFIG\n")
            with self.assertRaisesRegex(RuntimeError, "Incomplete receiver module set"):
                validate_receiver_source(root)

    def test_hook_is_idempotent_and_runs_before_other_hook_code(self):
        old = "#!/bin/sh\necho existing\nexit 0\n"
        installed = managed_text(old, "echo rob", "#!/bin/sh")
        self.assertLess(installed.index("echo rob"), installed.index("echo existing"))
        self.assertEqual(managed_text(installed, "echo rob", "#!/bin/sh"), installed)
        self.assertIn("exit 0", installed)

    def test_migrates_original_standalone_hook_once(self):
        old = ('#!/bin/sh\n# existing comment\nROB_VISION_URL=http://arduiain.local \\\n'
               'ROB_VISION_TOKEN_FILE=/home/pi/.config/rob-vision/token \\\n'
               '    /usr/bin/python3 /home/pi/rob-vision/tools/notify_game.py start "$@" >/dev/null || :\n')
        self.assertEqual(hook_event("launch"), "start")
        cleaned = remove_legacy_hook(old, hook_event("launch"))
        self.assertNotIn("notify_game.py", cleaned)
        self.assertIn("# existing comment", cleaned)
        with self.assertRaises(ValueError):
            remove_legacy_hook(old + "echo notify_game.py\n", "start")

    def test_config_keeps_existing_values_and_creates_one_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "retroarch.cfg"
            path.write_text('input_player1_a_btn = "0"\n#include "../all/retroarch.cfg"\n')
            update_managed(path, 'input_player2_a_btn = "1"')
            first = path.read_text()
            update_managed(path, 'input_player2_a_btn = "1"')
            self.assertEqual(path.read_text(), first)
            self.assertTrue((path.parent / "retroarch.cfg.before-rob-vision").exists())
            self.assertLess(first.index("#include"), first.index("input_player2_a_btn"))

    def test_managed_config_update_preserves_existing_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "retroarch.cfg"
            path.write_text('#include "all/retroarch.cfg"\n')
            owner = (path.stat().st_uid, path.stat().st_gid)
            update_managed(path, 'input_player2_a_btn = "1"', before_include=True)
            self.assertEqual((path.stat().st_uid, path.stat().st_gid), owner)

    def test_damaged_section_and_bad_hostname_are_rejected(self):
        with self.assertRaises(ValueError):
            managed_text("# BEGIN R.O.B. Vision (managed by installer)\n", "echo rob")
        for value in ("http://controller.local", "bad host", "-host", "a..b", "host:8766"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                valid_controller(value)
        self.assertEqual(valid_controller("robvision.local"), "robvision.local")
        with tempfile.TemporaryDirectory() as directory:
            env = Path(directory) / "receiver.env"
            self.assertIsNone(installed_controller(env))
            env.write_text("ROB_VISION_URL=http://robvision.local\n")
            self.assertEqual(installed_controller(env), "robvision.local")
            env.write_text("ROB_VISION_URL=http://robvision.local:8766\n")
            self.assertEqual(installed_controller(env), "robvision.local")
            env.write_text("ROB_VISION_URL=http://robvision.local:8101\n")
            self.assertEqual(installed_controller(env), "robvision.local")

    def test_retroarch_udev_index_can_differ_from_js_number(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            joystick = root / "js5/device"
            joystick.mkdir(parents=True)
            event = root / "event6/device"
            event.parent.mkdir()
            event.symlink_to(joystick)
            events = [f"/dev/input/event{number}" for number in (0, 4, 15, 16, 6)]
            self.assertEqual(retroarch_index_for_js(5, root, events), 4)

    def test_source_copy_ignores_macos_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "module.py").write_text("pass\n")
            (source / "._module.py").write_bytes(b"\0\0")
            (source / ".DS_Store").write_bytes(b"junk")
            target = root / "target"
            copy_tree_merge(source, target)
            self.assertTrue((target / "module.py").exists())
            self.assertFalse((target / "._module.py").exists())
            self.assertFalse((target / ".DS_Store").exists())

    def test_uno_stages_app_and_preserves_private_token_on_upgrade(self):
        with tempfile.TemporaryDirectory(prefix="rv-", dir="/tmp") as directory:
            root = Path(directory)
            source = root / "source"
            destination = root / "ArduinoApps" / "rob-vision"
            for name in ("python", "sketch", "dashboard", "matrix", "controller_router_portal/app/sketch"):
                (source / name).mkdir(parents=True)
            (source / "controller_router_portal/install.py").write_text("pass\n")
            (source / "controller_router_portal/client.py").write_text("# Router client\n")
            (source / "controller_router_portal/app/sketch/sketch.ino").write_text("// router\n")
            (source / "matrix/manifest.json").write_text("{}\n")
            (source / "app.yaml").write_text("name: R.O.B. Vision\n")
            (source / "python/main.py").write_text("pass\n")
            (source / "sketch/sketch.ino").write_text("// sketch\n")
            (source / "dashboard/index.html").write_text("<main>one</main>\n")
            destination.parent.mkdir()
            actions = []
            with patch("scripts.install.sys.platform", "linux"), \
                 patch("scripts.install.os.geteuid", return_value=1000), \
                 patch("scripts.install.pwd.getpwuid", return_value=SimpleNamespace(pw_name="arduino")), \
                 patch("scripts.install.app_lab_status", side_effect=[(None, False), ("running", False)]), \
                 patch("scripts.install.app_lab_action", side_effect=lambda action, _path: actions.append(action)), \
                 patch("scripts.install.wait_for_uno"), \
                 patch("scripts.install.print_uno_dashboard_urls"), \
                 patch("scripts.install.subprocess.run"):
                install_uno(source, destination)
                token = (destination / "data/controller-token").read_text()
                paired = '{"schema":1,"consoles":[{"id":"saved-console"}]}'
                (destination / "data/paired-consoles.json").write_text(paired)
                (destination / ".deps").mkdir()
                (destination / ".deps/bridge.txt").write_text("installed")
                (destination / ".cache").mkdir()
                (destination / ".cache/app-compose.yaml").write_text("generated")
                (source / "dashboard/index.html").write_text("<main>two</main>\n")
                os.mkfifo(destination / "data/.avahi-resolver.sock")
                install_uno(source, destination)
            self.assertEqual((destination / "data/controller-token").read_text(), token)
            self.assertEqual((destination / "data/paired-consoles.json").read_text(), paired)
            self.assertEqual((destination / "dashboard/index.html").read_text(), "<main>two</main>\n")
            self.assertTrue((destination / "controller_router_portal/client.py").is_file())
            self.assertEqual((root / "ArduinoApps/rob-vision.previous/dashboard/index.html").read_text(),
                             "<main>one</main>\n")
            self.assertEqual((destination / "data/controller-token").stat().st_mode & 0o777, 0o600)
            self.assertTrue((destination / "data").is_dir())
            self.assertFalse((destination / "data/.avahi-resolver.sock").exists())
            self.assertEqual((destination / ".deps/bridge.txt").read_text(), "installed")
            self.assertEqual((destination / ".cache/app-compose.yaml").read_text(), "generated")
            self.assertEqual(actions, ["stop"])

    def test_running_app_is_detected_from_app_lab(self):
        sample = '{"apps":[{"name":"R.O.B. Vision","status":"running"}]}'
        with patch("scripts.install.subprocess.run", return_value=SimpleNamespace(stdout=sample)):
            self.assertEqual(app_lab_status(), ("running", False))

    def test_failed_upgrade_restores_and_restarts_previous_app(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            destination = root / "ArduinoApps/rob-vision"
            for name in ("python", "sketch", "dashboard", "matrix", "controller_router_portal/app/sketch"):
                (source / name).mkdir(parents=True)
            (source / "controller_router_portal/install.py").write_text("pass\n")
            (source / "controller_router_portal/app/sketch/sketch.ino").write_text("// router\n")
            (source / "matrix/manifest.json").write_text("{}\n")
            (source / "app.yaml").write_text("name: R.O.B. Vision\n")
            (source / "python/main.py").write_text("pass\n")
            (source / "sketch/sketch.ino").write_text("// sketch\n")
            (source / "dashboard/index.html").write_text("new\n")
            destination.mkdir(parents=True)
            (destination / "dashboard").mkdir()
            (destination / "dashboard/index.html").write_text("old\n")
            actions = []
            def action(name, _path):
                actions.append(name)
            real_run = subprocess.run
            def run(command, *args, **kwargs):
                if isinstance(command, list) and command and str(command[-1]).endswith("controller_router_portal/install.py"):
                    raise RuntimeError("simulated shared Router startup failure")
                return real_run(command, *args, **kwargs)
            with patch("scripts.install.sys.platform", "linux"), \
                 patch("scripts.install.os.geteuid", return_value=1000), \
                 patch("scripts.install.pwd.getpwuid", return_value=SimpleNamespace(pw_name="arduino")), \
                 patch("scripts.install.app_lab_status", return_value=("running", False)), \
                 patch("scripts.install.app_lab_action", side_effect=action), \
                 patch("scripts.install.wait_for_uno"), \
                 patch("scripts.install.subprocess.run", side_effect=run):
                with self.assertRaisesRegex(RuntimeError, "previous app restored"):
                    install_uno(source, destination)
            self.assertEqual((destination / "dashboard/index.html").read_text(), "old\n")
            self.assertEqual(actions, ["stop", "stop", "start"])


if __name__ == "__main__":
    unittest.main()
