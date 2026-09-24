#!/usr/bin/env python3
"""Report derived R.O.B. optical commands from user-supplied NES ROM archives.

Reads ROMs in place from ZIP files. It does not write or redistribute ROM data.
The address constants were established by tracing the two supplied World builds.
"""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


GYROMITE_TABLE = 0xA6FC
STACK_TEMPLATE = 0xB24A  # First frame; B249 is the preceding jump-table byte.
STACK_PALETTE_POINTERS = 0x82E8

COMMANDS = {
    "0001": "reset/calibrate",
    "0010": "down 1 step",
    "0100": "left 1 station",
    "0101": "up 2 steps",
    "0110": "close grippers",
    "1000": "right 1 station",
    "1001": "head LED on",
    "1010": "open grippers",
    "1100": "up 1 step",
    "1101": "down 2 steps",
}


def read_nes(path: Path) -> bytes:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.lower().endswith(".nes")]
            if len(names) != 1:
                raise ValueError(f"{path}: expected one .nes entry, found {len(names)}")
            return archive.read(names[0])
    return path.read_bytes()


def prg_from_nes(data: bytes) -> bytes:
    if data[:4] != b"NES\x1a":
        raise ValueError("invalid iNES signature")
    if data[4] != 2 or data[5] != 1 or len(data) != 16 + 32768 + 8192:
        raise ValueError("expected this project's 32 KiB PRG / 8 KiB CHR World build")
    mapper = (data[6] >> 4) | (data[7] & 0xF0)
    if mapper != 0:
        raise ValueError(f"expected NROM (mapper 0), found mapper {mapper}")
    return data[16:16 + 32768]


def at(prg: bytes, address: int, count: int) -> bytes:
    return prg[address - 0x8000:address - 0x8000 + count]


def explain(bits: str) -> dict:
    if len(bits) != 13 or not bits.startswith("000101") or bits[7] != "1" or bits[9] != "1" or bits[11] != "1":
        raise ValueError(f"unexpected R.O.B. frame sequence: {bits}")
    variable = bits[6:13:2]
    return {"frames": bits, "wxyz": variable, "command_byte": f"0x{int(bits[5:], 2):02X}", "action": COMMANDS.get(variable, "unknown")}


def gyromite(prg: bytes) -> list[dict]:
    rows = []
    for slot in (1, 2, 3, 5, 6, 7, 8):
        palette_indices = at(prg, GYROMITE_TABLE + (slot - 1) * 13, 13)
        if any(value not in (3, 4) for value in palette_indices):
            raise ValueError(f"unexpected Gyromite table at slot {slot}")
        # Counter $49 starts at 13, skips that tick, then reads index 12..0.
        bits = "".join("1" if value == 4 else "0" for value in reversed(palette_indices))
        rows.append({"slot": slot, **explain(bits)})
    # $23=3 selects the black ($0F) palette; $23=4 selects green ($2A).
    if at(prg, 0xB404, 4) != bytes.fromhex("3f 00 20 0f") or at(prg, 0xB428, 4) != bytes.fromhex("3f 00 20 2a"):
        raise ValueError("Gyromite palette evidence differs from inspected build")
    return rows


def stack_up(prg: bytes) -> list[dict]:
    template = at(prg, STACK_TEMPLATE, 13)
    if template != bytes.fromhex("00 00 00 01 00 01 ff 01 ff 01 ff 01 ff"):
        raise ValueError("Stack-Up frame template differs from inspected build")
    if at(prg, STACK_PALETTE_POINTERS, 8) != bytes.fromhex("20 60 74 b5 98 b5 ac b5"):
        raise ValueError("Stack-Up palette pointers differ from inspected build")
    # The loop also reads B257 as a signed template entry on pass 14. The
    # command values fit in four bits, so this fifth shift produces dark.
    if at(prg, 0xB257, 1)[0] < 0x80:
        raise ValueError("Stack-Up trailing frame is no longer a shifted bit")
    if at(prg, 0xB598, 4) != bytes.fromhex("3f 00 10 0f") or at(prg, 0xB5AC, 4) != bytes.fromhex("3f 00 10 2a"):
        raise ValueError("Stack-Up palette evidence differs from inspected build")
    rows = []
    for value in range(1, 7):
        shifted = value
        bits = ""
        for frame in template:
            if frame == 0xFF:
                bits += str(shifted & 1)
                shifted >>= 1
            else:
                bits += str(frame)
        rows.append({"input_value": value, **explain(bits), "trailing_frame": "0"})
    return rows


def report(path: Path, game: str) -> dict:
    data = read_nes(path)
    prg = prg_from_nes(data)
    rows = gyromite(prg) if game == "gyromite" else stack_up(prg)
    return {"game": game, "source": str(path), "rom_sha256": hashlib.sha256(data).hexdigest(),
            "mapper": 0, "prg_kib": 32, "chr_kib": 8, "commands": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gyromite", type=Path, required=True)
    parser.add_argument("--stack-up", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps([report(args.gyromite, "gyromite"), report(args.stack_up, "stack-up")], indent=2))


if __name__ == "__main__":
    main()
