#!/usr/bin/env python3
"""Render documentation art from the actual UNO Q sketch and live UI captures."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SKETCH = (ROOT / "sketch" / "sketch.ino").read_text()
OUT = ROOT / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)
CAPTURES = ROOT / "tools" / "guide_sources"
FONT = ROOT / "dashboard" / "fonts" / "DMSans-700.ttf"
TITLE = ROOT / "dashboard" / "fonts" / "BarlowCondensed-800.ttf"


def patterns():
    source = SKETCH.split("const char* const loading[][8] = {", 1)[1].split("};", 1)[0]
    lines = re.findall(r'"([.1-7]{13})"', source)
    assert len(lines) == 24
    return [lines[i : i + 8] for i in range(0, 24, 8)]


def glyph(name):
    source = re.search(rf"const uint8_t {name}\[7\]=\{{([^}}]+)\}};", SKETCH)
    assert source, name
    return [int(value) for value in source.group(1).split(",")]


def blank():
    return [[0] * 13 for _ in range(8)]


def pixel(frame, x, y, value):
    if 0 <= x < 13 and 0 <= y < 8:
        frame[y][x] = max(frame[y][x], value)


def draw_glyph(frame, name, left, value):
    for y, row in enumerate(glyph(name)):
        for x in range(5):
            if row & (1 << (4 - x)):
                pixel(frame, left + x, y, value)


def hourglass(index):
    return [[int(c) if c != "." else 0 for c in row] for row in patterns()[index]]


def eyes(frame_number, mode="idle", hint=0):
    frame = blank()
    glance = [0, 1, 0, -1][(frame_number // 10) % 4]
    if hint == 1:
        glance = -1
    elif hint == 2:
        glance = 1
    blink = frame_number % 23 == 21
    for center in (3, 9):
        for x in range(center - 2, center + 3):
            pixel(frame, x, 1, 5)
            pixel(frame, x, 5, 4)
        for y in range(2, 5):
            pixel(frame, center - 3, y, 4)
            pixel(frame, center + 3, y, 4)
        if blink or hint in (5, 6):
            for x in range(center - 1, center + 2):
                pixel(frame, x, 3, 7)
        else:
            offset_y = -1 if hint == 3 else 1 if hint == 4 else 0
            pixel(frame, center + glance, 3 + offset_y, 7)
            pixel(frame, center + glance, 4 + offset_y, 6)
    if mode == "gyromite":
        pixel(frame, [5, 6, 7, 6][frame_number % 4], 7, 5)
    elif mode == "stack-up":
        for x in range(5, 8):
            pixel(frame, x, 7 - (frame_number // 3) % 3, 5)
    return frame


def title_mark(a, b):
    frame = blank()
    draw_glyph(frame, a, 1, 7)
    draw_glyph(frame, b, 7, 7)
    return frame


def letter(name, brightness=7):
    frame = blank()
    draw_glyph(frame, name, 4, brightness)
    return frame


def panel(frame, caption, footnote):
    cell, gap = 35, 8
    matrix_w, matrix_h = 13 * cell + 12 * gap, 8 * cell + 7 * gap
    width, height = matrix_w + 70, matrix_h + 130
    image = Image.new("RGB", (width, height), "#091727")
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((12, 12, width - 12, height - 12), 24, fill="#102338", outline="#366179", width=2)
    d.text((36, 28), caption.upper(), font=ImageFont.truetype(str(TITLE), 31), fill="#e3f4fa")
    x0, y0 = 35, 79
    glow = Image.new("RGBA", image.size)
    gd = ImageDraw.Draw(glow)
    for y, row in enumerate(frame):
        for x, value in enumerate(row):
            px, py = x0 + x * (cell + gap), y0 + y * (cell + gap)
            d.rounded_rectangle((px, py, px + cell, py + cell), 6, fill="#182c41", outline="#27485c", width=1)
            if value:
                intensity = value / 7
                gd.ellipse((px - 5, py - 5, px + cell + 5, py + cell + 5), fill=(48, 180, 240, int(105 * intensity)))
                color = (int(27 + 90 * intensity), int(72 + 160 * intensity), int(112 + 143 * intensity))
                d.rounded_rectangle((px + 2, py + 2, px + cell - 2, py + cell - 2), 5, fill=color)
    image = Image.alpha_composite(image.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(image)
    d.text((36, height - 44), footnote.upper(), font=ImageFont.truetype(str(FONT), 14), fill="#89b7c7")
    return image.convert("RGB")


def strip(name, frames):
    panes = [panel(frame, caption, footnote) for frame, caption, footnote in frames]
    gutter = 18
    result = Image.new("RGB", (len(panes) * panes[0].width + (len(panes) - 1) * gutter, panes[0].height), "#091727")
    for index, pane in enumerate(panes):
        result.paste(pane, (index * (pane.width + gutter), 0))
    result.save(OUT / f"matrix-{name}.png", optimize=True)


def crop_capture(name, box):
    source = Image.open(CAPTURES / f"{name}-full.png").convert("RGB")
    crop = source.crop(box)
    crop.save(OUT / f"{name}-screenshot.png", optimize=True)


def main():
    strip("startup", [(hourglass(0), "Starting", "Hourglass / frame 1"),
                      (hourglass(1), "Bridge loading", "Hourglass / frame 2"),
                      (hourglass(2), "Waiting", "Hourglass / frame 3")])
    strip("idle", [(eyes(0), "Ready", "Eyes centered"),
                   (eyes(10), "Looking right", "Glance"),
                   (eyes(21), "Blink", "Brief eyelid")])
    strip("game-titles", [(title_mark("G", "Y"), "Gyromite", "Title cue / 1.3 seconds"),
                          (title_mark("S", "U"), "Stack-Up", "Title cue / 1.3 seconds")])
    strip("game-eyes", [(eyes(1, "gyromite"), "Gyromite", "Eyes + spinning dot"),
                        (eyes(3, "stack-up"), "Stack-Up", "Eyes + rising blocks")])
    strip("test", [(letter("T", 4), "Test armed", "Steady T"),
                   (letter("T", 7), "Flashes seen", "Pulsing T")])
    strip("pair-fault", [(letter("P", 7), "Pairing", "Pulsing P"),
                         (letter("X", 7), "Fault", "Blinking X")])
    source = Image.open(CAPTURES / "mission-full.png").convert("RGB")
    source.crop((0, 0, 640, 500)).save(OUT / "mission-model-screenshot.png", optimize=True)
    source.crop((0, 500, 625, 715)).save(OUT / "mission-controls-screenshot.png", optimize=True)
    crop_capture("setup", (0, 0, 640, 622))
    source = Image.open(CAPTURES / "setup-full.png").convert("RGB")
    source.crop((0, 126, 640, 416)).save(OUT / "setup-link-camera-screenshot.png", optimize=True)



if __name__ == "__main__":
    main()
