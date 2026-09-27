#!/usr/bin/env python3
"""Create the static-site ZIP for a manual web-root upload."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "website"
OUTPUT = ROOT / "output/site/rob-vision-website.zip"
REQUIRED = {
    "index.html", "install.html", "engineering.html", "about.html",
    "site.css", "site.js", "robots.txt", "sitemap.xml",
}


def main():
    files = sorted((SITE / name for name in REQUIRED), key=lambda path: path.name)
    for directory in ("assets", "downloads"):
        files += sorted(path for path in (SITE / directory).rglob("*") if path.is_file())
    for path in files:
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"Website file missing or unsupported: {path}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, path.relative_to(SITE))
    print(OUTPUT)


if __name__ == "__main__":
    main()
