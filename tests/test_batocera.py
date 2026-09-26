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
from tools.batocera import configure_player2_overrides, map_player2, pad_index, player1_index, select_games
from scripts.install_batocera import available_cores, prepare_wrappers, suspend_menu, resume_menu, wrapper_arch
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

    def test_player1_uses_the_controller_mapped_in_emulationstation(self):
        with tempfile.TemporaryDirectory() as directory:
            xml = Path(directory) / "es_input.cfg"
            xml.write_text('<inputList><inputConfig type="joystick" '
                           'deviceName="Atari Game Controller"/></inputList>')
            sdl = MagicMock()
            sdl.SDL_Init.return_value = 0
            sdl.SDL_NumJoysticks.return_value = 3
            sdl.SDL_JoystickNameForIndex.side_effect = [
                b"Atari Game Controller", b"virtual spinner", b"R.O.B. Vision Controller 2"]
            with patch("tools.batocera.ctypes.CDLL", return_value=sdl):
                self.assertEqual(player1_index(xml), 0)
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

    def test_core_preflight_uses_installed_cores_instead_of_a_version_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cores, info = root / "cores", root / "info"
            cores.mkdir()
            info.mkdir()
            (cores / "nestopia_libretro.so").touch()
            (info / "nestopia_libretro.info").touch()
            self.assertEqual(available_cores(cores, info), ["nestopia"])
            (info / "nestopia_libretro.info").unlink()
            with self.assertRaisesRegex(RuntimeError, "FCEUmm or Nestopia"):
                available_cores(cores, info)

    def test_uses_matching_architecture_bundle_without_version_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "deploy/batocera/cores/aarch64"
            bundle.mkdir(parents=True)
            library = bundle / "robvision_fceumm_libretro.so"
            library.touch()
            with patch("scripts.install_batocera.ctypes.CDLL") as load:
                self.assertEqual(prepare_wrappers(root, root, ["fceumm"], "aarch64"),
                                 {"fceumm": library})
            load.assert_called_once_with(str(library))

    def test_release_bundles_both_wrappers_for_linux_cpu_families(self):
        machines = {"x86_64": (2, 62), "x86": (1, 3), "aarch64": (2, 183),
                    "armv7l": (1, 40), "armv6l": (1, 40), "riscv64": (2, 243)}
        for machine, (elf_class, elf_machine) in machines.items():
            for core in ("fceumm", "nestopia"):
                path = ROOT / "deploy/batocera/cores" / machine / f"robvision_{core}_libretro.so"
                with self.subTest(machine=machine, core=core):
                    header = path.read_bytes()[:20]
                    self.assertEqual(header[:4], b"\x7fELF")
                    self.assertEqual(header[4], elf_class)
                    self.assertEqual(int.from_bytes(header[18:20], "little"), elf_machine)
        self.assertEqual(wrapper_arch("i686"), "x86")
        self.assertEqual(wrapper_arch("armv8l"), "armv7l")
        self.assertEqual(wrapper_arch("arm64"), "aarch64")

    def test_can_build_a_missing_architecture_wrapper_before_install(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            proxy = root / "deploy/retropie/rob_vision_fceumm_proxy.c"
            proxy.parent.mkdir(parents=True)
            proxy.touch()
            with patch("scripts.install_batocera.shutil.which", return_value="/usr/bin/gcc"), patch(
                "scripts.install_batocera.subprocess.run"
            ) as compile_core, patch("scripts.install_batocera.ctypes.CDLL"):
                libraries = prepare_wrappers(root, root, ["fceumm"], "armv7l")
            self.assertEqual(libraries["fceumm"], root / "robvision_fceumm_libretro.so")
            self.assertIn('-DROB_REAL_CORE_PATH="/usr/lib/libretro/fceumm_libretro.so"',
                          compile_core.call_args.args[0])
            with patch("scripts.install_batocera.shutil.which", return_value=None), self.assertRaisesRegex(
                RuntimeError, "no C compiler"
            ):
                prepare_wrappers(root, root, ["fceumm"], "armv7l")

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

    def test_selects_installed_nestopia_when_fceumm_is_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "batocera.conf"
            config.write_text('')
            roms = root / "roms"
            roms.mkdir()
            (roms / "Gyromite (World).zip").touch()
            self.assertEqual(select_games(config, roms, available=["nestopia"]),
                             ["Gyromite (World).zip"])
            self.assertIn('nes["Gyromite (World).zip"].core=robvision_nestopia',
                          config.read_text())

    def test_player2_changes_only_its_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "retroarchcustom.cfg"
            config.write_text('input_player1_a_btn = "4"\ninput_player2_joypad_index = 1\n')
            self.assertEqual(map_player2(config, 3), 3)
            first = config.read_text()
            self.assertIn('input_player1_a_btn = "4"', first)
            self.assertIn('input_player2_joypad_index = "3"', first)
            self.assertIn('input_player2_a_btn = "0"', first)
            self.assertIn('input_player2_b_btn = "1"', first)
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
            self.assertEqual(configure_player2_overrides(config, roms, 5, player1=0), 5)
            first = config.read_text()
            self.assertIn('nes["Gyromite (World).zip"].retroarch.input_player2_joypad_index=5', first)
            self.assertIn('nes["Gyromite (World).zip"].retroarch.input_player1_joypad_index=0', first)
            self.assertIn('nes["Stack-Up (World).zip"].retroarch.input_player1_joypad_index=0', first)
            self.assertNotIn('nes["Stack-Up (World).zip"].retroarch.input_player2', first)
            self.assertIn('nes["Gyromite (World).zip"].retroarch.input_player2_a_btn=0', first)
            self.assertIn('nes["Gyromite (World).zip"].retroarch.input_player2_b_btn=1', first)
            self.assertIn('nes["Super Glove Ball (USA).7z"].core=nestopia_powerglove', first)
            configure_player2_overrides(config, roms, 5, player1=0)
            self.assertEqual(config.read_text(), first)
            with self.assertRaises(RuntimeError):
                configure_player2_overrides(config, roms, 5, player1=5)

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
