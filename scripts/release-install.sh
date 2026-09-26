#!/bin/sh
# Rendered with a version and source-archive digest by package_release.py.
set -eu
VERSION="@VERSION@"
ARCHIVE_SHA256="@SHA256@"
BASE="https://github.com/mathan416/ROB-Vision/releases/download/$VERSION"

fail() { echo "R.O.B. Vision: $*" >&2; exit 1; }
[ "$#" -ge 1 ] || fail "Use: install.sh uno-q | console <Uno-Q-hostname>"
target="$1"
case "$target" in
    uno-q) [ "$#" -eq 1 ] || fail "Uno Q needs no other argument" ;;
    console) [ "$#" -eq 2 ] || { [ "$#" -eq 3 ] && [ "$3" = --pair ]; } || fail "Console needs the Uno Q hostname; optional --pair renews pairing" ;;
    *) fail "Unknown target: $target" ;;
esac
command -v curl >/dev/null || fail "curl is required"
command -v tar >/dev/null || fail "tar is required"
command -v python3 >/dev/null || fail "Python 3 is required"
if command -v sha256sum >/dev/null; then
    hash_file() { sha256sum "$1" | cut -d ' ' -f 1; }
elif command -v shasum >/dev/null; then
    hash_file() { shasum -a 256 "$1" | cut -d ' ' -f 1; }
else
    fail "sha256sum or shasum is required"
fi
work="$(mktemp -d)" || fail "Could not create temporary directory"
trap 'rm -rf "$work"' EXIT HUP INT TERM
archive="$work/rob-vision.tar.gz"
curl -fL --retry 3 --connect-timeout 15 -o "$archive" \
    "$BASE/rob-vision-$VERSION.tar.gz" || fail "Could not download $VERSION"
[ "$(hash_file "$archive")" = "$ARCHIVE_SHA256" ] || fail "Release archive checksum mismatch"
tar -xzf "$archive" -C "$work" || fail "Release archive could not be opened"
source="$work/rob-vision"
[ -f "$source/scripts/install.py" ] || fail "Release package is incomplete"

if [ "$target" = uno-q ]; then
    [ "$(id -un)" = arduino ] || fail "Run the Uno Q command as arduino"
    python3 "$source/scripts/install.py" uno-q
    exit
fi

if [ "$(id -u)" -eq 0 ]; then
    as_root() { "$@"; }
else
    command -v sudo >/dev/null || fail "Run as root or install sudo"
    as_root() { sudo "$@"; }
fi
if [ -f /userdata/system/batocera.conf ] && [ -d /usr/lib/libretro ]; then
    platform=batocera
    as_root python3 "$source/scripts/install_batocera.py" --controller "$2"
    token=/userdata/system/rob-vision/token
    pair=/userdata/system/rob-vision/tools/retropie_pair.py
else
    [ -d /opt/retropie/configs ] || fail "This console is neither a supported RetroPie nor Batocera installation"
    platform=retropie
    as_root python3 "$source/scripts/install.py" retropie --controller "$2"
    token=/home/pi/.config/rob-vision/token
    pair=/home/pi/rob-vision/tools/retropie_pair.py
fi
if as_root test -s "$token" && [ "${3:-}" != --pair ]; then
    echo "R.O.B. Vision $VERSION installed; existing pairing retained."
else
    echo "Installation is complete. Enter the following pairing details on the Uno Q Setup page."
    as_root python3 "$pair" --platform "$platform" --token-file "$token"
fi
