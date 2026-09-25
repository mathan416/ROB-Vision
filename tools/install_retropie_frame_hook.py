#!/usr/bin/env python3
"""Select the FCEUmm frame proxy only for Gyromite and Stack-Up ROMs."""

import argparse
import re
import shutil
from pathlib import Path

PROXY = Path('/home/pi/rob-vision/build/rob_vision_fceumm_libretro.so')
REAL = Path('/opt/retropie/libretrocores/lr-fceumm/fceumm_libretro.so')
EMULATOR = 'lr-robvision-fceumm'
ROM_KEYS = ('nes_GyromiteWorld', 'nes_Stack-UpWorld')


def set_entry(path, key, value):
    original = path.read_text() if path.exists() else ''
    lines = original.splitlines()
    entry = '{} = "{}"'.format(key, value)
    pattern = re.compile(r'^\s*' + re.escape(key) + r'\s*=')
    matched = [i for i, line in enumerate(lines) if pattern.match(line)]
    if matched:
        lines[matched[0]] = entry
        for index in reversed(matched[1:]):
            del lines[index]
    else:
        lines.append(entry)
    changed = '\n'.join(lines) + '\n'
    if changed != original:
        backup = path.with_name(path.name + '.before-rob-vision-frame-hook')
        if path.exists() and not backup.exists():
            shutil.copy2(path, backup)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(changed)


def install(root, proxy=PROXY, real=REAL):
    if not proxy.is_file() or not real.is_file():
        raise FileNotFoundError('Build the frame proxy and verify the real FCEUmm core first.')
    command = ('/opt/retropie/emulators/retroarch/bin/retroarch -L {} '
               '--config /opt/retropie/configs/nes/retroarch.cfg %ROM%').format(proxy)
    set_entry(root / 'nes' / 'emulators.cfg', EMULATOR, command)
    for key in ROM_KEYS:
        set_entry(root / 'all' / 'emulators.cfg', key, EMULATOR)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-root', type=Path, default=Path('/opt/retropie/configs'))
    args = parser.parse_args()
    install(args.config_root)
