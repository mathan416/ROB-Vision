"""Check installer edits without touching system services or game files."""

import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.install import (app_lab_status, configure_player2, copy_tree_merge, hook_event, install_uno, installed_controller, managed_text,
                             remove_legacy_hook, update_managed, valid_controller)


class InstallerTests(unittest.TestCase):
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

    def test_player2_migration_stays_above_retroarch_include(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "retroarch.cfg"
            path.write_text('input_player1_a_btn = "7"\ninput_player2_joypad_index = "1"\n'
                            '#include "/opt/retropie/configs/all/retroarch.cfg"\n')
            self.assertEqual(configure_player2(2, config=path), 2)
            text = path.read_text()
            self.assertEqual(text.count("input_player2_joypad_index"), 1)
            self.assertLess(text.index('input_player2_joypad_index = "2"'), text.index("#include"))
            self.assertIn('input_player1_a_btn = "7"', text)
            configure_player2(2, config=path)
            self.assertEqual(path.read_text(), text)

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

    def test_detects_virtual_pad_and_only_changes_nes_player2(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, name in ((0, "Player One"), (2, "R.O.B. Vision Controller 2")):
                device = root / "sys" / f"js{index}" / "device"
                device.mkdir(parents=True)
                (device / "name").write_text(name)
            config = root / "retroarch.cfg"
            config.write_text('input_player1_a_btn = "7"\n')
            self.assertEqual(configure_player2(sys_root=root / "sys", config=config), 2)
            self.assertIn('input_player1_a_btn = "7"', config.read_text())
            self.assertIn('input_player2_joypad_index = "2"', config.read_text())

    def test_player2_waits_for_receiver_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "retroarch.cfg"
            config.write_text("#include all.cfg\n")
            device = root / "sys/js1/device"
            def appear():
                device.mkdir(parents=True)
                (device / "name").write_text("R.O.B. Vision Controller 2\n")
            timer = threading.Timer(0.15, appear)
            timer.start()
            try:
                self.assertEqual(configure_player2(sys_root=root / "sys", config=config,
                                                   wait_seconds=1.0), 1)
            finally:
                timer.join()

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
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            destination = root / "ArduinoApps" / "rob-vision"
            for name in ("python", "sketch", "dashboard"):
                (source / name).mkdir(parents=True)
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
                 patch("scripts.install.wait_for_uno"):
                install_uno(source, destination)
                token = (destination / "data/controller-token").read_text()
                (destination / ".deps").mkdir()
                (destination / ".deps/bridge.txt").write_text("installed")
                (destination / ".cache").mkdir()
                (destination / ".cache/app-compose.yaml").write_text("generated")
                (source / "dashboard/index.html").write_text("<main>two</main>\n")
                install_uno(source, destination)
            self.assertEqual((destination / "data/controller-token").read_text(), token)
            self.assertEqual((destination / "dashboard/index.html").read_text(), "<main>two</main>\n")
            self.assertEqual((root / "ArduinoApps/rob-vision.previous/dashboard/index.html").read_text(),
                             "<main>one</main>\n")
            self.assertEqual((destination / "data/controller-token").stat().st_mode & 0o777, 0o600)
            self.assertTrue((destination / "data").is_dir())
            self.assertEqual((destination / ".deps/bridge.txt").read_text(), "installed")
            self.assertEqual((destination / ".cache/app-compose.yaml").read_text(), "generated")
            self.assertEqual(actions, ["start", "stop", "start"])

    def test_running_app_is_detected_from_app_lab(self):
        sample = '{"apps":[{"name":"R.O.B. Vision","status":"running"}]}'
        with patch("scripts.install.subprocess.run", return_value=SimpleNamespace(stdout=sample)):
            self.assertEqual(app_lab_status(), ("running", False))

    def test_failed_upgrade_restores_and_restarts_previous_app(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            destination = root / "ArduinoApps/rob-vision"
            for name in ("python", "sketch", "dashboard"):
                (source / name).mkdir(parents=True)
            (source / "app.yaml").write_text("name: R.O.B. Vision\n")
            (source / "python/main.py").write_text("pass\n")
            (source / "sketch/sketch.ino").write_text("// sketch\n")
            (source / "dashboard/index.html").write_text("new\n")
            destination.mkdir(parents=True)
            (destination / "dashboard").mkdir()
            (destination / "dashboard/index.html").write_text("old\n")
            actions = []
            starts = [False, True]
            def action(name, _path):
                actions.append(name)
                if name == "start" and not starts.pop(0):
                    raise RuntimeError("simulated App Lab start failure")
            with patch("scripts.install.sys.platform", "linux"), \
                 patch("scripts.install.os.geteuid", return_value=1000), \
                 patch("scripts.install.pwd.getpwuid", return_value=SimpleNamespace(pw_name="arduino")), \
                 patch("scripts.install.app_lab_status", return_value=("running", False)), \
                 patch("scripts.install.app_lab_action", side_effect=action), \
                 patch("scripts.install.wait_for_uno"):
                with self.assertRaisesRegex(RuntimeError, "previous app restored"):
                    install_uno(source, destination)
            self.assertEqual((destination / "dashboard/index.html").read_text(), "old\n")
            self.assertEqual(actions, ["stop", "start", "stop", "start"])


if __name__ == "__main__":
    unittest.main()
