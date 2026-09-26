#!/bin/sh
# Rebuild the Batocera libretro wrappers for its Linux CPU families.
# Zig 0.15.2 (or a compatible Zig cc) supplies cross-platform glibc headers.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
SOURCE="$ROOT/deploy/retropie/rob_vision_fceumm_proxy.c"
ZIG=${ZIG:-zig}
"$ZIG" version >/dev/null

scratch=$(mktemp -d "${TMPDIR:-/tmp}/robvision-build.XXXXXX")
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
export ZIG_GLOBAL_CACHE_DIR="$scratch/global-cache"
export ZIG_LOCAL_CACHE_DIR="$scratch/local-cache"

build_arch() {
    arch=$1
    target=$2
    cpu=$3
    output="$ROOT/deploy/batocera/cores/$arch"
    set --
    if [ "$cpu" != auto ]; then set -- "-mcpu=$cpu"; fi
    mkdir -p "$output"
    for core in fceumm nestopia; do
        # The same proxy source wraps either installed stock core.
        if [ "$core" = nestopia ]; then
            "$ZIG" cc -target "$target" "$@" -std=gnu11 -O2 -g0 \
                -fPIC -shared -Wall -Wextra -DROB_USE_NESTOPIA \
                '-DROB_REAL_CORE_PATH="/usr/lib/libretro/nestopia_libretro.so"' \
                -o "$output/robvision_nestopia_libretro.so" "$SOURCE" -ldl
        else
            "$ZIG" cc -target "$target" "$@" -std=gnu11 -O2 -g0 \
                -fPIC -shared -Wall -Wextra \
                '-DROB_REAL_CORE_PATH="/usr/lib/libretro/fceumm_libretro.so"' \
                -o "$output/robvision_fceumm_libretro.so" "$SOURCE" -ldl
        fi
    done
    printf '%s: %s\n' "$arch" "$target"
}

build_arch x86_64 x86_64-linux-gnu.2.17 auto
build_arch x86 x86-linux-gnu.2.17 auto
build_arch aarch64 aarch64-linux-gnu.2.17 auto
build_arch armv7l arm-linux-gnueabihf.2.17 generic+v7a
build_arch armv6l arm-linux-gnueabihf.2.17 arm1176jzf_s
build_arch riscv64 riscv64-linux-gnu.2.27 auto
