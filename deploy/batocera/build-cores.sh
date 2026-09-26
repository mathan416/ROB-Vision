#!/bin/sh
# Build the two small wrapper libraries on an x86_64 Linux host with GCC.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
OUT="$ROOT/deploy/batocera/cores/x86_64"
mkdir -p "$OUT"
SOURCE="$ROOT/deploy/retropie/rob_vision_fceumm_proxy.c"
"${CC:-gcc}" -std=gnu11 -O2 -fPIC -shared -Wall -Wextra \
    '-DROB_REAL_CORE_PATH="/usr/lib/libretro/fceumm_libretro.so"' \
    '-DROB_PAD_RETURN_PATH="/run/rob-vision/pads"' \
    -o "$OUT/robvision_fceumm_libretro.so" "$SOURCE" -ldl
"${CC:-gcc}" -std=gnu11 -O2 -fPIC -shared -Wall -Wextra -DROB_USE_NESTOPIA \
    '-DROB_REAL_CORE_PATH="/usr/lib/libretro/nestopia_libretro.so"' \
    '-DROB_PAD_RETURN_PATH="/run/rob-vision/pads"' \
    -o "$OUT/robvision_nestopia_libretro.so" "$SOURCE" -ldl
