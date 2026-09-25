import tempfile
import unittest
from pathlib import Path

from controller.pairings import PairingStore


def headers(token, platform, console_id=""):
    result = {"Authorization": "Bearer " + token, "X-ROB-Receiver": platform}
    if console_id:
        result["X-ROB-Console-ID"] = console_id
    return result


class PairingTests(unittest.TestCase):
    def test_two_credentials_are_independent_and_removal_persists(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paired-consoles.json"
            store = PairingStore(path, "old-shared-token-123")
            retro_id, bat_id = "a" * 32, "b" * 32
            store.add(retro_id, "retropie-secret-token", "retropie", "retropie.local")
            store.add(bat_id, "batocera-secret-token", "batocera", "batocera.local")
            self.assertIsNone(store.verify(headers("old-shared-token-123", "retropie")))
            self.assertEqual(store.verify(headers("retropie-secret-token", "retropie", retro_id))["id"], retro_id)
            self.assertEqual(store.verify(headers("batocera-secret-token", "batocera", bat_id))["id"], bat_id)
            self.assertIsNone(store.verify(headers("batocera-secret-token", "retropie", bat_id)))
            store.seen(retro_id)
            store.seen(bat_id)
            self.assertEqual(len([row for row in store.list_public() if row["online"]]), 2)
            self.assertNotIn("token", store.list_public()[0])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            store.remove(retro_id)
            reloaded = PairingStore(path, "old-shared-token-123")
            self.assertIsNone(reloaded.verify(headers("retropie-secret-token", "retropie", retro_id)))
            self.assertIsNone(reloaded.verify(headers("old-shared-token-123", "retropie")))
            self.assertIsNotNone(reloaded.verify(headers("batocera-secret-token", "batocera", bat_id)))

    def test_legacy_pairings_are_visible_and_can_be_revoked(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PairingStore(Path(directory) / "pairings.json", "old-shared-token-123")
            self.assertEqual(store.verify(headers("old-shared-token-123", "retropie"))["id"],
                             "legacy:retropie")
            store.seen("legacy:retropie")
            self.assertEqual(store.list_public()[0]["legacy"], True)
            store.remove("legacy:retropie")
            self.assertIsNone(store.verify(headers("old-shared-token-123", "retropie")))


if __name__ == "__main__":
    unittest.main()
