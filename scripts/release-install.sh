#!/bin/sh
# Rendered with a version and source-archive digest by package_release.py.
set -eu
export PYTHONDONTWRITEBYTECODE=1
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
cleanup() {
    if [ "$target" = console ] && [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null; then
        sudo -n rm -rf "$work" 2>/dev/null || rm -rf "$work"
    else
        rm -rf "$work"
    fi
}
trap cleanup 0 HUP INT TERM
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
    as_root() { PYTHONDONTWRITEBYTECODE=1 "$@"; }
else
    command -v sudo >/dev/null || fail "Run as root or install sudo"
    as_root() { sudo env PYTHONDONTWRITEBYTECODE=1 "$@"; }
fi
if [ -f /userdata/system/batocera.conf ] && [ -d /usr/lib/libretro ]; then
    platform=batocera
    as_root python3 "$source/scripts/install_batocera.py" --controller "$2"
    token=/userdata/system/rob-vision/token
    pair=/userdata/system/controller-router/pair-console
elif [ -f /recalbox/recalbox.version ] && [ -d /usr/lib/libretro ]; then
    platform=recalbox
    as_root python3 "$source/scripts/install_recalbox.py" --controller "$2"
    token=/recalbox/share/system/rob-vision/token
    pair=/recalbox/share/system/controller-router/pair-console
else
    [ -d /opt/retropie/configs ] || fail "This console is not a supported RetroPie, Batocera, or Recalbox installation"
    platform=retropie
    as_root python3 "$source/scripts/install.py" retropie --controller "$2"
    token=/home/pi/.config/rob-vision/token
    pair=/var/lib/controller-router/pair-console
fi
if as_root test -s "$token" && [ "${3:-}" != --pair ]; then
    echo "R.O.B. Vision $VERSION installed; existing pairing retained."
else
    echo "Installation is complete. Enter the following pairing details on the Uno Q Setup page."
    as_root sh "$pair"
fi
