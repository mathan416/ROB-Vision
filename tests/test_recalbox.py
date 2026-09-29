"""Recalbox integration keeps ordinary NES choices and existing ROM settings."""

import tempfile
import unittest
from pathlib import Path

from tools.recalbox import select_games, systemlist_text


SYSTEMS = '''<systemList><system name="nes"><emulatorList><emulator name="libretro"><core name="fceumm" /></emulator></emulatorList></system></systemList>'''


class RecalboxTests(unittest.TestCase):
    def test_system_registration_preserves_stock_core_and_is_repeatable(self):
        first = systemlist_text(SYSTEMS)
        second = systemlist_text(first)
        self.assertEqual(first, second)
        self.assertIn('name="fceumm"', second)
        self.assertEqual(second.count('name="robvision_fceumm"'), 1)
        self.assertEqual(second.count('name="robvision_nestopia"'), 1)

    def test_registered_roms_get_sidecars_without_changing_other_games(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            roms = root / 'roms'
            roms.mkdir()
            registry = root / 'games.json'
            registry.write_text('{"schema":1,"games":{"Gyromite (World).zip":"gyromite","Stack-Up (World).zip":"stack_up"}}')
            for name in ('Gyromite (World).zip', 'Stack-Up (World).zip', 'Other.zip'):
                (roms / name).touch()
            gyromite = roms / 'Gyromite (World).zip.recalbox.conf'
            gyromite.write_text('volume=70\nnes.core=nestopia\n')
            chosen = select_games(registry, roms)
            self.assertEqual(chosen, ['Gyromite (World).zip', 'Stack-Up (World).zip'])
            self.assertIn('volume=70\n', gyromite.read_text())
            self.assertIn('nes.core=robvision_nestopia\n', gyromite.read_text())
            self.assertIn('nes.core=robvision_fceumm\n', (roms / 'Stack-Up (World).zip.recalbox.conf').read_text())
            self.assertFalse((roms / 'Other.zip.recalbox.conf').exists())
            self.assertEqual(select_games(registry, roms), chosen)


if __name__ == '__main__':
    unittest.main()
