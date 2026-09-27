"""Verify shared Router migrations without changing a live console."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from router_shared.controller_router import merge_retropie_indexes, output_indexes, validate_config
from router_shared.virtual_sources import configured_sources
from tools.controller_router_setup import (BUDDY, ensure, ensure_buddy_frontend_mapping,
                                           activate, proposed_config, retire_legacy_nes_override,
                                           retire_batocera_pad_overrides)


def source(name, identity):
    return {"id": identity, "name": name, "guid": "0" * 32,
            "vendor": "1209", "product": "0001", "version": "0001",
            "uniq": "", "phys": "", "mapping": [
                {"name": "a", "type": "button", "code": 0, "value": 1,
                 "evdev_code": 304}]}


class ControllerRouterTests(unittest.TestCase):
    def test_buddy_mapping_is_project_supplied(self):
        sources = configured_sources(Path(__file__).resolve().parents[1] /
                                     "config/router_sources.json")
        self.assertEqual([(item["name"], item["vendor"], item["product"])
                          for item in sources],
                         [(BUDDY, "1209", "0001")])

    def test_receiver_services_expose_buddy_to_setup_inventory(self):
        root = Path(__file__).resolve().parents[1]
        retropie = (root / "deploy/retropie/rob-vision-controller2.service").read_text()
        batocera = (root / "deploy/batocera/ROBVision").read_text()
        self.assertIn("Environment=CONTROLLER_ROUTER_SOURCES_FILE="
                      "/home/pi/rob-vision/config/router_sources.json", retropie)
        self.assertIn('CONTROLLER_ROUTER_SOURCES_FILE="$APP/config/router_sources.json" \\',
                      batocera)

    def test_fresh_console_assigns_known_controllers_and_buddy(self):
        p1 = source("8BitDo", "a" * 16)
        p2 = source("Arcade Player 2", "b" * 16)
        buddy = source(BUDDY, "c" * 16)
        config = proposed_config(None, "retropie", [p1, p2, buddy])
        self.assertEqual([(item["player"], [source["name"] for source in item["sources"]])
                          for item in config["players"]],
                         [(1, ["8BitDo"]), (2, ["Arcade Player 2", BUDDY])])

    def test_existing_router_keeps_all_assignments_and_is_idempotent(self):
        p1, p2, buddy = (source("8BitDo", "a" * 16),
                         source("Arcade Player 2", "b" * 16), source(BUDDY, "c" * 16))
        current = validate_config({"format": 2, "platform": "retropie",
                                   "players": [{"player": 1, "sources": [p1]},
                                               {"player": 2, "sources": [p2]}],
                                   "virtualglove_player": 1, "physical_scope": "all"})
        updated = proposed_config(current, "retropie", [p1, p2, buddy])
        self.assertEqual(updated["virtualglove_player"], 1)
        self.assertEqual(updated["players"][0]["sources"], [p1])
        self.assertEqual(updated["players"][1]["sources"], [p2, buddy])
        self.assertEqual(proposed_config(updated, "retropie", [p1, p2, buddy]), updated)
        self.assertEqual(current["players"][1]["sources"], [p2])

    def test_missing_buddy_does_not_change_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "controller-router.json"
            es = Path(directory) / "es_input.cfg"
            es.write_text("<inputList/>")
            with patch("tools.controller_router_setup.controller_candidates", return_value=[]):
                with self.assertRaisesRegex(RuntimeError, "Buddy's controller"):
                    ensure("retropie", config_path=path, es_inputs=es, wait_seconds=0)
            self.assertFalse(path.exists())

    def test_first_pair_refuses_truncated_emulationstation_process(self):
        def process(command, **_kwargs):
            return type("Result", (), {"returncode": 0 if command[-1] == "emulationstatio" else 1})()

        with patch("tools.controller_router_setup.subprocess.run", side_effect=process):
            with self.assertRaisesRegex(RuntimeError, "Exit EmulationStation"):
                activate("retropie")

    def test_existing_batocera_router_can_discover_buddy_from_frontend_map(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'es_input.cfg'
            path.write_text('<inputList>\n</inputList>\n')
            buddy = source(BUDDY, 'c' * 16)
            self.assertTrue(ensure_buddy_frontend_mapping(path, buddy))
            self.assertFalse(ensure_buddy_frontend_mapping(path, buddy))
            self.assertIn('code="304"', path.read_text())
            self.assertTrue(path.with_name('es_input.cfg.before-rob-vision-router').exists())

    def test_router_replaces_only_its_nes_index_block(self):
        config = proposed_config(None, "retropie", [source(BUDDY, "c" * 16)])
        before = ('input_player1_a_btn = "7"\n'
                  '# VirtualGlove Controller Router\n'
                  'input_player1_joypad_index = "3"\n'
                  '# End VirtualGlove Controller Router\n'
                  '#include "../all/retroarch.cfg"\n')
        after = merge_retropie_indexes(before, config, {2: 5})
        self.assertIn('input_player1_a_btn = "7"', after)
        self.assertIn('input_player2_joypad_index = "5"', after)
        self.assertNotIn('input_player1_joypad_index = "3"', after)
        self.assertLess(after.index('input_player2_joypad_index'), after.index('#include'))
        self.assertEqual(merge_retropie_indexes(after, config, {2: 5}), after)

    def test_router_waits_for_udev_registration_after_joystick_appears(self):
        with tempfile.TemporaryDirectory() as directory:
            sys_root = Path(directory)
            device = sys_root / 'js2/device'
            device.mkdir(parents=True)
            (device / 'name').write_text('VirtualGlove Merged Player 2\n')
            with patch('router_shared.controller_router.retroarch_udev_event_nodes', return_value=[]), \
                    patch('router_shared.controller_router.retroarch_index_for_js', side_effect=RuntimeError('not ready')):
                self.assertEqual(output_indexes([2], sys_root=sys_root, platform='retropie'), {})

    def test_one_time_cleanup_preserves_unrelated_nes_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "retroarch.cfg"
            path.write_text('input_player1_joypad_index = "3"\n'
                            '# BEGIN R.O.B. Vision (managed by installer)\n'
                            'input_player2_a_btn = "1"\n'
                            'input_player2_b_btn = "0"\n'
                            '# END R.O.B. Vision (managed by installer)\n'
                            '#include "all/retroarch.cfg"\n')
            self.assertTrue(retire_legacy_nes_override(path))
            self.assertFalse(retire_legacy_nes_override(path))
            self.assertIn('input_player1_joypad_index = "3"', path.read_text())
            self.assertNotIn('input_player2_a_btn', path.read_text())
            self.assertTrue(path.with_name('retroarch.cfg.before-rob-vision-router').exists())

    def test_batocera_migration_removes_only_old_registered_pad_override(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / 'games.json'
            registry.write_text(json.dumps({"schema": 1, "games": {
                "Gyromite (World).zip": "gyromite"}}))
            config = root / 'batocera.conf'
            prefix = 'nes["Gyromite (World).zip"].retroarch.'
            config.write_text('global.retroarch.video_fullscreen=true\n' +
                              ''.join(prefix + key + '=' + value + '\n' for key, value in (
                                  ('input_libretro_device_p2', '1'),
                                  ('input_player2_joypad_index', '5'),
                                  ('input_player2_a_btn', '0'),
                                  ('input_player2_b_btn', '1'))) +
                              prefix + 'input_player1_joypad_index=3\n')
            self.assertTrue(retire_batocera_pad_overrides(config, registry))
            self.assertFalse(retire_batocera_pad_overrides(config, registry))
            self.assertIn('input_player1_joypad_index=3', config.read_text())
            self.assertIn('video_fullscreen=true', config.read_text())
            self.assertNotIn('input_player2_a_btn', config.read_text())


if __name__ == '__main__':
    unittest.main()
