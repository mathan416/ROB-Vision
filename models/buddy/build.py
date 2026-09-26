#!/usr/bin/env python3
"""Build Buddy's single-color STL and four/six-color multipart 3MF files.

Requires OpenSCAD on PATH. No Python packages beyond the standard library.
"""

from __future__ import annotations

import os
import platform
import shutil
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "Buddy.scad"
PARTS = HERE / "parts"
PARTS_4 = HERE / "parts-4"

# Earlier colors carve later colors. This gives each printable volume its own
# closed mesh and leaves no overlapping material volumes inside the 3MF.
COLORS = [
    ("white", "#FFFFFFFF"),
    ("cyan", "#4DE5EEFF"),
    ("orange", "#EF765EFF"),
    ("shell", "#ECEAE4FF"),
    ("navy_light", "#34465DFF"),
    ("navy", "#182A42FF"),
]
FOUR_COLORS = [
    ("shell", "#ECEAE4FF", "shell4"),
    ("cyan", "#4DE5EEFF", "cyan"),
    ("orange", "#EF765EFF", "orange"),
    ("navy", "#182A42FF", "navy4"),
]

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>"""
RELS = """<?xml version="1.0" encoding="utf-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" Target="/3D/3dmodel.model" Id="rel0"/>
</Relationships>"""


def openscad_command() -> list[str]:
    binary = shutil.which(os.environ.get("OPENSCAD", "openscad"))
    if binary is None:
        raise SystemExit("OpenSCAD was not found on PATH")
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        return ["arch", "-x86_64", binary]
    return [binary]


def export(command: list[str], scad: Path, stl: Path, definition: str | None = None) -> None:
    args = command + ["--export-format", "binstl", "-o", str(stl)]
    if definition:
        args += ["-D", definition]
    args.append(str(scad))
    subprocess.run(args, check=True, capture_output=True, text=True)


def read_stl(path: Path) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError(f"Invalid STL: {path}")
    count = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + 50 * count:
        raise ValueError(f"Invalid triangle count: {path}")

    vertices: list[tuple[float, float, float]] = []
    triangles: list[tuple[int, int, int]] = []
    indices: dict[tuple[float, float, float], int] = {}
    for offset in range(84, len(data), 50):
        row = struct.unpack_from("<12f", data, offset)
        coords = [tuple(row[start : start + 3]) for start in (3, 6, 9)]
        if len(set(coords)) < 3:
            continue  # OpenSCAD can emit zero-area STL faces at boolean seams.
        face = []
        for xyz in coords:
            if xyz not in indices:
                indices[xyz] = len(vertices)
                vertices.append(xyz)
            face.append(indices[xyz])
        triangles.append(tuple(face))
    return vertices, triangles


def check_mesh(path: Path) -> float:
    vertices, triangles = read_stl(path)
    edges: Counter[tuple[int, int]] = Counter()
    signed_volume = 0.0
    for a, b, c in triangles:
        for x, y in ((a, b), (b, c), (c, a)):
            edges[tuple(sorted((x, y)))] += 1
        v0, v1, v2 = vertices[a], vertices[b], vertices[c]
        signed_volume += (
            v0[0] * (v1[1] * v2[2] - v1[2] * v2[1])
            + v0[1] * (v1[2] * v2[0] - v1[0] * v2[2])
            + v0[2] * (v1[0] * v2[1] - v1[1] * v2[0])
        ) / 6
    if not triangles or any(count != 2 for count in edges.values()):
        raise ValueError(f"Open or invalid mesh: {path}")
    return abs(signed_volume)


def assemble_3mf(groups: list[tuple[str, str, Path]], target: Path) -> None:
    ET.register_namespace("", CORE)
    model = ET.Element(f"{{{CORE}}}model", {"unit": "millimeter", "{http://www.w3.org/XML/1998/namespace}lang": "en-US"})
    ET.SubElement(model, f"{{{CORE}}}metadata", {"name": "Title"}).text = f"Buddy {len(groups)}-color figure"
    resources = ET.SubElement(model, f"{{{CORE}}}resources")
    materials = ET.SubElement(resources, f"{{{CORE}}}basematerials", {"id": "1"})
    for name, color, _ in groups:
        ET.SubElement(materials, f"{{{CORE}}}base", {"name": name, "displaycolor": color})

    for color_index, (name, _, path) in enumerate(groups):
        vertices, triangles = read_stl(path)
        obj_id = str(color_index + 2)
        obj = ET.SubElement(resources, f"{{{CORE}}}object", {
            "id": obj_id, "name": f"Buddy - {name.replace('_', ' ')}", "type": "model",
            "pid": "1", "pindex": str(color_index),
        })
        mesh = ET.SubElement(obj, f"{{{CORE}}}mesh")
        verts_node = ET.SubElement(mesh, f"{{{CORE}}}vertices")
        for x, y, z in vertices:
            ET.SubElement(verts_node, f"{{{CORE}}}vertex", {
                "x": format(x, ".9g"), "y": format(y, ".9g"), "z": format(z, ".9g")
            })
        tris_node = ET.SubElement(mesh, f"{{{CORE}}}triangles")
        for a, b, c in triangles:
            ET.SubElement(tris_node, f"{{{CORE}}}triangle", {
                "v1": str(a), "v2": str(b), "v3": str(c),
                "pid": "1", "p1": str(color_index),
            })

    assembly_id = str(len(groups) + 2)
    assembly = ET.SubElement(resources, f"{{{CORE}}}object", {
        "id": assembly_id, "name": "Buddy (multicolor)", "type": "model",
    })
    components = ET.SubElement(assembly, f"{{{CORE}}}components")
    for index in range(len(groups)):
        ET.SubElement(components, f"{{{CORE}}}component", {"objectid": str(index + 2)})
    build = ET.SubElement(model, f"{{{CORE}}}build")
    ET.SubElement(build, f"{{{CORE}}}item", {"objectid": assembly_id})

    with ZipFile(target, "w", ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", RELS)
        archive.writestr("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True))


def main() -> None:
    command = openscad_command()
    PARTS.mkdir(exist_ok=True)
    PARTS_4.mkdir(exist_ok=True)
    export(command, SOURCE, HERE / "Buddy.stl")
    with tempfile.TemporaryDirectory(prefix="buddy-build-") as temp_name:
        temp = Path(temp_name)
        raw: dict[str, Path] = {}
        for name, _ in COLORS:
            raw[name] = temp / f"raw-{name}.stl"
            export(command, SOURCE, raw[name], f'part="{name}"')

        output_parts: list[Path] = []
        for index, (name, _) in enumerate(COLORS):
            target = PARTS / f"Buddy-{name}.stl"
            if index == 0:
                shutil.copyfile(raw[name], target)
            else:
                cuts = "\n".join(f'import("{raw[higher]}");' for higher, _ in COLORS[:index])
                csg = temp / f"cut-{name}.scad"
                csg.write_text(f'difference() {{ import("{raw[name]}"); union() {{ {cuts} }} }}\n')
                export(command, csg, target)
            output_parts.append(target)

    whole_volume = check_mesh(HERE / "Buddy.stl")
    parts_volume = sum(check_mesh(path) for path in output_parts)
    if abs(parts_volume - whole_volume) > whole_volume * 0.0001:
        raise ValueError("Color part volumes do not reconstruct the one-piece STL")
    six_groups = [(name, color, path) for (name, color), path in zip(COLORS, output_parts)]
    assemble_3mf(six_groups, HERE / "Buddy-6-color.3mf")
    shutil.copyfile(HERE / "Buddy-6-color.3mf", HERE / "Buddy.3mf")

    four_groups = []
    with tempfile.TemporaryDirectory(prefix="buddy-four-") as temp_name:
        temp = Path(temp_name)
        raw_four = {}
        for name, _, selector in FOUR_COLORS:
            raw_four[name] = temp / f"raw-{name}.stl"
            export(command, SOURCE, raw_four[name], f'part="{selector}"')
        for index, (name, color, _) in enumerate(FOUR_COLORS):
            path = PARTS_4 / f"Buddy-{name}.stl"
            if index == 0:
                shutil.copyfile(raw_four[name], path)
            else:
                cuts = "\n".join(f'import("{raw_four[higher]}");' for higher, _, _ in FOUR_COLORS[:index])
                csg = temp / f"cut-{name}.scad"
                csg.write_text(f'difference() {{ import("{raw_four[name]}"); union() {{ {cuts} }} }}\n')
                export(command, csg, path)
            four_groups.append((name, color, path))
    four_volume = sum(check_mesh(path) for _, _, path in four_groups)
    if abs(four_volume - whole_volume) > whole_volume * 0.0001:
        raise ValueError("Four-color volumes do not reconstruct the one-piece STL")
    assemble_3mf(four_groups, HERE / "Buddy-4-color.3mf")
    print("Built Buddy.stl, 4/6-color 3MFs, and their separate color-part STLs")


if __name__ == "__main__":
    main()
