"""Check release bootstrap and the first-pairing service transition."""

import subprocess
import hashlib
import io
import os
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.retropie_pair import activate_receiver

ROOT = Path(__file__).resolve().parents[1]


class ReleaseInstallTests(unittest.TestCase):
    def test_bootstrap_parses_as_posix_shell(self):
        subprocess.run(["sh", "-n", str(ROOT / "scripts/release-install.sh")], check=True)

    def test_retropie_pairing_enables_receiver_and_maps_player_two(self):
        with patch("tools.retropie_pair.os.geteuid", return_value=0), patch(
            "tools.retropie_pair.subprocess.run"
        ) as run:
            activate_receiver("retropie")
        self.assertEqual([call.args[0] for call in run.call_args_list], [
            ["systemctl", "enable", "rob-vision-controller2.service"],
            ["systemctl", "restart", "rob-vision-controller2.service"],
            ["/usr/bin/python3", "/home/pi/rob-vision/scripts/install.py", "player2"],
        ])

    def test_batocera_pairing_restarts_its_receiver(self):
        with patch("tools.retropie_pair.subprocess.run") as run:
            activate_receiver("batocera")
        self.assertEqual(run.call_args.args[0], ["batocera-services", "restart", "ROBVision"])

    def test_bootstrap_checks_archive_before_invoking_uno_installer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "source.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                body = b"# dummy installer\n"
                info = tarfile.TarInfo("rob-vision/scripts/install.py")
                info.size = len(body)
                tar.addfile(info, io.BytesIO(body))
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            rendered = root / "install.sh"
            template = (ROOT / "scripts/release-install.sh").read_text()
            rendered.write_text(template.replace("@VERSION@", "v0.1.0")
                                .replace("@SHA256@", digest))
            binaries = root / "bin"
            binaries.mkdir()
            (binaries / "curl").write_text(
                '#!/bin/sh\nwhile [ "$1" != -o ]; do shift; done\ncp "$ROB_TEST_ARCHIVE" "$2"\n')
            (binaries / "id").write_text('#!/bin/sh\necho arduino\n')
            (binaries / "python3").write_text(
                '#!/bin/sh\nprintf "called" > "$ROB_TEST_MARKER"\n')
            for path in binaries.iterdir():
                path.chmod(0o755)
            marker = root / "called"
            env = dict(os.environ, PATH=str(binaries) + ":" + os.environ["PATH"],
                       ROB_TEST_ARCHIVE=str(archive), ROB_TEST_MARKER=str(marker))
            subprocess.run(["sh", str(rendered), "uno-q"], env=env, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertTrue(marker.exists())
            marker.unlink()
            rendered.write_text(template.replace("@VERSION@", "v0.1.0")
                                .replace("@SHA256@", "0" * 64))
            result = subprocess.run(["sh", str(rendered), "uno-q"], env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"checksum mismatch", result.stderr)
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
