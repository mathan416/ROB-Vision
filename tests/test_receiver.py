import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from identify_game import load_registry  # noqa: E402
from retropie_controller2 import pads_from_state, running_game, sync_game  # noqa: E402
from tools.retropie_frame_hook import FrameHookServer, sender_game  # noqa: E402
from tools.install_retropie_frame_hook import install  # noqa: E402


class ReceiverTests(unittest.TestCase):
    def test_frame_hook_install_selects_only_two_roms_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'nes').mkdir()
            (root / 'nes' / 'emulators.cfg').write_text('default = "lr-fceumm"\n')
            proxy = root / 'proxy.so'
            real = root / 'real.so'
            proxy.touch()
            real.touch()
            install(root, proxy, real)
            before = ((root / 'nes' / 'emulators.cfg').read_text(),
                      (root / 'all' / 'emulators.cfg').read_text())
            install(root, proxy, real)
            self.assertEqual(before, ((root / 'nes' / 'emulators.cfg').read_text(),
                                      (root / 'all' / 'emulators.cfg').read_text()))
            self.assertIn('default = "lr-fceumm"', before[0])
            self.assertIn('nes_GyromiteWorld = "lr-robvision-fceumm"', before[1])
            self.assertIn('nes_Stack-UpWorld = "lr-robvision-fceumm"', before[1])
            self.assertEqual(len(before[1].splitlines()), 2)

    def test_frame_hook_offers_both_cores_and_preserves_per_rom_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'configs'
            (root / 'nes').mkdir(parents=True)
            (root / 'all').mkdir()
            (root / 'nes' / 'emulators.cfg').write_text('default = "lr-fceumm"\n')
            (root / 'all' / 'emulators.cfg').write_text(
                'nes_GyromiteWorld = "lr-nestopia"\n'
                'nes_Stack-UpWorld = "lr-robvision-fceumm"\n')
            cores = {}
            for name in ('fceumm', 'nestopia'):
                proxy, real = base / (name + '-proxy.so'), base / (name + '-real.so')
                proxy.touch()
                real.touch()
                cores[name] = proxy, real
            install(root, cores=cores)
            self.assertEqual((root / 'all' / 'emulators.cfg').read_text(),
                             'nes_GyromiteWorld = "lr-robvision-nestopia"\n'
                             'nes_Stack-UpWorld = "lr-robvision-fceumm"\n')
            self.assertIn('lr-robvision-nestopia =', (root / 'nes' / 'emulators.cfg').read_text())
            install(root, cores=cores)
            self.assertEqual(len((root / 'nes' / 'emulators.cfg').read_text().splitlines()), 3)
            install(root, cores=cores, choices={'nes_Stack-UpWorld': 'nestopia'})
            self.assertIn('nes_Stack-UpWorld = "lr-robvision-nestopia"',
                          (root / 'all' / 'emulators.cfg').read_text())

    def test_frame_hook_leaves_other_rom_emulator_override_intact(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'configs'
            (root / 'nes').mkdir(parents=True)
            (root / 'all').mkdir()
            (root / 'nes' / 'emulators.cfg').write_text('default = "lr-fceumm"\n')
            (root / 'all' / 'emulators.cfg').write_text(
                'nes_GyromiteWorld = "custom-emulator"\n')
            proxy, real = base / 'proxy.so', base / 'real.so'
            proxy.touch()
            real.touch()
            install(root, cores={'fceumm': (proxy, real)})
            self.assertIn('nes_GyromiteWorld = "custom-emulator"',
                          (root / 'all' / 'emulators.cfg').read_text())

    def test_frame_hook_accepts_only_known_rom_under_proxy_core(self):
        registry = load_registry()
        with tempfile.TemporaryDirectory() as directory:
            proc = Path(directory)
            process = proc / '123'
            process.mkdir()
            args = ['/opt/retropie/emulators/retroarch/bin/retroarch', '-L',
                    '/home/pi/rob-vision/build/rob_vision_fceumm_libretro.so',
                    '/home/pi/RetroPie/roms/nes/Stack-Up (World).zip',
                    '--appendconfig', '/dev/shm/retroarch.cfg']
            (process / 'cmdline').write_bytes(b'\0'.join(a.encode() for a in args) + b'\0')
            self.assertEqual(sender_game(123, registry, proc), 'stack_up')
            args[2] = '/opt/retropie/libretrocores/lr-fceumm/fceumm_libretro.so'
            (process / 'cmdline').write_bytes(b'\0'.join(a.encode() for a in args) + b'\0')
            self.assertIsNone(sender_game(123, registry, proc))
            args[2] = '/home/pi/rob-vision/build/rob_vision_nestopia_libretro.so'
            (process / 'cmdline').write_bytes(b'\0'.join(a.encode() for a in args) + b'\0')
            self.assertEqual(sender_game(123, registry, proc), 'stack_up')

    def test_frame_hook_queues_only_complete_exact_command(self):
        with tempfile.TemporaryDirectory() as directory:
            hook = FrameHookServer(load_registry(), Path(directory) / 'unused.sock')
            with patch('tools.retropie_frame_hook.sender_game', return_value='stack_up'):
                for index, level in enumerate('N0001011111010'):
                    hook.feed(123, index, level)
                queued = hook.take_pending()
                self.assertEqual([(item['command'], item['pattern']) for item in queued],
                                 [('UP_STACK', '0001011111010')])
                for index, level in enumerate('0001011111011', start=20):
                    hook.feed(123, index, level)
                self.assertEqual(hook.take_pending(), [])

    def test_detects_each_live_retroarch_game_but_not_background_emulator(self):
        registry = load_registry()
        for filename, expected in [('Gyromite (World).7z', 'gyromite'),
                                   ('Stack-Up (World).zip', 'stack_up')]:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                proc = Path(directory)
                process = proc / '123'
                process.mkdir()
                rom = '/home/pi/RetroPie/roms/nes/' + filename
                args = ['/opt/retropie/emulators/retroarch/bin/retroarch', '-L', 'fceumm_libretro.so',
                        rom, '--appendconfig', '/dev/shm/retroarch.cfg']
                (process / 'cmdline').write_bytes(b'\0'.join(a.encode() for a in args) + b'\0')
                self.assertEqual(running_game(registry, proc), (expected, 'nes', rom))
                (process / 'cmdline').write_bytes(b'\0'.join(a.encode() for a in args[:-2]) + b'\0')
                self.assertIsNone(running_game(registry, proc))

    def test_unknown_name_and_game_state_release_buttons(self):
        self.assertEqual(pads_from_state({'game': 'stack_up'}), (False, False))
        self.assertEqual(pads_from_state({'game': 'gyromite', 'robot': {'pads': {'red': True, 'blue': False}}}),
                         (True, False))
        with self.assertRaises(ValueError):
            pads_from_state({'game': 'gyromite', 'robot': {'pads': {'red': 1, 'blue': False}}})

    def test_resync_posts_exact_rom_name_without_exposing_token_in_body(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b'{}'

        with patch('retropie_controller2.urlopen', return_value=Response()) as urlopen:
            sync_game('http://arduiain.local', 'secret-token', 'nes',
                      '/home/pi/RetroPie/roms/nes/Stack-Up (World).zip', .25)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, 'http://arduiain.local/api/launch')
        self.assertEqual(request.get_header('Authorization'), 'Bearer secret-token')
        self.assertEqual(json.loads(request.data),
                         {'event': 'start', 'system': 'nes', 'rom': 'Stack-Up (World).zip'})


if __name__ == '__main__':
    unittest.main()
