import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.install import copy_tree_merge
from controller.pairings import PairingStore
from controller.service import console_registry, game_from_launch
from tools.batocera import select_games
from tools.game_registry import RegistryStore, serve
from tools.identify_game import load_registry, parse_registry, retropie_override_key
from tools.install_retropie_frame_hook import install as install_retropie_core


class GameRegistryEditorTests(unittest.TestCase):
    def test_custom_names_drive_both_console_core_choices(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / 'games.json'
            registry.write_text(json.dumps({'schema': 1, 'games': {
                'my gyromite.nes': 'gyromite', 'Blocks Night.zip': 'stack_up'}}))
            self.assertEqual(retropie_override_key('My Gyromite.nes'), 'nes_MyGyromite')
            configs = root / 'configs'
            (configs / 'nes').mkdir(parents=True)
            (configs / 'nes/emulators.cfg').write_text('default = "lr-fceumm"\n')
            proxy, real = root / 'proxy.so', root / 'real.so'
            proxy.touch(); real.touch()
            roms = root / 'roms'; roms.mkdir()
            (roms / 'My Gyromite.nes').touch()
            (roms / 'Blocks Night.zip').touch()
            install_retropie_core(configs, proxy, real, registry_path=registry, roms=roms)
            choices = (configs / 'all/emulators.cfg').read_text()
            self.assertIn('nes_MyGyromite = "lr-robvision-fceumm"', choices)
            self.assertIn('nes_BlocksNight = "lr-robvision-fceumm"', choices)
            batocera = root / 'batocera.conf'
            batocera.write_text('')
            select_games(batocera, roms, available=['nestopia'], registry_path=registry)
            self.assertIn('nes["My Gyromite.nes"].core=robvision_nestopia', batocera.read_text())
            self.assertIn('nes["Blocks Night.zip"].core=robvision_nestopia', batocera.read_text())

    def test_console_registry_survives_source_upgrade(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, installed = root / 'source', root / 'installed'
            source.mkdir(); installed.mkdir()
            (source / 'games.json').write_text('{"schema":1,"games":{"Default.nes":"gyromite"}}')
            (installed / 'games.json').write_text('{"schema":1,"games":{"Mine.nes":"stack_up"}}')
            copy_tree_merge(source, installed, preserve_registry=True)
            self.assertEqual(load_registry(installed / 'games.json'), {'mine.nes': 'stack_up'})

    def test_revision_backup_and_running_game_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'games.json'
            path.write_text('{"schema":1,"games":{"Gyromite (World).zip":"gyromite"}}')
            applied = []
            running = [False]
            store = RegistryStore(path, 'retropie', apply=lambda: applied.append(True),
                                  game_running=lambda: running[0])
            original = store.operate('read', {})
            updated = '{"schema":1,"games":{"My Game.nes":"stack_up"}}'
            running[0] = True
            with self.assertRaisesRegex(ValueError, 'Exit the running game'):
                store.operate('save', {'revision': original['revision'], 'document': updated})
            self.assertEqual(path.read_text(), original['document'])
            running[0] = False
            saved = store.operate('save', {'revision': original['revision'], 'document': updated})
            self.assertEqual(saved['document'], updated)
            self.assertTrue(saved['has_backup'])
            self.assertEqual(applied, [True])
            with self.assertRaisesRegex(ValueError, 'changed elsewhere'):
                store.operate('save', {'revision': original['revision'], 'document': updated})
            restored = store.operate('restore', {'revision': saved['revision']})
            self.assertEqual(restored['document'], original['document'])

    def test_rejects_ambiguous_filenames_and_invalid_game_ids(self):
        with self.assertRaisesRegex(ValueError, 'collision'):
            parse_registry('{"schema":1,"games":{"A B.nes":"gyromite","AB.zip":"stack_up"}}')
        with self.assertRaisesRegex(ValueError, 'Unsupported game ID'):
            parse_registry('{"schema":1,"games":{"Mario.nes":"mario"}}')

    def test_controller_accepts_custom_game_report_from_paired_launch(self):
        self.assertEqual(game_from_launch({'event': 'start', 'system': 'nes',
                                           'rom': 'My Gyromite.nes', 'game': 'gyromite'}), 'gyromite')
        self.assertIsNone(game_from_launch({'event': 'start', 'system': 'snes',
                                            'rom': 'My Gyromite.nes', 'game': 'gyromite'}))
        self.assertIsNone(game_from_launch({'event': 'start', 'system': 'nes',
                                            'rom': 'My Gyromite.nes', 'game': 'other'}))

    def test_uno_proxies_only_to_the_selected_paired_console(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *_args): return False
            def read(self, _limit): return b'{"document":"{}","revision":"abc"}'
        class Opener:
            def open(self, request, timeout):
                self.request = request
                self.timeout = timeout
                return Response()
        with tempfile.TemporaryDirectory() as directory:
            pairings = PairingStore(Path(directory) / 'paired.json')
            pairings.add('a' * 32, 'secret-token-123456', 'retropie', 'retropie.local')
            opener = Opener()
            with patch('controller.service.build_opener', return_value=opener), \
                 patch('controller.service.resolve_ipv4', return_value='10.0.2.57'):
                result = console_registry(pairings, 'a' * 32, 'read')
            self.assertEqual(result['revision'], 'abc')
            self.assertEqual(opener.request.full_url, 'http://10.0.2.57:8769/registry')
            self.assertEqual(opener.request.get_header('Authorization'), 'Bearer secret-token-123456')
            with self.assertRaisesRegex(ValueError, 'Choose a paired console'):
                console_registry(pairings, 'b' * 32, 'read')

    def test_registry_uses_authenticated_current_address_after_dhcp_change(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *_args): return False
            def read(self, _limit): return b'{"document":"{}","revision":"abc"}'
        class Opener:
            def open(self, request, timeout):
                self.request = request
                return Response()
        with tempfile.TemporaryDirectory() as directory:
            pairings = PairingStore(Path(directory) / 'paired.json')
            pairings.add('a' * 32, 'secret-token-123456', 'batocera', '10.0.2.153')
            pairings.seen('a' * 32, '10.0.2.26')
            opener = Opener()
            with patch('controller.service.build_opener', return_value=opener):
                console_registry(pairings, 'a' * 32, 'read')
            self.assertEqual(opener.request.full_url, 'http://10.0.2.26:8769/registry')

    def test_paired_console_http_editor_rejects_missing_token(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, token = root / 'games.json', root / 'token'
            path.write_text('{"schema":1,"games":{"Game.nes":"gyromite"}}')
            token.write_text('paired-secret')
            try:
                server = serve(RegistryStore(path, 'retropie', apply=lambda: None,
                                             game_running=lambda: False), token, host='127.0.0.1', port=0)
            except PermissionError:
                self.skipTest('Local socket binding is unavailable in this sandbox')
            try:
                address = f'http://127.0.0.1:{server.server_port}/registry'
                body = json.dumps({'action': 'read'}).encode()
                with self.assertRaises(HTTPError) as denied:
                    urlopen(Request(address, data=body, method='POST'), timeout=2)
                self.assertEqual(denied.exception.code, 403)
                denied.exception.close()
                with urlopen(Request(address, data=body, method='POST',
                                     headers={'Authorization': 'Bearer paired-secret'}), timeout=2) as response:
                    result = json.load(response)
                self.assertIn('Game.nes', result['document'])
            finally:
                server.shutdown()
                server.server_close()


if __name__ == '__main__':
    unittest.main()
