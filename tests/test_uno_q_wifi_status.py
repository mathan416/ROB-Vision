"""Verify R.O.B. Vision's unprivileged host link-status sampler."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "deploy" / "uno-q" / "rob-vision-wifi-status.py"
SPEC = importlib.util.spec_from_file_location("rob_vision_wifi_status", SOURCE)
status = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(status)


class WifiStatusTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def interface(self, name, carrier, wireless=False, physical=True):
        interface = self.root / name
        interface.mkdir()
        (interface / "carrier").write_text(carrier)
        if wireless:
            (interface / "wireless").mkdir()
        if physical:
            (interface / "device").mkdir()
            (interface / "type").write_text("1")
        return interface

    def test_ethernet_is_connected_when_wifi_is_down_and_bridges_are_ignored(self):
        self.interface("wlan0", "0", wireless=True)
        self.interface("eth0", "1")
        self.interface("docker0", "1", physical=False)
        self.assertEqual(status.wifi_state(self.root), "disconnected")
        self.assertEqual(status.link_state(self.root), "connected")

    def test_broadcast_is_derived_only_from_connected_physical_link(self):
        self.interface("eth0", "1")
        self.interface("docker0", "1", physical=False)
        with patch.object(status, "_interface_ipv4", return_value=("192.168.42.17", "255.255.255.0")):
            addresses = status.broadcast_addresses(self.root, status._interface_ipv4)
        self.assertEqual(addresses, ["192.168.42.255"])

    def test_public_status_has_no_network_name_or_credentials(self):
        output = self.root / "wifi-status.json"
        with patch.object(status, "wifi_state", return_value="disconnected"), \
                patch.object(status, "link_state", return_value="connected"), \
                patch.object(status, "broadcast_addresses", return_value=["192.168.42.255"]):
            status.publish(output)
        payload = json.loads(output.read_text())
        self.assertEqual(payload["networking"], "connected")
        self.assertEqual(payload["broadcasts"], ["192.168.42.255"])
        self.assertEqual(set(payload), {"version", "state", "networking", "broadcasts", "observed_at"})


if __name__ == "__main__":
    unittest.main()
