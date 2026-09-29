"""Register Buddy's NES frame cores and exact ROM choices on Recalbox."""

from __future__ import annotations

import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.identify_game import identify, load_registry

SYSTEM_LIST = Path('/recalbox/share_init/system/.emulationstation/systemlist.xml')
ROM_ROOT = Path('/recalbox/share/roms/nes')


def systemlist_text(current: str, available=('fceumm', 'nestopia')) -> str:
    root = ET.fromstring(current)
    systems = [item for item in root.findall('system') if item.get('name') == 'nes']
    if len(systems) != 1:
        raise ValueError('Recalbox NES system was not found uniquely.')
    emulators = [item for item in systems[0].findall('./emulatorList/emulator')
                 if item.get('name') == 'libretro']
    if len(emulators) != 1:
        raise ValueError('Recalbox NES Libretro emulator was not found uniquely.')
    emulator = emulators[0]
    for core in available:
        name = 'robvision_' + core
        matches = [item for item in emulator.findall('core') if item.get('name') == name]
        if len(matches) > 1:
            raise ValueError('Duplicate Buddy core in Recalbox system list.')
        attributes = {'name': name, 'priority': '250',
                      'extensions': '.nes .unf .unif .zip! .7z!', 'netplay': '0',
                      'softpatching': '1', 'compatibility': 'high', 'speed': 'high',
                      'crt.available': '1', 'video.backend': 'default'}
        if matches:
            matches[0].attrib.clear(); matches[0].attrib.update(attributes)
        else:
            ET.SubElement(emulator, 'core', attributes)
    ET.indent(root, space='  ')
    return '<?xml version="1.0" ?>\n' + ET.tostring(root, encoding='unicode') + '\n'


def selected_core(current: str) -> str | None:
    for line in current.splitlines():
        if line.strip().startswith(('#', ';')) or '=' not in line:
            continue
        key, value = line.split('=', 1)
        if key.strip() == 'nes.core':
            return value.strip()
    return None


def sidecar_text(current: str, core: str) -> str:
    lines = [line for line in current.splitlines()
             if line.split('=', 1)[0].strip() not in ('nes.core', 'nes.emulator')
             and line != '# R.O.B. Vision game core']
    if lines and lines[-1]:
        lines.append('')
    lines.extend(('# R.O.B. Vision game core', 'nes.emulator=libretro',
                  'nes.core=robvision_' + core))
    return '\n'.join(lines).rstrip() + '\n'


def write_atomic(path: Path, content: str):
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError('Refusing symbolic Recalbox configuration path.')
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, prefix='.rob-vision-',
                                     delete=False) as stream:
        stream.write(content)
        stream.flush()
        temporary = Path(stream.name)
    temporary.chmod(0o644)
    temporary.replace(path)


def select_games(registry_path: Path, rom_root=ROM_ROOT, available=('fceumm', 'nestopia')):
    registry = load_registry(registry_path)
    chosen = []
    for rom in sorted(rom_root.iterdir()):
        if not rom.is_file() or not identify('nes', rom.name, registry):
            continue
        sidecar = rom.with_name(rom.name + '.recalbox.conf')
        original = sidecar.read_text() if sidecar.is_file() else ''
        selected = selected_core(original)
        if selected and selected not in ('fceumm', 'nestopia', 'robvision_fceumm',
                                         'robvision_nestopia'):
            continue
        core = 'nestopia' if selected and selected.endswith('nestopia') else 'fceumm'
        if core not in available:
            core = available[0]
        updated = sidecar_text(original, core)
        if updated != original:
            backup = sidecar.with_name(sidecar.name + '.before-rob-vision')
            if sidecar.is_file() and not backup.exists():
                shutil.copy2(sidecar, backup)
            write_atomic(sidecar, updated)
        chosen.append(rom.name)
    return chosen
