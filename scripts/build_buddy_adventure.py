#!/usr/bin/env python3
"""Typeset Buddy's four-page comic without changing the original artwork."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "docs" / "images"
OUTPUT = ROOT / "output" / "pdf" / "Buddy-and-the-Big-Wide-Window.pdf"
FONT_DIR = ROOT / "dashboard" / "fonts"
PAGE_W, PAGE_H = 612, 900
ART_H = 820
ART_Y = 34
NAVY = HexColor("#071321")
CORAL = HexColor("#d95f4a")


@dataclass(frozen=True)
class ComicPage:
    art: str
    chapter: str
    strips: tuple[tuple[int, int], ...]
    lines: tuple[str, ...]


PAGES = (
    ComicPage(
        "buddy-comic-v1.png",
        "THE OTHER SIDE",
        ((297, 350), (655, 707), (1010, 1065), (1391, 1490)),
        (
            '<b>BUDDY (thinking):</b> Turn. Lift. Wait. I know every signal. But who keeps sending them?',
            '<b>BUDDY:</b> Huh? That blink was not mine. ...Hello?',
            '<b>BUDDY:</b> A window! Wait. Those are my hands!',
            '<b>BUDDY:</b> A table! A block! Okay, Buddy. Look cool. Set. It. Down.',
        ),
    ),
    ComicPage(
        "buddy-adventure-gyro.png",
        "THE SPINNY THING",
        ((303, 360), (681, 740), (1067, 1125), (1432, 1535)),
        (
            '<b>BUDDY:</b> Good morning, world! First mission: one gyro, two pads, zero panicking.',
            '<b>BUDDY (thinking):</b> Easy... easy... Why does the tiny tornado have a point?',
            '<b>BUDDY:</b> Blue gate, open up! Go on, little hero - I have got you!',
            '<b>BUDDY:</b> Oops! Even a top needs a rest. Back to the holder, you.',
        ),
    ),
    ComicPage(
        "buddy-adventure-blocks.png",
        "FIVE BLOCKS AND A FEELING",
        ((326, 372), (687, 737), (1046, 1096), (1438, 1535)),
        (
            '<b>BUDDY:</b> Five blocks. One tower. I was programmed for this! ...I think.',
            '<b>BUDDY (thinking):</b> Hands wide. Down. Close. Breathe. Wait - do I breathe?',
            '<b>BUDDY:</b> I have got them! Nobody sneeze!',
            '<b>BUDDY:</b> The signal is gone. I am still holding on... Are you still there?',
        ),
    ),
    ComicPage(
        "buddy-adventure-finale.png",
        "THE NEXT ROUND",
        ((306, 361), (675, 730), (1037, 1095), (1434, 1535)),
        (
            '<b>BUDDY:</b> There you are! For a second I thought the window had closed.',
            '<b>BUDDY:</b> Steady... open hands... ta-da!',
            '<b>PLAYER:</b> Nice save! &nbsp; <b>BUDDY:</b> I knew you were there!',
            '<b>BUDDY (thinking):</b> Maybe I never needed to leave the game. I just needed a friend on the other side. <b>BUDDY:</b> ...Do robots get pancakes?',
        ),
    ),
)


def draw_page(pdf: canvas.Canvas, page: ComicPage, index: int, render_art: Path) -> None:
    path = IMAGES / page.art
    with Image.open(path) as image:
        image_w, image_h = image.size
    art_w = ART_H * image_w / image_h
    art_x = (PAGE_W - art_w) / 2
    scale = ART_H / image_h

    pdf.setFillColor(NAVY)
    pdf.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    pdf.drawImage(str(render_art), art_x, ART_Y, art_w, ART_H)

    pdf.setFont("Barlow", 20)
    pdf.setFillColor(HexColor("#f4f8f5"))
    pdf.drawString(art_x, 868, "BUDDY & THE BIG WIDE WINDOW")
    pdf.setFont("DM-Bold", 8.4)
    pdf.setFillColor(HexColor("#83a9b9"))
    pdf.drawRightString(art_x + art_w, 870, f"{index:02d} / {len(PAGES):02d}")
    pdf.setFillColor(CORAL)
    pdf.rect(art_x, 860, art_w, 2.5, fill=1, stroke=0)

    style = ParagraphStyle(
        "comic-caption",
        fontName="DM",
        fontSize=10.4,
        leading=12.2,
        textColor=NAVY,
        splitLongWords=0,
    )
    for (top, bottom), line in zip(page.strips, page.lines, strict=True):
        strip_top = ART_Y + ART_H - top * scale
        strip_bottom = ART_Y + ART_H - bottom * scale
        width = art_w - 45
        paragraph = Paragraph(line.replace("<b>", '<font color="#bf4d3b"><b>').replace("</b>", "</b></font>"), style)
        _, height = paragraph.wrap(width, 100)
        if height > strip_top - strip_bottom - 2:
            raise ValueError(f"Caption overflows {page.art}: {line}")
        paragraph.drawOn(pdf, art_x + 23, strip_bottom + (strip_top - strip_bottom - height) / 2)

    pdf.setFont("DM-Bold", 8)
    pdf.setFillColor(HexColor("#9ab8c4"))
    pdf.drawString(art_x, 15, page.chapter)
    pdf.drawRightString(art_x + art_w, 15, "AN ORIGINAL BUDDY ADVENTURE")
    pdf.showPage()


def main() -> None:
    pdfmetrics.registerFont(TTFont("DM", str(FONT_DIR / "DMSans-400.ttf")))
    pdfmetrics.registerFont(TTFont("DM-Bold", str(FONT_DIR / "DMSans-700.ttf")))
    pdfmetrics.registerFont(TTFont("Barlow", str(FONT_DIR / "BarlowCondensed-800.ttf")))
    pdfmetrics.registerFontFamily("DM", normal="DM", bold="DM-Bold")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H))
    pdf.setTitle("Buddy & the Big Wide Window")
    pdf.setAuthor("R.O.B. Vision contributors")
    pdf.setSubject("An original four-page Buddy comic")
    with TemporaryDirectory(prefix="buddy-comic-") as scratch:
        for index, page in enumerate(PAGES, 1):
            render_art = Path(scratch) / f"page-{index}.jpg"
            with Image.open(IMAGES / page.art) as image:
                image.convert("RGB").save(render_art, quality=91, subsampling=0, optimize=True)
            draw_page(pdf, page, index, render_art)
    pdf.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
