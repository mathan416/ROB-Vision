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


class ReceiverTests(unittest.TestCase):
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
