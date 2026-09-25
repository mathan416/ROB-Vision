#!/usr/bin/env python3
"""Register R.O.B. Vision frame proxies and retain each game's NES core choice."""

import argparse
import re
import shutil
from pathlib import Path

BUILD = Path('/home/pi/rob-vision/build')
CORES = {
    'fceumm': (BUILD / 'rob_vision_fceumm_libretro.so',
               Path('/opt/retropie/libretrocores/lr-fceumm/fceumm_libretro.so')),
    'nestopia': (BUILD / 'rob_vision_nestopia_libretro.so',
                Path('/opt/retropie/libretrocores/lr-nestopia/nestopia_libretro.so')),
}
ROM_KEYS = ('nes_GyromiteWorld', 'nes_Stack-UpWorld')


def get_entry(path, key):
    if not path.exists():
        return None
    pattern = re.compile(r'^\s*' + re.escape(key) + r'\s*=\s*"([^"]+)"\s*$')
    for line in path.read_text().splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1)
    return None


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


def selected_core(value):
    for core in CORES:
        if value in ('lr-' + core, 'lr-robvision-' + core):
            return core
    return None


def install(root, proxy=None, real=None, choices=None, cores=None):
    """Install available cores; explicit choices may select either per ROM.

    proxy/real retain the original FCEUmm installer API for local installations.
    An unknown pre-existing per-ROM emulator choice is left untouched.
    """
    cores = dict(CORES if cores is None else cores)
    if proxy is not None or real is not None:
        cores['fceumm'] = (Path(proxy or CORES['fceumm'][0]),
                           Path(real or CORES['fceumm'][1]))
    choices = choices or {}
    available = {}
    for core, (core_proxy, core_real) in cores.items():
        if core_proxy.is_file() and core_real.is_file():
            available[core] = core_proxy
        elif choices.get('nes_GyromiteWorld') == core or choices.get('nes_Stack-UpWorld') == core:
            raise FileNotFoundError('Requested {} proxy and real core must both exist'.format(core))
    if not available:
        raise FileNotFoundError('Build a frame proxy and verify its real NES core first.')

    emulators = root / 'nes' / 'emulators.cfg'
    overrides = root / 'all' / 'emulators.cfg'
    default = selected_core(get_entry(emulators, 'default'))
    for core, core_proxy in available.items():
        command = ('/opt/retropie/emulators/retroarch/bin/retroarch -L {} '
                   '--config /opt/retropie/configs/nes/retroarch.cfg %ROM%').format(core_proxy)
        set_entry(emulators, 'lr-robvision-' + core, command)
    for key in ROM_KEYS:
        previous = get_entry(overrides, key)
        wanted = choices.get(key) or selected_core(previous) or (default if previous is None else None)
        if wanted is None:
            continue
        if wanted not in available:
            if key in choices:
                raise FileNotFoundError('The {} frame proxy is not installed'.format(wanted))
            continue
        set_entry(overrides, key, 'lr-robvision-' + wanted)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-root', type=Path, default=Path('/opt/retropie/configs'))
    parser.add_argument('--gyromite-core', choices=tuple(CORES))
    parser.add_argument('--stack-up-core', choices=tuple(CORES))
    args = parser.parse_args()
    chosen = {'nes_GyromiteWorld': args.gyromite_core,
              'nes_Stack-UpWorld': args.stack_up_core}
    install(args.config_root, choices={key: value for key, value in chosen.items() if value})
