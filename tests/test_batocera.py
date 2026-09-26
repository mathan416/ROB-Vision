import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from identify_game import load_registry
from retropie_controller2 import running_game
from tools.batocera import configure_player2_overrides, map_player2, pad_index, select_games
from scripts.install_batocera import supported_hardware, suspend_menu, resume_menu
from tools.retropie_frame_hook import sender_game


class BatoceraTests(unittest.TestCase):
    def test_pad_index_uses_joystick_order_not_js_device_number(self):
        sdl = MagicMock()
        sdl.SDL_Init.return_value = 0
        sdl.SDL_NumJoysticks.return_value = 3
        sdl.SDL_JoystickNameForIndex.side_effect = [
            b"Atari Game Controller", b"virtual spinner", b"R.O.B. Vision Controller 2"
        ]
        with patch("tools.batocera.ctypes.CDLL", return_value=sdl):
            self.assertEqual(pad_index(), 2)
        sdl.SDL_QuitSubSystem.assert_called_once_with(0x200)

    def test_menu_is_suspended_before_receiver_hotplug_and_resumed(self):
        with tempfile.TemporaryDirectory() as directory:
            service = Path(directory) / "S31emulationstation"
            service.touch()
            results = [subprocess.CompletedProcess([], 0) for _ in range(2)]
            results.extend([subprocess.CompletedProcess([], 1) for _ in range(2)])
            results.append(subprocess.CompletedProcess([], 0))
            with patch("scripts.install_batocera.ES_SERVICE", service), patch(
                "scripts.install_batocera.subprocess.run", side_effect=results
            ) as run:
                self.assertTrue(suspend_menu())
                resume_menu()
            self.assertEqual([call.args[0] for call in run.call_args_list], [
                ["pidof", "emulationstation"], [str(service), "suspend"],
                ["pidof", "emulationstation"], ["pidof", "emulationstation"],
                [str(service), "resume"],
            ])

    def test_resume_skips_fifo_when_menu_already_restarted(self):
        with patch("scripts.install_batocera.subprocess.run", return_value=subprocess.CompletedProcess([], 0)) as run, patch(
            "scripts.install_batocera.Path.unlink"
        ) as unlink:
            resume_menu()
        run.assert_called_once_with(["pidof", "emulationstation"], stdout=subprocess.DEVNULL)
        unlink.assert_called_once_with(missing_ok=True)

    def test_hardware_gate_precedes_installation(self):
        with tempfile.TemporaryDirectory() as directory:
            version = Path(directory) / "batocera.version"
            version.write_text("43.1 2026/09/01 12:00\n")
            supported_hardware("x86_64", version)
            for machine, value in (("aarch64", "43.1"), ("x86_64", "44")):
                version.write_text(value + " 2026/09/01\n")
                with self.subTest(machine=machine, version=value), self.assertRaises(RuntimeError):
                    supported_hardware(machine, version)

    def test_select_only_registered_roms_and_preserve_virtualglove(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "batocera.conf"
            config.write_text('system.services=VirtualGlove\n'
                              'nes["Super Glove Ball (USA).7z"].core=nestopia_powerglove\n'
                              'nes["Stack-Up (World).zip"].core=nestopia\n')
            roms = root / "roms"
            roms.mkdir()
            for name in ("Gyromite (World).zip", "Stack-Up (World).zip", "Other.nes"):
                (roms / name).touch()
            self.assertEqual(select_games(config, roms),
                             ["Gyromite (World).zip", "Stack-Up (World).zip"])
            first = config.read_text()
            self.assertIn('nes["Stack-Up (World).zip"].core=robvision_nestopia', first)
            self.assertIn('nes["Super Glove Ball (USA).7z"].core=nestopia_powerglove', first)
            self.assertNotIn('Other.nes', first)
            select_games(config, roms)
            self.assertEqual(config.read_text(), first)

    def test_player2_changes_only_its_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "retroarchcustom.cfg"
            config.write_text('input_player1_a_btn = "4"\ninput_player2_joypad_index = 1\n')
            self.assertEqual(map_player2(config, 3), 3)
            first = config.read_text()
            self.assertIn('input_player1_a_btn = "4"', first)
            self.assertIn('input_player2_joypad_index = "3"', first)
            map_player2(config, 3)
            self.assertEqual(config.read_text(), first)

    def test_persistent_gyromite_p2_overrides_do_not_touch_stackup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            roms = root / "roms"
            roms.mkdir()
            (roms / "Gyromite (World).zip").touch()
            (roms / "Stack-Up (World).zip").touch()
            config = root / "batocera.conf"
            config.write_text('nes["Super Glove Ball (USA).7z"].core=nestopia_powerglove\n')
            self.assertEqual(configure_player2_overrides(config, roms, 5), 5)
            first = config.read_text()
            self.assertIn('nes["Gyromite (World).zip"].retroarch.input_player2_joypad_index=5', first)
            self.assertNotIn('nes["Stack-Up (World).zip"].retroarch', first)
            self.assertIn('nes["Super Glove Ball (USA).7z"].core=nestopia_powerglove', first)
            configure_player2_overrides(config, roms, 5)
            self.assertEqual(config.read_text(), first)

    def test_trust_only_proxy_core_and_exact_rom_path(self):
        registry = load_registry()
        with tempfile.TemporaryDirectory() as directory:
            proc = Path(directory)
            process = proc / "123"
            process.mkdir()
            args = ["/usr/bin/retroarch", "-L", "/usr/lib/libretro/robvision_fceumm_libretro.so",
                    "--config", "/userdata/system/configs/retroarch/retroarchcustom.cfg",
                    "/userdata/roms/nes/Gyromite (World).zip"]
            process.joinpath("cmdline").write_bytes(b"\0".join(a.encode() for a in args) + b"\0")
            self.assertEqual(sender_game(123, registry, proc, "batocera"), "gyromite")
            self.assertEqual(running_game(registry, proc, "batocera"),
                             ("gyromite", "nes", args[-1]))
            args[2] = "/usr/lib/libretro/fceumm_libretro.so"
            process.joinpath("cmdline").write_bytes(b"\0".join(a.encode() for a in args) + b"\0")
            self.assertIsNone(sender_game(123, registry, proc, "batocera"))
            self.assertIsNone(running_game(registry, proc, "batocera"))


if __name__ == "__main__":
    unittest.main()
