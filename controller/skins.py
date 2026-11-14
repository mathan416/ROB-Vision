"""Local, bounded artwork packs for the browser's Buddy model."""

import io
import json
import re
import secrets
import shutil
import struct
import threading
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path


SLOTS = (
    "head", "body", "left_upper_arm", "left_forearm", "right_upper_arm",
    "right_forearm", "left_hand", "right_hand", "background", "floor",
    "platform", "gyro_linkage", "holder_far", "holder_near", "spinner",
    "red_pad", "blue_pad", "stack_linkage", "stack_tray",
)
GAME_PIECE_SLOTS = frozenset((
    "gyro", "block_red", "block_white", "block_blue", "block_yellow", "block_green",
))
ARTIST_GUIDE = "R.O.B.-Vision-Buddy-Skin-Artist-Guide.pdf"
MAX_ASSET = 4 * 1024 * 1024
MAX_PACK = 24 * 1024 * 1024
MAX_SKINS = 16
SVG_TAGS = {
    "svg", "g", "defs", "path", "rect", "circle", "ellipse", "line", "polyline",
    "polygon", "linearGradient", "radialGradient", "stop", "clipPath", "mask",
    "title", "desc", "text", "tspan",
}
SVG_STYLE = {
    "fill", "fill-opacity", "stroke", "stroke-opacity", "stroke-width",
    "stroke-linecap", "stroke-linejoin", "stroke-dasharray", "opacity",
    "display", "font-family", "font-size", "font-weight", "text-anchor",
    "clip-path", "mask",
}
ID = re.compile(r"[0-9a-f]{16}\Z")


def _safe_text(value, field):
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 80:
        raise ValueError(f"{field} must be 1 to 80 characters.")
    return value.strip()


def validate_art(data, suffix):
    if not data or len(data) > MAX_ASSET:
        raise ValueError("Artwork must be between 1 byte and 4 MiB.")
    if suffix == ".png":
        if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
            raise ValueError("This file is not a PNG image.")
        width, height = struct.unpack(">II", data[16:24])
        if not (1 <= width <= 4096 and 1 <= height <= 4096):
            raise ValueError("PNG dimensions must be at most 4096 x 4096.")
        offset, image_data, ended = 8, False, False
        while offset + 12 <= len(data):
            length = struct.unpack(">I", data[offset:offset + 4])[0]
            end = offset + 12 + length
            if length > MAX_ASSET or end > len(data):
                raise ValueError("PNG has a damaged chunk.")
            chunk = data[offset + 4:offset + 8]
            body = data[offset + 8:offset + 8 + length]
            expected = struct.unpack(">I", data[end - 4:end])[0]
            if zlib.crc32(chunk + body) != expected:
                raise ValueError("PNG has a damaged chunk.")
            if offset == 8 and (chunk != b"IHDR" or length != 13):
                raise ValueError("PNG has an invalid header.")
            image_data |= chunk == b"IDAT"
            if chunk == b"IEND":
                ended = length == 0 and end == len(data)
                break
            offset = end
        if not image_data or not ended:
            raise ValueError("PNG is incomplete.")
        return
    if suffix != ".svg":
        raise ValueError("Artwork must be PNG or SVG.")
    if re.search(rb"<!\s*(?:DOCTYPE|ENTITY|\[CDATA)", data, re.I) or b"<?" in data.replace(b"<?xml", b"", 1):
        raise ValueError("SVG declarations and document types are not supported.")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError("SVG markup is not valid XML.") from exc
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("Artwork must have an SVG root element.")
    if "viewBox" not in root.attrib:
        raise ValueError("SVG artwork needs a viewBox.")
    for element in root.iter():
        if element.tag.removeprefix("{http://www.w3.org/2000/svg}") not in SVG_TAGS:
            raise ValueError("SVG contains an unsupported element.")
        for key, value in element.attrib.items():
            local = key.rsplit("}", 1)[-1].lower()
            if local.startswith("on") or local == "href" or key.startswith("{http://www.w3.org/1999/xlink}"):
                raise ValueError("SVG links and scripts are not allowed.")
            if local == "style":
                for declaration in value.split(";"):
                    if not declaration.strip():
                        continue
                    property_name, separator, css_value = declaration.partition(":")
                    if (not separator or property_name.strip().lower() not in SVG_STYLE
                            or not re.fullmatch(r"[A-Za-z0-9#(),.%\s_+\-]+", css_value.strip())):
                        raise ValueError("SVG uses unsupported styling.")
            if "url(" in value.lower():
                references = re.findall(r"url\(([^)]*)\)", value, re.I)
                if len(references) != value.lower().count("url(") or any(
                    not re.fullmatch(r"#[A-Za-z_][\w.-]*", reference.strip()) for reference in references
                ):
                    raise ValueError("SVG may refer only to definitions inside itself.")
            if re.search(r"(?:https?:|data:|javascript:)", value, re.I):
                raise ValueError("SVG cannot load external content.")


class SkinStore:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()

    def _path(self, skin_id):
        if not isinstance(skin_id, str) or not ID.fullmatch(skin_id):
            raise ValueError("Choose a saved skin.")
        path = self.root / skin_id
        if path.is_symlink():
            raise ValueError("Invalid skin directory.")
        return path

    def _read(self, skin_id):
        path = self._path(skin_id)
        if not path.is_dir():
            raise ValueError("Skin not found.")
        doc = json.loads((path / "skin.json").read_text())
        if doc.get("schema") != 1 or not isinstance(doc.get("assets"), dict):
            raise ValueError("Skin format is not supported.")
        return doc

    @staticmethod
    def _visible_assets(doc):
        """Keep obsolete game-piece entries on disk, but never offer or export them."""
        return {slot: filename for slot, filename in doc["assets"].items() if slot in SLOTS}

    @staticmethod
    def _check_slot(slot):
        if slot in GAME_PIECE_SLOTS:
            raise ValueError("Gyros and Stack-Up blocks keep their original artwork.")
        if slot not in SLOTS:
            raise ValueError("Unknown artwork part.")

    def active(self):
        try:
            skin_id = json.loads((self.root / "active.json").read_text()).get("id")
            if skin_id and self._path(skin_id).is_dir():
                return skin_id
        except (OSError, ValueError, TypeError):
            pass
        return "built-in"

    def listing(self):
        with self.lock:
            skins = [{"id": "built-in", "name": "Original Buddy", "artist": "R.O.B. Vision", "assets": {}}]
            for path in sorted(self.root.iterdir()):
                if path.is_dir() and not path.is_symlink() and ID.fullmatch(path.name):
                    try:
                        doc = self._read(path.name)
                        skins.append({"id": path.name, "name": doc["name"],
                                      "artist": doc["artist"], "assets": self._visible_assets(doc),
                                      "revision": doc.get("revision", 0)})
                    except (OSError, ValueError, KeyError, TypeError):
                        continue
            return {"active": self.active(), "skins": skins, "slots": list(SLOTS)}

    def create(self, name, artist):
        name, artist = _safe_text(name, "Name"), _safe_text(artist, "Artist")
        with self.lock:
            if len([p for p in self.root.iterdir() if p.is_dir() and ID.fullmatch(p.name)]) >= MAX_SKINS:
                raise ValueError("The skin library is full (16 skins).")
            skin_id = secrets.token_hex(8)
            path = self._path(skin_id)
            path.mkdir(mode=0o700)
            (path / "assets").mkdir(mode=0o700)
            self._write_json(path / "skin.json", {"schema": 1, "name": name, "artist": artist,
                                                   "revision": 0, "assets": {}})
            return skin_id

    @staticmethod
    def _write_json(path, value):
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(value, indent=2) + "\n")
        temporary.replace(path)

    def put_asset(self, skin_id, slot, suffix, data):
        self._check_slot(slot)
        suffix = suffix.lower()
        validate_art(data, suffix)
        with self.lock:
            doc = self._read(skin_id)
            path = self._path(skin_id)
            old = doc["assets"].get(slot)
            name = f"assets/{slot}{suffix}"
            target = path / name
            temporary = target.with_suffix(suffix + ".tmp")
            temporary.write_bytes(data)
            temporary.replace(target)
            doc["assets"][slot] = name
            doc["revision"] = doc.get("revision", 0) + 1
            self._write_json(path / "skin.json", doc)
            if old and old != name:
                (path / old).unlink(missing_ok=True)
            return doc

    def remove_asset(self, skin_id, slot):
        self._check_slot(slot)
        with self.lock:
            doc = self._read(skin_id)
            old = doc["assets"].pop(slot, None)
            doc["revision"] = doc.get("revision", 0) + 1
            self._write_json(self._path(skin_id) / "skin.json", doc)
            if old:
                (self._path(skin_id) / old).unlink(missing_ok=True)
            return doc

    def activate(self, skin_id):
        with self.lock:
            if skin_id != "built-in":
                self._read(skin_id)
            self._write_json(self.root / "active.json", {"id": skin_id})
            return self.listing()

    def delete(self, skin_id):
        with self.lock:
            self._read(skin_id)
            if self.active() == skin_id:
                self.activate("built-in")
            shutil.rmtree(self._path(skin_id))
            return self.listing()

    def asset(self, skin_id, slot):
        self._check_slot(slot)
        with self.lock:
            doc = self._read(skin_id)
            filename = doc["assets"].get(slot)
            if not filename or filename not in (f"assets/{slot}.png", f"assets/{slot}.svg"):
                raise ValueError("Artwork part not found.")
            path = self._path(skin_id) / filename
            if path.is_symlink():
                raise ValueError("Invalid artwork path.")
            data = path.read_bytes()
            validate_art(data, path.suffix)
            return data, "image/png" if path.suffix == ".png" else "image/svg+xml"

    def export(self, skin_id):
        with self.lock:
            doc = self._read(skin_id)
            doc = {**doc, "assets": self._visible_assets(doc)}
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("skin.json", json.dumps(doc, indent=2) + "\n")
                for slot in doc["assets"]:
                    data, _ = self.asset(skin_id, slot)
                    archive.writestr(doc["assets"][slot], data)
            return stream.getvalue()

    def import_pack(self, data):
        if not data or len(data) > MAX_PACK:
            raise ValueError("Skin pack must be at most 24 MiB.")
        try:
            archive = zipfile.ZipFile(io.BytesIO(data))
            files = {info.filename: info for info in archive.infolist()}
            if len(files) != len(archive.infolist()) or len(files) > 31 or "skin.json" not in files:
                raise ValueError("Skin pack has duplicate or unexpected files.")
            if any(name.startswith("/") or ".." in Path(name).parts or "\\" in name or info.is_dir()
                   or info.file_size > MAX_ASSET or (info.external_attr >> 16) & 0o170000 == 0o120000
                   for name, info in files.items()):
                raise ValueError("Skin pack contains an unsafe file.")
            if sum(info.file_size for info in files.values()) > 32 * 1024 * 1024:
                raise ValueError("Skin pack is too large.")
            doc = json.loads(archive.read("skin.json"))
            if not isinstance(doc, dict) or doc.get("schema") != 1 or not isinstance(doc.get("assets"), dict):
                raise ValueError("Skin pack needs a version 1 skin.json.")
            name, artist = _safe_text(doc.get("name"), "Name"), _safe_text(doc.get("artist"), "Artist")
            assets = doc["assets"]
            obsolete = sorted(GAME_PIECE_SLOTS.intersection(assets))
            if obsolete:
                raise ValueError("Remove game-piece entries from skin.json: " + ", ".join(obsolete))
            if any(slot not in SLOTS or filename not in (f"assets/{slot}.png", f"assets/{slot}.svg")
                   for slot, filename in assets.items()):
                raise ValueError("skin.json names an unknown part or file.")
            extra = set(files) - {"skin.json", *assets.values()}
            examples = {name for name in extra if any(name in (f"assets/{slot}.png", f"assets/{slot}.svg")
                                                     for slot in SLOTS)}
            if any(not (name == "README.txt" or name == ARTIST_GUIDE or name in examples or
                        name.startswith("reference/") and name.endswith((".svg", ".png", ".txt")))
                   for name in extra):
                raise ValueError("Every artwork file must match skin.json exactly.")
            checked = {slot: archive.read(filename) for slot, filename in assets.items()}
            for slot, body in checked.items():
                validate_art(body, Path(assets[slot]).suffix)
            for filename in examples:
                validate_art(archive.read(filename), Path(filename).suffix)
        except (zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
            raise ValueError("Skin pack is not a valid ZIP with skin.json.") from exc
        skin_id = self.create(name, artist)
        try:
            for slot, body in checked.items():
                self.put_asset(skin_id, slot, Path(assets[slot]).suffix, body)
        except Exception:
            shutil.rmtree(self._path(skin_id), ignore_errors=True)
            raise
        return skin_id
