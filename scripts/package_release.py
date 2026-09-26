#!/usr/bin/env python3
"""Build immutable Git-commit release assets, including a checksum-pinned installer."""

import argparse
import hashlib
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Release tag, e.g. v0.1.1 or v0.1.1-rc.1")
    parser.add_argument("--ref", default="HEAD", help="Committed Git revision to package")
    args = parser.parse_args()
    if not re.fullmatch(r"v0\.1\.\d+(?:-rc\.\d+)?", args.version):
        parser.error("Expected a 0.1.x release tag")
    output = ROOT / "output" / "release" / args.version
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"rob-vision-{args.version}.tar.gz"
    with archive.open("wb") as stream:
        subprocess.run(
            ["git", "archive", "--format=tar.gz", "--prefix=rob-vision/", args.ref],
            cwd=ROOT, stdout=stream, check=True,
        )
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    template = (ROOT / "scripts/release-install.sh").read_text()
    installer = output / "install.sh"
    installer.write_text(template.replace("@VERSION@", args.version).replace("@SHA256@", digest))
    installer.chmod(0o755)
    pdfs = []
    for guide in sorted((ROOT / "output/pdf").glob("R.O.B.-Vision-*.pdf")):
        copy = output / guide.name
        shutil.copy2(guide, copy)
        pdfs.append(copy)
    required_guides = {
        "R.O.B.-Vision-Buddy-Story-Comic.pdf",
        "R.O.B.-Vision-Engineering-Journey.pdf",
        "R.O.B.-Vision-Game-Manual.pdf",
        "R.O.B.-Vision-Installation-and-Setup.pdf",
        "R.O.B.-Vision-Matrix-Display-Guide.pdf",
        "R.O.B.-Vision-Quick-Reference.pdf",
        "R.O.B.-Vision-Technical-Reference.pdf",
        "R.O.B.-Vision-Technical-Test-Results.pdf",
        "R.O.B.-Vision-User-Guide.pdf",
    }
    actual_guides = {path.name for path in pdfs}
    if actual_guides != required_guides:
        missing = sorted(required_guides - actual_guides)
        unexpected = sorted(actual_guides - required_guides)
        parser.error(f"PDF guide set mismatch: missing={missing}, unexpected={unexpected}")
    checksums = output / "SHA256SUMS"
    checksums.write_text("".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
        for path in (archive, installer, *pdfs)
    ))
    print(output)


if __name__ == "__main__":
    main()
