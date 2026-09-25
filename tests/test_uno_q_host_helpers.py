"""Check that the R.O.B. Vision camera host helper protects the Ethernet hub."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "deploy" / "uno-q" / "rob-vision-camera-recovery.py"
SPEC = importlib.util.spec_from_file_location("rob_vision_camera_recovery", SOURCE)
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)


class CameraRecoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.data = root / "data"
        self.data.mkdir()
        self.config = root / "camera.json"
        self.driver = root / "driver"
        self.driver.mkdir()
        for name in ("bind", "unbind"):
            (self.driver / name).touch()
        self.usb_devices = root / "usb-devices"
        self.usb_devices.mkdir()
        self.hub = root / "2-1"
        (self.hub / "power").mkdir(parents=True)
        (self.hub / "idVendor").write_text("0bda")
        (self.hub / "idProduct").write_text("0411")
        (self.hub / "bDeviceClass").write_text("09")
        self.camera = root / "2-1.4"
        (self.camera / "power").mkdir(parents=True)
        (self.usb_devices / "2-1").symlink_to(self.hub)
        self.discovery = {
            "camera": {"vendor_id": "046d", "product_id": "0825", "name": "Camera"},
            "hub": {"vendor_id": "0bda", "product_id": "0411", "name": "Hub", "sysfs_name": "2-1"},
            "camera_path": self.camera, "hub_path": self.hub,
        }
        values = {
            "APP_DATA": self.data, "REQUEST": self.data / "camera-recovery-request",
            "RESULT": self.data / "camera-recovery-result", "CONFIG": self.config,
            "USB_DEVICES": self.usb_devices, "USB_DRIVER": self.driver,
            "LOCK": root / "lock", "STAMP": root / "stamp",
        }
        for name, value in values.items():
            patcher = patch.object(helper, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        for target, name, value in ((helper, "_config_is_secure", True),
                                    (helper.os, "geteuid", 0),
                                    (helper.shutil, "which", None)):
            patcher = patch.object(target, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        helper._write_config(self.discovery)

    def test_enroll_present_camera_without_usb_reset(self):
        helper.REQUEST.write_text("enroll\n")
        with patch.object(helper, "_discover_cameras", return_value=[self.discovery]):
            self.assertEqual(helper.main([]), 0)
        self.assertEqual(json.loads(helper.RESULT.read_text())["method"], "enrollment")
        self.assertEqual((self.driver / "unbind").read_text(), "")

    def test_refuse_whole_hub_reset_when_ethernet_is_attached(self):
        (self.hub / "2-1.2:1.0" / "net" / "eth0").mkdir(parents=True)
        helper.REQUEST.write_text("recover\n")
        with patch.object(helper, "_discover_cameras", return_value=[self.discovery]):
            with self.assertRaisesRegex(RuntimeError, "network interface"):
                helper.main([])
        self.assertEqual((self.driver / "unbind").read_text(), "")
        self.assertEqual(json.loads(helper.RESULT.read_text())["status"], "failed")

    def test_supported_camera_port_cycle_does_not_reset_hub(self):
        helper.REQUEST.write_text("recover\n")
        with patch.object(helper, "_discover_cameras", return_value=[self.discovery]), \
                patch.object(helper, "_power_cycle_camera_port", return_value=True):
            self.assertEqual(helper.main([]), 0)
        result = json.loads(helper.RESULT.read_text())
        self.assertEqual(result["method"], "port-power-cycle")
        self.assertEqual((self.driver / "unbind").read_text(), "")


if __name__ == "__main__":
    unittest.main()
