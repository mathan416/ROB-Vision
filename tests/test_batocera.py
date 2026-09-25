import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from identify_game import load_registry
from retropie_controller2 import running_game
from tools.batocera import configure_player2_overrides, map_player2, select_games
from tools.retropie_frame_hook import sender_game


class BatoceraTests(unittest.TestCase):
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
