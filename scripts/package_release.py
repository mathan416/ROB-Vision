#!/usr/bin/env python3
"""Build immutable Git-commit release assets, including a checksum-pinned installer."""

import argparse
import hashlib
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Release tag, e.g. v0.1.0-rc.1")
    parser.add_argument("--ref", default="HEAD", help="Committed Git revision to package")
    args = parser.parse_args()
    if not args.version.startswith("v0.1.0") or not all(
        char.isalnum() or char in ".-" for char in args.version
    ):
        parser.error("Expected a 0.1.0 release tag")
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
    if len(pdfs) != 4:
        parser.error("Build all four PDF guides before packaging the release")
    checksums = output / "SHA256SUMS"
    checksums.write_text("".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
        for path in (archive, installer, *pdfs)
    ))
    print(output)


if __name__ == "__main__":
    main()
