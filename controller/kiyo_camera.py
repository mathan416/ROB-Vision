"""Apply the tested, volatile 60 fps mode to an identified Razer Kiyo Pro."""

import ctypes
import fcntl
import os
from pathlib import Path
import struct
import sys


_GUID = bytes.fromhex("d09ee4237811314fae52d2fb8a8d3b48")
_HDR_OFF = bytes.fromhex("ff02000000000000")


class _ExtensionQuery(ctypes.Structure):
    _fields_ = [("unit", ctypes.c_uint8), ("selector", ctypes.c_uint8),
                ("query", ctypes.c_uint8), ("size", ctypes.c_uint16),
                ("data", ctypes.c_void_p)]


def _extension_unit(descriptors):
    offset = 0
    while offset + 2 <= len(descriptors):
        size = descriptors[offset]
        if size < 2 or offset + size > len(descriptors):
            raise ValueError("Malformed camera USB descriptors")
        block = descriptors[offset:offset + size]
        if len(block) >= 20 and block[1:3] == b"\x24\x06" and block[4:20] == _GUID:
            return block[3]
        offset += size
    raise ValueError("Kiyo Pro HDR control was not found")


def configure_kiyo_pro(device, sysfs=Path("/sys/class/video4linux")):
    """Return False for other cameras; configure a Kiyo Pro without saving to it."""
    if not sys.platform.startswith("linux"):
        return False
    name = Path(str(device)).name
    if not name.startswith("video") or not name[5:].isdigit():
        return False
    path = (sysfs / name).resolve()
    usb = next((parent for parent in path.parents if (parent / "idVendor").is_file()), None)
    if (usb is None or (usb / "idVendor").read_text().strip() != "1532" or
            (usb / "idProduct").read_text().strip() != "0e05"):
        return False
    unit = _extension_unit((usb / "descriptors").read_bytes())
    fd = os.open("/dev/" + name, os.O_RDWR)
    try:
        request = (3 << 30) | (ctypes.sizeof(_ExtensionQuery) << 16) | (ord("u") << 8) | 0x21
        size = ctypes.c_uint16()
        fcntl.ioctl(fd, request, _ExtensionQuery(unit, 1, 0x85, 2, ctypes.addressof(size)))
        if not 8 <= size.value <= 64:
            raise ValueError("Unexpected Kiyo Pro HDR control size")
        payload = ctypes.create_string_buffer(size.value)
        payload[0:8] = _HDR_OFF
        fcntl.ioctl(fd, request, _ExtensionQuery(unit, 1, 0x01, size.value, ctypes.addressof(payload)))
        for control, value in ((0x009A0901, 3), (0x009A0903, 0)):
            fcntl.ioctl(fd, 0xC008561C, bytearray(struct.pack("Ii", control, value)))
        for control, expected in ((0x009A0901, 3), (0x009A0903, 0)):
            result = bytearray(struct.pack("Ii", control, 0))
            fcntl.ioctl(fd, 0xC008561B, result)
            if struct.unpack("Ii", result)[1] != expected:
                raise RuntimeError("Kiyo Pro exposure control did not take effect")
    finally:
        os.close(fd)
    return True
