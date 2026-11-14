import io
import json
import struct
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

from controller.skins import GAME_PIECE_SLOTS, SLOTS, SkinStore


SAFE_SVG = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 128"><path d="M32 8V120" fill="none" stroke="#fff"/></svg>'


def tiny_png():
    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b'\x00\xff\x00\x00\xff')) + chunk(b'IEND', b''))


class SkinStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = SkinStore(Path(self.temp.name) / 'skins')

    def tearDown(self):
        self.temp.cleanup()

    def test_partial_skin_round_trip_and_activation(self):
        skin_id = self.store.create('Moonlight Buddy', 'Artist')
        self.store.put_asset(skin_id, 'left_upper_arm', '.svg', SAFE_SVG)
        self.store.put_asset(skin_id, 'head', '.png', tiny_png())
        self.assertEqual(self.store.listing()['active'], 'built-in')
        self.assertEqual(self.store._read(skin_id)['assets'],
                         {'left_upper_arm': 'assets/left_upper_arm.svg', 'head': 'assets/head.png'})
        self.store.activate(skin_id)
        self.assertEqual(self.store.active(), skin_id)
        exported = self.store.export(skin_id)
        imported = self.store.import_pack(exported)
        self.assertNotEqual(imported, skin_id)
        self.assertEqual(self.store.asset(imported, 'left_upper_arm')[0], SAFE_SVG)
        self.assertEqual(self.store.asset(imported, 'head')[0], tiny_png())
        self.store.delete(skin_id)
        self.assertEqual(self.store.active(), 'built-in')

    def test_unsafe_svg_and_pack_do_not_replace_active_skin(self):
        skin_id = self.store.create('Safe', 'Artist')
        self.store.activate(skin_id)
        self.store.put_asset(skin_id, 'head', '.svg',
                             b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><!-- art --><rect style="fill:#fff;stroke-width:1"/></svg>')
        with self.assertRaisesRegex(ValueError, 'unsupported element'):
            self.store.put_asset(skin_id, 'head', '.svg',
                                 b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><script>alert(1)</script></svg>')
        with self.assertRaisesRegex(ValueError, 'external content'):
            self.store.put_asset(skin_id, 'head', '.svg',
                                 b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><rect fill="https://example.org/a"/></svg>')
        with self.assertRaisesRegex(ValueError, 'unsupported styling'):
            self.store.put_asset(skin_id, 'head', '.svg',
                                 b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><rect style="background-image:url(https://example.org/a)"/></svg>')
        with self.assertRaisesRegex(ValueError, 'damaged chunk'):
            self.store.put_asset(skin_id, 'head', '.png', tiny_png()[:-13] + b'broken pixels')
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('skin.json', json.dumps({'schema': 1, 'name': 'Bad', 'artist': 'X', 'assets': {}}))
            archive.writestr('../outside.svg', SAFE_SVG)
        with self.assertRaisesRegex(ValueError, 'unsafe file'):
            self.store.import_pack(stream.getvalue())
        self.assertEqual(self.store.active(), skin_id)
        self.assertEqual(len(self.store.listing()['skins']), 2)

    def test_starter_pack_imports_with_reference_art(self):
        pack = Path(__file__).resolve().parents[1] / 'output/skins/Buddy-Skin-Starter.zip'
        with zipfile.ZipFile(pack) as archive:
            self.assertIn('R.O.B.-Vision-Buddy-Skin-Artist-Guide.pdf', archive.namelist())
            self.assertTrue(archive.read('R.O.B.-Vision-Buddy-Skin-Artist-Guide.pdf').startswith(b'%PDF-'))
            self.assertEqual({f'assets/{slot}.svg' for slot in SLOTS},
                             {name for name in archive.namelist() if name.startswith('assets/')})
        skin_id = self.store.import_pack(pack.read_bytes())
        self.assertEqual(self.store._read(skin_id)['assets'], {'head': 'assets/head.svg'})
        self.assertIn(b'<svg', self.store.asset(skin_id, 'head')[0])
        self.assertEqual(zipfile.ZipFile(io.BytesIO(self.store.export(skin_id))).namelist(),
                         ['skin.json', 'assets/head.svg'])

    def test_unselected_example_must_still_be_safe(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('skin.json', json.dumps({
                'schema': 1, 'name': 'Example', 'artist': 'Artist', 'assets': {}}))
            archive.writestr('assets/body.svg',
                             b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><script/></svg>')
        with self.assertRaisesRegex(ValueError, 'unsupported element'):
            self.store.import_pack(stream.getvalue())

    def test_game_piece_uploads_and_zip_entries_are_rejected(self):
        skin_id = self.store.create('Stage Buddy', 'Artist')
        self.store.put_asset(skin_id, 'spinner', '.svg', SAFE_SVG)
        for slot in GAME_PIECE_SLOTS:
            self.assertNotIn(slot, SLOTS)
            with self.subTest(slot=slot), self.assertRaisesRegex(ValueError, 'original artwork'):
                self.store.put_asset(skin_id, slot, '.svg', SAFE_SVG)
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('skin.json', json.dumps({
                'schema': 1, 'name': 'Old pack', 'artist': 'Artist',
                'assets': {'head': 'assets/head.svg', 'gyro': 'assets/gyro.svg',
                           'block_red': 'assets/block_red.svg'}}))
            for name in ('head', 'gyro', 'block_red'):
                archive.writestr(f'assets/{name}.svg', SAFE_SVG)
        with self.assertRaisesRegex(ValueError, 'Remove game-piece entries from skin.json: block_red, gyro'):
            self.store.import_pack(stream.getvalue())
        self.assertEqual(self.store.listing()['skins'][1]['assets'], {'spinner': 'assets/spinner.svg'})

    def test_saved_game_piece_art_is_ignored_and_excluded_from_export(self):
        skin_id = self.store.create('Earlier Buddy', 'Artist')
        self.store.put_asset(skin_id, 'head', '.svg', SAFE_SVG)
        path = self.store._path(skin_id)
        legacy_art = path / 'assets/gyro.svg'
        legacy_art.write_bytes(SAFE_SVG)
        doc = self.store._read(skin_id)
        doc['assets']['gyro'] = 'assets/gyro.svg'
        self.store._write_json(path / 'skin.json', doc)
        self.assertEqual(self.store.listing()['skins'][1]['assets'], {'head': 'assets/head.svg'})
        with self.assertRaisesRegex(ValueError, 'original artwork'):
            self.store.asset(skin_id, 'gyro')
        exported = self.store.export(skin_id)
        with zipfile.ZipFile(io.BytesIO(exported)) as archive:
            self.assertEqual(json.loads(archive.read('skin.json'))['assets'],
                             {'head': 'assets/head.svg'})
            self.assertEqual(archive.namelist(), ['skin.json', 'assets/head.svg'])
        self.assertTrue(legacy_art.is_file())
        imported = self.store.import_pack(exported)
        self.assertEqual(next(item['assets'] for item in self.store.listing()['skins']
                              if item['id'] == imported), {'head': 'assets/head.svg'})


if __name__ == '__main__':
    unittest.main()
