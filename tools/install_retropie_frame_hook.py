#!/usr/bin/env python3
"""Register R.O.B. Vision frame proxies and retain each game's NES core choice."""

import argparse
import os
import pwd
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.identify_game import DEFAULT_REGISTRY, registry_roms, retropie_override_key

BUILD = Path('/home/pi/rob-vision/build')
CORES = {
    'fceumm': (BUILD / 'rob_vision_fceumm_libretro.so',
               Path('/opt/retropie/libretrocores/lr-fceumm/fceumm_libretro.so')),
    'nestopia': (BUILD / 'rob_vision_nestopia_libretro.so',
                Path('/opt/retropie/libretrocores/lr-nestopia/nestopia_libretro.so')),
}
def get_entry(path, key):
    if not path.exists():
        return None
    pattern = re.compile(r'^\s*' + re.escape(key) + r'\s*=\s*"([^"]+)"\s*$')
    for line in path.read_text().splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1)
    return None


def set_entry(path, key, value, owner=None):
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
    if owner is not None and os.geteuid() == 0:
        os.chown(path, owner.pw_uid, owner.pw_gid)
        backup = path.with_name(path.name + '.before-rob-vision-frame-hook')
        if backup.exists():
            os.chown(backup, owner.pw_uid, owner.pw_gid)


def selected_core(value):
    for core in CORES:
        if value in ('lr-' + core, 'lr-robvision-' + core):
            return core
    return None


def install(root, proxy=None, real=None, choices=None, cores=None, registry_path=DEFAULT_REGISTRY,
            roms=Path('/home/pi/RetroPie/roms/nes')):
    """Install available cores; explicit choices may select either per ROM.

    proxy/real retain the original FCEUmm installer API for local installations.
    An unknown pre-existing per-ROM emulator choice is left untouched.
    """
    cores = dict(CORES if cores is None else cores)
    if proxy is not None or real is not None:
        cores['fceumm'] = (Path(proxy or CORES['fceumm'][0]),
                           Path(real or CORES['fceumm'][1]))
    choices = choices or {}
    mappings = registry_roms(registry_path)
    # The registry matches without case, but RetroPie's per-ROM key keeps the
    # real filename's capitalization. Prefer the file on disk when present.
    actual_names = {rom.name.casefold(): rom.name for rom in roms.iterdir() if rom.is_file()} if roms.is_dir() else {}
    rom_keys = {}
    for filename, game in mappings.items():
        key = retropie_override_key(actual_names.get(filename.casefold(), filename))
        if key in rom_keys and rom_keys[key] != game:
            raise ValueError(f"RetroPie ROM choice collision for {filename!r}")
        rom_keys[key] = game
    available = {}
    for core, (core_proxy, core_real) in cores.items():
        if core_proxy.is_file() and core_real.is_file():
            available[core] = core_proxy
        elif any(choices.get(key) == core for key in rom_keys):
            raise FileNotFoundError('Requested {} proxy and real core must both exist'.format(core))
    if not available:
        raise FileNotFoundError('Build a frame proxy and verify its real NES core first.')

    emulators = root / 'nes' / 'emulators.cfg'
    overrides = root / 'all' / 'emulators.cfg'
    owner = pwd.getpwnam('pi') if root.resolve() == Path('/opt/retropie/configs') else None
    default = selected_core(get_entry(emulators, 'default'))
    for core, core_proxy in available.items():
        command = ('/opt/retropie/emulators/retroarch/bin/retroarch -L {} '
                   '--config /opt/retropie/configs/nes/retroarch.cfg %ROM%').format(core_proxy)
        set_entry(emulators, 'lr-robvision-' + core, command, owner=owner)
    for key in rom_keys:
        previous = get_entry(overrides, key)
        wanted = choices.get(key) or selected_core(previous) or (default if previous is None else None)
        if wanted is None:
            continue
        if wanted not in available:
            if key in choices:
                raise FileNotFoundError('The {} frame proxy is not installed'.format(wanted))
            continue
        set_entry(overrides, key, 'lr-robvision-' + wanted, owner=owner)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-root', type=Path, default=Path('/opt/retropie/configs'))
    parser.add_argument('--gyromite-core', choices=tuple(CORES))
    parser.add_argument('--stack-up-core', choices=tuple(CORES))
    args = parser.parse_args()
    chosen = {retropie_override_key(filename): args.gyromite_core if game == 'gyromite'
              else args.stack_up_core for filename, game in registry_roms().items()}
    install(args.config_root, choices={key: value for key, value in chosen.items() if value})
