import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from identify_game import event, identify, load_registry  # noqa: E402


class GameIdentificationTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()

    def test_each_supplied_archive_basename_selects_the_game(self):
        for extension in (".7z", ".zip"):
            with self.subTest(extension=extension):
                self.assertEqual(
                    identify("nes", f"/roms/nes/Gyromite (World){extension}", self.registry),
                    "gyromite",
                )
                self.assertEqual(
                    identify("nes", f"/roms/nes/Stack-Up (World){extension}", self.registry),
                    "stack_up",
                )

    def test_extracted_rom_and_famicom_alias(self):
        self.assertEqual(identify("famicom", "/roms/GYROMITE (WORLD).NES", self.registry), "gyromite")

    def test_unknown_and_other_systems_fail_closed(self):
        self.assertIsNone(identify("snes", "/roms/Gyromite (World).zip", self.registry))
        self.assertIsNone(identify("nes", "/roms/Gyromite (USA).zip", self.registry))
        self.assertIsNone(identify("nes", "/roms/Other Game.zip", self.registry))
        self.assertEqual(event("start", "nes", "/roms/Other Game.zip", self.registry)["state"], "idle")

    def test_end_clears_state(self):
        self.assertEqual(event("end", "nes", "/roms/Gyromite (World).zip", self.registry), {
            "event": "end", "state": "idle", "game": None, "system": "", "rom": "",
        })

    def test_registry_rejects_case_collisions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "games.json"
            path.write_text(json.dumps({"schema": 1, "games": {
                "Gyromite (World).zip": "gyromite",
                "GYROMITE (WORLD).ZIP": "stack_up",
            }}))
            with self.assertRaisesRegex(ValueError, "Duplicate ROM basename"):
                load_registry(path)


if __name__ == "__main__":
    unittest.main()
