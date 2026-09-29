#!/usr/bin/env python3
"""Install R.O.B. Vision and the shared Router on Recalbox 10.x."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.install import copy_file, copy_tree_merge, valid_controller, write_file, validate_receiver_source
from tools.identify_game import load_registry
from tools.recalbox import select_games

DEST = Path('/recalbox/share/system/rob-vision')
SYSTEM = Path('/recalbox/share/system')


def custom_hook(text):
    begin, end = '# BEGIN R.O.B. Vision service', '# END R.O.B. Vision service'
    block = (begin + '\ncase "$1" in\n'
             'start) sh /recalbox/share/system/rob-vision/deploy/recalbox/rob-vision-service start;;\n'
             'stop) sh /recalbox/share/system/rob-vision/deploy/recalbox/rob-vision-service stop;;\n'
             'esac\n' + end)
    if begin in text:
        start, finish = text.index(begin), text.index(end) + len(end)
        return text[:start] + block + text[finish:]
    return text.rstrip() + '\n' + block + '\n'


def wrapper_files(source=ROOT):
    aliases = {'armv8l': 'armv7l', 'armv7': 'armv7l', 'amd64': 'x86_64'}
    arch = aliases.get(platform.machine().lower(), platform.machine().lower())
    bundled = source / 'deploy/batocera/cores' / arch
    found = {}
    for core in ('fceumm', 'nestopia'):
        if not Path('/usr/lib/libretro', core + '_libretro.so').is_file():
            continue
        candidate = bundled / ('robvision_' + core + '_libretro.so')
        if not candidate.is_file():
            raise RuntimeError('No R.O.B. Vision ' + arch + ' wrapper for ' + core + '.')
        ctypes.CDLL(str(candidate))
        found[core] = candidate
    if not found:
        raise RuntimeError('Recalbox needs an installed FCEUmm or Nestopia Libretro core.')
    return found


def install(controller, source=ROOT, destination=DEST):
    if sys.platform != 'linux' or os.geteuid() != 0:
        raise RuntimeError('Run this installer as root on Recalbox.')
    version_file = Path('/recalbox/recalbox.version')
    if not version_file.is_file() or not version_file.read_text().strip().startswith('10.'):
        raise RuntimeError('Recalbox 10.x is required.')
    if subprocess.run(['pgrep', '-x', 'retroarch'], stdout=subprocess.DEVNULL).returncode == 0:
        raise RuntimeError('Exit the running game before installing.')
    if not Path('/dev/uinput').exists():
        raise RuntimeError('Recalbox virtual-input support is missing.')
    valid_controller(controller)
    validate_receiver_source(source)
    libraries = wrapper_files(source)
    registry_source = (destination / 'config/games.json'
                       if (destination / 'config/games.json').is_file() else source / 'config/games.json')
    load_registry(registry_source)
    menu = Path("/etc/init.d/S31emulationstation")
    menu_running = subprocess.run(["pidof", "emulationstation"],
                                  stdout=subprocess.DEVNULL).returncode == 0
    if menu_running:
        subprocess.run(["sh", str(menu), "stop"], check=True)
    try:
        service = destination / 'deploy/recalbox/rob-vision-service'
        if service.is_file():
            subprocess.run(['sh', str(service), 'stop'], check=True)
        destination.mkdir(parents=True, exist_ok=True)
        for folder in ('tools', 'controller', 'config', 'router_shared', 'deploy/recalbox'):
            copy_tree_merge(source / folder, destination / folder,
                            preserve_registry=(folder == 'config'))
        for library in libraries.values():
            copy_file(library, destination / 'build' / library.name, 0o755)
        write_file(destination / 'controller.url', 'http://' + controller + ':8766\n', 0o600)
        token = destination / 'token'
        if not token.exists():
            write_file(token, '', 0o600)
        custom = SYSTEM / 'custom.sh'
        write_file(custom, custom_hook(custom.read_text() if custom.is_file() else '#!/bin/sh\n'), 0o755)
        router_path = SYSTEM / 'virtualglove/data/controller-router.json'
        if not router_path.is_file():
            from router_shared.controller_router import FORMAT, validate_config, _saved_source
            from router_shared.merged_gamepad import controller_candidates
            es = SYSTEM / '.emulationstation/es_input.cfg'
            candidates = [item for item in controller_candidates(es)
                          if item['name'] != 'R.O.B. Vision Controller 2'
                          and not item['name'].startswith('VirtualGlove Merged Player')]
            players = [{'player': number, 'sources': [_saved_source(item)]}
                       for number, item in enumerate(candidates[:4], 1)]
            config = validate_config({'format': FORMAT, 'platform': 'recalbox',
                                      'players': players, 'virtualglove_player': None,
                                      'physical_scope': 'nes'})
            write_file(router_path, json.dumps(config, indent=2) + '\n', 0o600)
        from router_shared.launch_install import install_recalbox as install_session_routing
        install_session_routing()
        chosen = select_games(registry_path=destination / 'config/games.json', available=tuple(libraries))
        subprocess.run(['sh', str(service), 'start'], check=True)
        from router_shared.pairing_install import install as install_link
        install_link('rob_vision', {'kind': 'text', 'token_file': str(token),
            'target_file': str(destination / 'controller.url'),
            'identity_file': str(destination / 'console-id'),
            'restart': ['sh', str(service), 'restart'],
            'setup': ['python3', str(destination / 'tools/controller_router_setup.py'),
                      'recalbox', '--pair-only'],
            'backup_files': [str(router_path), str(router_path) + '.previous',
                             str(SYSTEM / '.emulationstation/es_input.cfg')],
            'stop': ['sh', str(service), 'stop']})
    finally:
        if menu_running:
            subprocess.run(["sh", str(menu), "start"], check=True)
    print('Installed R.O.B. Vision for:', ', '.join(chosen) or 'no registered ROMs present')
    if token.stat().st_size:
        print('Existing Controller Router pairing retained.')
    else:
        print('Pair once in Controller Router > Setup > Pair console.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controller', required=True, help='UNO Q hostname or LAN IP')
    args = parser.parse_args()
    try:
        install(args.controller)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        parser.exit(1, 'Installation stopped: {}\n'.format(exc))


if __name__ == '__main__':
    main()
