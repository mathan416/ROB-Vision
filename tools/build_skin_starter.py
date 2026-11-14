#!/usr/bin/env python3
"""Build the editable Buddy skin starter pack and artist placement diagram."""

import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
SVG = lambda tag: f"{{{NS}}}{tag}"


def guide_svg():
    stations = [(145, 469, "far holder"), (225, 496, "near holder"),
                (445, 477, "spinner"), (285, 514, "red pad"), (370, 514, "blue pad")]
    trays = [(145, 493), (230, 516), (325, 525), (410, 512), (500, 493)]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 590">',
             '<title>Buddy live stage placement guide</title>',
             '<g fill="none" stroke="#24b9cd" stroke-width="2" stroke-dasharray="7 5">',
             '<rect x="190" y="95" width="270" height="190"/>',
             '<rect x="250" y="275" width="150" height="245"/>',
             '<rect x="45" y="460" width="560" height="130"/>',
             '</g><g fill="none" stroke="#ef765d" stroke-width="3">']
    for x, y in [(325, 265), (285, 317), (365, 317), (245, 381), (405, 381), (279, 465), (371, 465)]:
        parts.append(f'<circle cx="{x}" cy="{y}" r="8"/>')
        parts.append(f'<path d="M{x-12} {y}h24 M{x} {y-12}v24"/>')
    parts.append('</g><g fill="none" stroke="#f5c66a" stroke-width="2">')
    for x, y, _ in stations:
        parts.append(f'<circle cx="{x}" cy="{y}" r="9"/>')
    parts.append('</g><g fill="none" stroke="#94d69d" stroke-width="2">')
    for x, y in trays:
        parts.append(f'<circle cx="{x}" cy="{y}" r="8"/>')
    parts.append('</g><g fill="#a7e9ef" font-family="Arial" font-size="12" font-weight="bold">')
    parts += ['<text x="197" y="90">HEAD ART BOX</text>',
              '<text x="260" y="293">BODY ART BOX</text>',
              '<text x="24" y="33">650 x 590 VIEWBOX - TRANSPARENT GUIDE</text>',
              '<text x="48" y="454">STAGE FLOOR</text>']
    parts.append('</g></svg>')
    return ''.join(parts).encode()


def arm_svg():
    return b'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 128">
<title>Articulated arm segment placement guide</title>
<path d="M32 8V120" stroke="#24b9cd" stroke-width="2" stroke-dasharray="5 4"/>
<rect x="0.5" y="0.5" width="63" height="127" fill="none" stroke="#24b9cd"/>
<circle cx="32" cy="8" r="6" fill="none" stroke="#ef765d" stroke-width="2"/>
<circle cx="32" cy="120" r="6" fill="none" stroke="#ef765d" stroke-width="2"/>
</svg>'''


def head_example():
    source = ET.parse(ROOT / "output/svg/Buddy-Live-Model.svg").getroot()
    head = source.find(f".//{SVG('g')}[@id='head']")
    if head is None:
        raise RuntimeError("Buddy head is missing from the reference SVG.")
    gradients = source.find(SVG('defs'))
    root = ET.Element(SVG('svg'), {"viewBox": "190 95 270 190"})
    defs = ET.SubElement(root, SVG('defs'))
    for gradient in gradients:
        if gradient.attrib.get("id") in ("body", "dark", "eye", "metal"):
            defs.append(gradient)
    head.attrib.pop("transform", None)
    for child in list(head):
        if child.attrib.get("id") in ("head-led", "skin-head"):
            head.remove(child)
    root.append(head)
    return ET.tostring(root, encoding="utf-8", xml_declaration=False)


def part_examples():
    """Editable, transparent examples in the exact coordinate box of each slot."""
    boxes = {
        "background": (650, 590), "floor": (560, 130), "body": (150, 245),
        "left_upper_arm": (64, 128), "left_forearm": (64, 128),
        "right_upper_arm": (64, 128), "right_forearm": (64, 128),
        "left_hand": (50, 48), "right_hand": (50, 48), "platform": (205, 72),
        "gyro_linkage": (355, 90), "holder_far": (86, 66),
        "holder_near": (90, 66), "spinner": (78, 62), "red_pad": (64, 37),
        "blue_pad": (64, 37), "stack_linkage": (430, 83), "stack_tray": (76, 78),
    }
    arm = ('<path d="M32 8V120" stroke="#213d54" stroke-width="25" stroke-linecap="round"/>'
           '<path d="M32 17V111" stroke="#68d5e0" stroke-width="11" stroke-linecap="round"/>'
           '<circle cx="32" cy="8" r="7" fill="#f4eee1" stroke="#213d54" stroke-width="3"/>'
           '<circle cx="32" cy="120" r="7" fill="#f4eee1" stroke="#213d54" stroke-width="3"/>')
    hand = ('<path d="M27 8H14Q5 8 5 17V31Q5 40 14 40H27V32H16V16H27Z" '
            'fill="#f4eee1" stroke="#213d54" stroke-width="3"/>'
            '<path d="M27 18V30" stroke="#68d5e0" stroke-width="3"/>')
    holder = ('<path d="M31 18V58Q43 66 55 58V18Z" fill="#f4eee1" stroke="#213d54" stroke-width="3"/>'
              '<ellipse cx="43" cy="18" rx="34" ry="10" fill="#213d54" stroke="#68d5e0" stroke-width="3"/>'
              '<ellipse cx="43" cy="18" rx="22" ry="5" fill="#091d30"/>')
    pad = ('<path d="M32 18V34" stroke="#f4eee1" stroke-width="5"/>'
           '<ellipse cx="32" cy="16" rx="28" ry="10" fill="#213d54" stroke="#f4eee1" stroke-width="3"/>'
           '<ellipse cx="32" cy="14" rx="21" ry="6" fill="{colour}"/>')
    art = {
        "background": ('<rect width="650" height="590" fill="#10273a"/>'
                       '<path d="M0 470Q325 405 650 470V590H0Z" fill="#173b4d"/>'
                       '<circle cx="88" cy="78" r="4" fill="#68d5e0"/>'
                       '<circle cx="535" cy="128" r="3" fill="#f4eee1"/>'
                       '<circle cx="573" cy="65" r="5" fill="#68d5e0"/>'),
        "floor": ('<path d="M8 56Q280 -10 552 56L552 114Q280 148 8 114Z" '
                  'fill="#173b4d" stroke="#68d5e0" stroke-width="3"/>'
                  '<path d="M280 20V130M70 89Q280 39 490 89" fill="none" '
                  'stroke="#4a8595" stroke-width="2"/>'),
        "body": ('<path d="M30 15H120L140 218Q75 242 10 218Z" '
                 'fill="#f4eee1" stroke="#213d54" stroke-width="5"/>'
                 '<path d="M53 46H97L111 199Q75 213 39 199Z" fill="#213d54"/>'
                 '<path d="M61 78H89M57 112H93M54 146H96" stroke="#68d5e0" stroke-width="6"/>'
                 '<rect x="27" y="6" width="96" height="25" rx="10" fill="#68d5e0" '
                 'stroke="#213d54" stroke-width="4"/>'),
        "left_hand": hand, "right_hand": hand,
        "platform": ('<path d="M8 18H197L184 63H22Z" fill="#213d54" '
                     'stroke="#f4eee1" stroke-width="4"/>'
                     '<path d="M8 18H197L178 36H27Z" fill="#68d5e0" '
                     'stroke="#213d54" stroke-width="3"/>'),
        "gyro_linkage": ('<path d="M8 49L92 26M8 58L92 35M266 40L348 12M266 49L348 21" '
                         'stroke="#f4eee1" stroke-width="10" stroke-linecap="round"/>'
                         '<path d="M8 49L92 26M266 40L348 12" stroke="#68d5e0" '
                         'stroke-width="4" stroke-linecap="round"/>'),
        "holder_far": holder, "holder_near": holder.replace('cx="43"', 'cx="45"'),
        "spinner": ('<path d="M11 49L50 24" stroke="#f4eee1" stroke-width="10"/>'
                    '<path d="M48 17V51" stroke="#213d54" stroke-width="19"/>'
                    '<ellipse cx="49" cy="17" rx="27" ry="9" fill="#f4eee1" '
                    'stroke="#213d54" stroke-width="3"/>'
                    '<ellipse cx="49" cy="16" rx="16" ry="5" fill="#68d5e0"/>'),
        "red_pad": pad.format(colour="#ef765d"),
        "blue_pad": pad.format(colour="#68d5e0"),
        "stack_linkage": ('<path d="M30 20L170 63M95 35L170 63M260 63L335 35M260 63L400 20" '
                          'stroke="#f4eee1" stroke-width="9" stroke-linecap="round"/>'
                          '<path d="M30 20L170 63M260 63L400 20" stroke="#68d5e0" '
                          'stroke-width="4" stroke-linecap="round"/>'),
        "stack_tray": ('<path d="M27 13V62Q38 73 49 62V13Z" fill="#f4eee1" '
                       'stroke="#213d54" stroke-width="3"/>'
                       '<ellipse cx="38" cy="13" rx="34" ry="10" fill="#68d5e0" '
                       'stroke="#213d54" stroke-width="3"/>'
                       '<ellipse cx="38" cy="12" rx="22" ry="5" fill="#10273a"/>'),
    }
    for slot in ("left_upper_arm", "left_forearm", "right_upper_arm", "right_forearm"):
        art[slot] = arm
    assert set(art) == set(boxes)
    return {slot: (f'<svg xmlns="{NS}" viewBox="0 0 {width} {height}">'
                   f'<title>{slot.replace("_", " ").title()} example</title>{art[slot]}</svg>').encode()
            for slot, (width, height) in boxes.items()}


def diagram_png(path):
    image = Image.new("RGB", (1300, 1180), "#0c2030")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(str(ROOT / "dashboard/fonts/DMSans-700.ttf"), 22)
        small = ImageFont.truetype(str(ROOT / "dashboard/fonts/DMSans-400.ttf"), 16)
    except OSError:
        font = small = ImageFont.load_default()
    scale = 2
    def circle(x, y, colour, radius=8):
        x, y = x * scale, y * scale
        draw.ellipse((x-radius*scale, y-radius*scale, x+radius*scale, y+radius*scale),
                     outline=colour, width=4)
    draw.rounded_rectangle((380, 190, 920, 570), 25, outline="#45c8d7", width=4)
    draw.rounded_rectangle((500, 550, 800, 1040), 25, outline="#45c8d7", width=4)
    draw.text((410, 200), "HEAD ART BOX", fill="#a9e7ec", font=font)
    draw.text((525, 570), "BODY ART BOX", fill="#a9e7ec", font=font)
    for x, y in [(325, 265), (285, 317), (365, 317), (245, 381), (405, 381), (279, 465), (371, 465)]:
        circle(x, y, "#ff8268")
    for x, y, label in [(145, 469, "FAR"), (225, 496, "NEAR"), (445, 477, "SPINNER"),
                        (285, 514, "RED"), (370, 514, "BLUE")]:
        circle(x, y, "#f5c66a")
        draw.text((x*scale-18, y*scale+24), label, fill="#f5d994", font=small)
    draw.text((50, 38), "BUDDY LIVE MODEL - ART PLACEMENT", fill="white", font=font)
    draw.text((50, 75), "650 x 590 canvas  /  red = joints  /  gold = Gyromite destinations", fill="#a9c8d3", font=small)
    image.save(path)


def main():
    output = ROOT / "output/skins/Buddy-Skin-Starter.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    diagram = ROOT / "docs/images/skin-placement-guide.png"
    diagram_png(diagram)
    shutil.copy2(diagram, ROOT / "website/assets/skin-placement-guide.png")
    manifest = {"schema": 1, "name": "My Buddy", "artist": "Your name",
                "assets": {"head": "assets/head.svg"}}
    readme = ("BUDDY SKIN STARTER\n\n"
              "Open R.O.B.-Vision-Buddy-Skin-Artist-Guide.pdf first.\n"
              "Import this ZIP in Setup > Skins to see the sample head.\n"
              "assets/head.svg is the head artwork currently selected in skin.json.\n"
              "The other files in assets/ are editable examples for every allowed part.\n"
              "They do not appear in Buddy until you add their filenames to skin.json,\n"
              "or upload the parts through Setup. Unlisted examples are not saved on import.\n"
              "Replace assets/head.svg with your art, or use Setup to upload individual parts.\n"
              "Omit any entry in skin.json to keep that original Buddy part.\n"
              "Only Buddy and fixed stage fixtures can change. Gyros and Stack-Up blocks always keep their original artwork.\n"
              "The reference folder is for drawing guides and is ignored by the app.\n"
              "See reference/layer-order.txt to plan which parts sit in front.\n")
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("skin.json", json.dumps(manifest, indent=2) + "\n")
        archive.writestr("assets/head.svg", head_example())
        for slot, art in part_examples().items():
            archive.writestr(f"assets/{slot}.svg", art)
        archive.write(ROOT / "output/pdf/R.O.B.-Vision-Buddy-Skin-Artist-Guide.pdf",
                      "R.O.B.-Vision-Buddy-Skin-Artist-Guide.pdf")
        archive.writestr("reference/Buddy-Live-Model.svg", (ROOT / "output/svg/Buddy-Live-Model.svg").read_bytes())
        archive.writestr("reference/placement-guide.svg", guide_svg())
        archive.writestr("reference/arm-segment-guide.svg", arm_svg())
        archive.writestr("reference/layer-order.txt",
                         "BACK TO FRONT\nbackground\nfloor\nbody\nplatform and fixtures\n"
                         "original game pieces (not skin slots)\nupper arms and forearms\nhands\nhead\n"
                         "red Test light (always drawn by the app)\n")
        archive.writestr("README.txt", readme)
    for folder in (ROOT / "dashboard/downloads", ROOT / "website/downloads"):
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, folder / output.name)
    print(output)


if __name__ == "__main__":
    main()
