#!/usr/bin/env python3
"""Render the Stack-Up starting Game Table from the dashboard's model values.

This is a documentation illustration, not a browser screenshot. Its tray placement
and block order are read from dashboard/app.js and dashboard/stack-model.js.
"""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/images/stack-up-game-table.png"
APP = (ROOT / "dashboard/app.js").read_text()
MODEL = (ROOT / "dashboard/stack-model.js").read_text()


def array(source: str, name: str) -> list[int]:
    match = re.search(rf"const {name} = \[([^]]+)\]", source)
    if not match:
        raise ValueError(f"Cannot find {name} in dashboard/app.js")
    return [int(value.strip()) for value in match.group(1).split(",")]


def main() -> None:
    percents = array(APP, "stackPercents")
    tops = array(APP, "stackTops")
    colors_match = re.search(r"const COLORS = Object.freeze\(\[([^]]+)\]\)", MODEL)
    if not colors_match:
        raise ValueError("Cannot find Stack-Up block order")
    bottom_to_top = re.findall(r"'([a-z]+)'", colors_match.group(1))
    if len(percents) != 5 or len(tops) != 5 or bottom_to_top != [
        "green", "yellow", "blue", "white", "red"
    ]:
        raise ValueError("The starting Stack-Up layout changed; review this illustration")

    width, height = 1380, 500
    image = Image.new("RGB", (width, height), "#071626")
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            glow = max(0, 1 - abs(x - width / 2) / (width / 2))
            pixels[x, y] = (
                int(7 + 7 * y / height),
                int(22 + 22 * y / height + 8 * glow),
                int(38 + 26 * y / height + 11 * glow),
            )
    draw = ImageDraw.Draw(image)
    bold = ROOT / "dashboard/fonts/DMSans-700.ttf"
    regular = ROOT / "dashboard/fonts/DMSans-400.ttf"
    display = ROOT / "dashboard/fonts/BarlowCondensed-800.ttf"
    title_font = ImageFont.truetype(str(display), 38)
    label_font = ImageFont.truetype(str(bold), 19)
    small_font = ImageFont.truetype(str(regular), 17)

    draw.rounded_rectangle((22, 18, width - 22, height - 18), radius=20,
                           outline="#426a7e", width=2)
    draw.text((66, 40), "GAME TABLE / STACK-UP", font=title_font, fill="#e4f6f8")
    draw.text((width - 390, 50), "TRAY 3 / STARTING STACK", font=label_font,
              fill="#83c6d3")
    draw.line((66, 91, width - 66, 91), fill="#365b70", width=2)

    # Perspective floor and link bars reflect the five-station accessory view.
    draw.polygon([(140, 359), (1240, 359), (1285, 425), (95, 425)],
                 fill="#173449", outline="#5e8291")
    for anchor in (300, 470, 690, 910, 1080):
        draw.line((690, 367, anchor, 397), fill="#365e70", width=2)
    xs = [round(115 + (width - 230) * p / 100) for p in percents]
    ys = [round(135 + (top - min(tops)) * 1.0) for top in tops]
    center = (xs[2], ys[2] + 15)
    for x, y in zip(xs, ys):
        if x != center[0]:
            draw.line((center[0], center[1], x, y + 18), fill="#afc9cf", width=12)
            draw.line((center[0], center[1] - 3, x, y + 15), fill="#547789", width=5)

    for number, (x, y) in enumerate(zip(xs, ys), 1):
        support_bottom = min(362, y + 82)
        draw.rounded_rectangle((x - 12, y + 4, x + 12, support_bottom), radius=5,
                               fill="#8ca4ad", outline="#d9e9e8", width=2)
        draw.rectangle((x - 5, y + 7, x + 5, support_bottom - 3), fill="#cadcde")
        draw.ellipse((x - 66, y - 18, x + 66, y + 20),
                     fill="#dce8e8", outline="#f7fbf8", width=3)
        draw.ellipse((x - 52, y - 12, x + 52, y + 13),
                     fill="#526e7d", outline="#a6c6cc", width=3)
        draw.ellipse((x - 37, y - 8, x + 37, y + 8), fill="#10293a")
        label = f"TRAY {number}"
        box = draw.textbbox((0, 0), label, font=label_font)
        draw.text((x - (box[2] - box[0]) / 2, 434), label,
                  font=label_font, fill="#e0f2ed" if number == 3 else "#9fbfcb")

    paint = {
        "green": ("#4b9870", "#80d8a4", "#c0ead6"),
        "yellow": ("#a98145", "#f1c76e", "#fbe4a7"),
        "blue": ("#317d9b", "#5dd1ef", "#b9f2fa"),
        "white": ("#a1b5b5", "#e7efeb", "#fbfffa"),
        "red": ("#a03c47", "#f08069", "#ffd8bb"),
    }
    x = xs[2]
    tray_y = ys[2]
    for level, color in enumerate(bottom_to_top):
        top = tray_y - 14 - level * 20
        side, face, rim = paint[color]
        draw.rounded_rectangle((x - 46, top, x + 46, top + 17), radius=7,
                               fill=side, outline=rim, width=2)
        draw.ellipse((x - 46, top - 8, x + 46, top + 9),
                     fill=face, outline=rim, width=3)
        draw.ellipse((x - 12, top - 2, x + 12, top + 4), fill="#49616d")

    draw.text((67, 458), "FIVE TRAYS  /  FIVE BLOCKS  /  RED · WHITE · BLUE · YELLOW · GREEN, TOP TO BOTTOM",
              font=small_font, fill="#9fc4ce")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
