#!/usr/bin/env python3
"""Build the current project guides from their editable Markdown sources."""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
    Image as GuideImage,
    LongTable,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = ROOT / "output" / "pdf"
WEB_GUIDES = ROOT / "dashboard" / "guides"
FONTS = ROOT / "dashboard" / "fonts"
BUDDY_ART = DOCS / "images" / "buddy-concept-v1.png"

NAVY = colors.HexColor("#0C2030")
MIDNIGHT = colors.HexColor("#07131F")
TEAL = colors.HexColor("#246B7C")
PALE = colors.HexColor("#EAF3F4")
ORANGE = colors.HexColor("#E66D50")
BODY = colors.HexColor("#253746")
MUTED = colors.HexColor("#557182")
RULE = colors.HexColor("#D0DFE4")

pdfmetrics.registerFont(TTFont("DM", str(FONTS / "DMSans-400.ttf")))
pdfmetrics.registerFont(TTFont("DM-Bold", str(FONTS / "DMSans-700.ttf")))
pdfmetrics.registerFont(TTFont("Barlow", str(FONTS / "BarlowCondensed-800.ttf")))
pdfmetrics.registerFontFamily("DM", normal="DM", bold="DM-Bold")


def clean(s: str) -> str:
    return (s.replace("\u2011", "-").replace("\u2013", "-")
            .replace("\u2014", "-").replace("\u00a0", " "))


def inline(s: str) -> str:
    s = html.escape(clean(s), quote=False)

    def link(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        if target.startswith("https://") or target.startswith("http://"):
            return f'<link href="{html.escape(target, quote=True)}" color="#246B7C">{label}</link>'
        return f'<font color="#246B7C">{label}</font>'

    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, s)
    s = re.sub(r"`([^`]+)`", r'<font face="Courier" color="#204D61">\1</font>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", s)
    return s


def styles(compact: bool = False) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    scale = 0.9 if compact else 1.0
    return {
        "chapter": ParagraphStyle("RVChapter", parent=base["Title"], fontName="Barlow",
                                  fontSize=31 * scale, leading=32 * scale, textColor=NAVY,
                                  spaceAfter=17, alignment=TA_LEFT, keepWithNext=True),
        "h2": ParagraphStyle("RVH2", parent=base["Heading2"], fontName="Barlow",
                             fontSize=17 * scale, leading=19 * scale, textColor=TEAL,
                             spaceBefore=17 * scale, spaceAfter=8 * scale,
                             keepWithNext=True),
        "h3": ParagraphStyle("RVH3", parent=base["Heading3"], fontName="DM-Bold",
                             fontSize=10.4 * scale, leading=13 * scale, textColor=NAVY,
                             spaceBefore=10 * scale, spaceAfter=5 * scale,
                             keepWithNext=True),
        "body": ParagraphStyle("RVBody", parent=base["BodyText"], fontName="DM",
                               fontSize=9.15 * scale, leading=14 * scale, textColor=BODY,
                               spaceAfter=8 * scale),
        "status": ParagraphStyle("RVStatus", parent=base["BodyText"], fontName="DM-Bold",
                                 fontSize=9.2 * scale, leading=13 * scale, textColor=TEAL,
                                 spaceAfter=11 * scale),
        "bullet": ParagraphStyle("RVBullet", parent=base["BodyText"], fontName="DM",
                                 fontSize=8.9 * scale, leading=13.2 * scale, textColor=BODY,
                                 leftIndent=15, firstLineIndent=-10, spaceAfter=5 * scale),
        "cell": ParagraphStyle("RVCell", parent=base["BodyText"], fontName="DM",
                               fontSize=7.5 * scale, leading=10.2 * scale, textColor=BODY),
        "cellhead": ParagraphStyle("RVCellHead", parent=base["BodyText"], fontName="DM-Bold",
                                   fontSize=7.5 * scale, leading=10.2 * scale, textColor=colors.white),
        "eyebrow": ParagraphStyle("RVEyebrow", parent=base["BodyText"], fontName="DM-Bold",
                                  fontSize=7.5, leading=10, textColor=ORANGE,
                                  spaceAfter=8, keepWithNext=True),
        "code": ParagraphStyle("RVCode", parent=base["Code"], fontName="Courier",
                               fontSize=7.25, leading=10.2, textColor=NAVY),
    }


def table_block(lines: list[str], usable_width: float, st: dict[str, ParagraphStyle]):
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        rows.append(cells)
    if not rows:
        return None
    count = max(len(r) for r in rows)
    # Favor descriptive columns while preserving room for short labels.
    if count == 2:
        widths = [usable_width * 0.31, usable_width * 0.69]
    elif count == 3:
        widths = [usable_width * 0.25, usable_width * 0.40, usable_width * 0.35]
    elif count == 4:
        widths = [usable_width * 0.18, usable_width * 0.28, usable_width * 0.29, usable_width * 0.25]
    else:
        widths = [usable_width / count] * count
    data = []
    for idx, row in enumerate(rows):
        cells = row + [""] * (count - len(row))
        data.append([Paragraph(inline(cell), st["cellhead" if idx == 0 else "cell"])
                     for cell in cells])
    table = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F6F7")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, RULE),
    ]))
    return table


def markdown_story(path: Path, usable_width: float, st: dict[str, ParagraphStyle],
                   chapter_number: int | None = None, new_page: bool = True,
                   max_image_height: float = 330, chapter_label: str = "GUIDE"):
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].removeprefix("# ").strip()
    story = []
    if new_page:
        story.append(PageBreak())
    elif chapter_number is not None:
        story.append(CondPageBreak(160))
        story.append(Spacer(1, 23))
    if chapter_number is not None:
        story.append(Paragraph(f"CHAPTER {chapter_number:02d} / {chapter_label}", st["eyebrow"]))
    story.append(Paragraph(inline(title), st["chapter"]))
    i = 1
    paragraph: list[str] = []

    def flush():
        nonlocal paragraph
        if paragraph:
            value = " ".join(x.strip() for x in paragraph)
            style = st["status"] if value.startswith("**Status:") or value.startswith("**Project stage:") or value.startswith("**Current release:") else st["body"]
            story.append(Paragraph(inline(value), style))
            paragraph = []

    while i < len(lines):
        line = lines[i]
        if line.strip() == "<!-- pagebreak -->":
            flush(); story.append(PageBreak()); i += 1; continue
        if not line.strip():
            flush(); i += 1; continue
        image_match = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", line.strip())
        if image_match:
            flush()
            image_path = (path.parent / image_match.group(2)).resolve()
            if not image_path.is_relative_to(ROOT) or not image_path.is_file():
                raise ValueError(f"Missing or outside-repository guide image: {image_path}")
            picture = GuideImage(str(image_path))
            scale = min(usable_width / picture.imageWidth,
                        max_image_height / picture.imageHeight, 1)
            picture.drawWidth = picture.imageWidth * scale
            picture.drawHeight = picture.imageHeight * scale
            picture.hAlign = "CENTER"
            story.extend([Spacer(1, 6), picture, Spacer(1, 8)])
            i += 1; continue
        if line.startswith("## ") or line.startswith("### "):
            flush()
            level = "h3" if line.startswith("### ") else "h2"
            story.append(Paragraph(inline(line.split(" ", 1)[1]), st[level]))
            i += 1; continue
        if line.startswith("```"):
            flush(); i += 1; code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(clean(lines[i]).replace("→", "->").replace("↓", "v"))
                i += 1
            if i < len(lines): i += 1
            story.append(Preformatted("\n".join(code), st["code"], maxLineLength=110,
                                      newLineChars="\\"))
            story.append(Spacer(1, 9))
            continue
        if line.lstrip().startswith("|"):
            flush(); table_lines = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                table_lines.append(lines[i]); i += 1
            table = table_block(table_lines, usable_width, st)
            if table: story.extend([table, Spacer(1, 9)])
            continue
        if line.startswith("- ") or re.match(r"\d+\. ", line):
            flush()
            content = line[2:] if line.startswith("- ") else line
            bullet = "•" if line.startswith("- ") else None
            story.append(Paragraph(inline(content), st["bullet"], bulletText=bullet))
            i += 1; continue
        if line.startswith("# "):
            flush(); i += 1; continue
        paragraph.append(line)
        i += 1
    flush()
    return story


def cover(canvas, doc, title: str, subtitle: str, landscape_page: bool = False):
    width, height = doc.pagesize
    canvas.saveState()
    canvas.setFillColor(MIDNIGHT); canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#112D42")); canvas.circle(width * .77, height * .58, height * .34, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#2C6173")); canvas.setLineWidth(1.4)
    for offset in (0, 27, 55):
        canvas.circle(width * .77, height * .58, height * .24 + offset, fill=0, stroke=1)
    # Buddy is a separate story portrait; body diagrams remain screenshots of the app.
    art_height = 450 if landscape_page else 550
    art_width = art_height * 1145 / 1374
    canvas.drawImage(str(BUDDY_ART), width - art_width - 9,
                     80 if landscape_page else 165,
                     width=art_width, height=art_height, mask="auto")
    canvas.setFillColor(ORANGE); canvas.rect(0, 0, 11, height, fill=1, stroke=0)
    canvas.setFillColor(colors.white); canvas.setFont("Barlow", 22)
    canvas.drawString(53, height-75, "R.O.B. VISION")
    canvas.setFont("DM-Bold", 8.4); canvas.setFillColor(colors.HexColor("#83B4C2"))
    canvas.drawString(54, height-92, "VIRTUAL ROBOT COMPANION / MK.01")
    canvas.setFillColor(colors.white); canvas.setFont("Barlow", 42 if not landscape_page else 38)
    canvas.drawString(53, 150, title.upper())
    canvas.setFillColor(colors.HexColor("#ADD0D9")); canvas.setFont("DM", 12)
    canvas.drawString(55, 126, subtitle)
    canvas.setStrokeColor(ORANGE); canvas.setLineWidth(3); canvas.line(55, 109, 216, 109)
    canvas.setFillColor(colors.HexColor("#8BA9B8")); canvas.setFont("DM-Bold", 8)
    canvas.drawString(55, 67, "VERSION 0.1.5")
    canvas.drawString(55, 52, "UNO Q · RETROPIE · BATOCERA")
    canvas.restoreState()


def body_page(canvas, doc, label: str):
    width, height = doc.pagesize
    canvas.saveState()
    if label == "Quick Reference":
        art_height = 190
        canvas.drawImage(str(BUDDY_ART), width - 48 - art_height * 1145 / 1374,
                         70, width=art_height * 1145 / 1374,
                         height=art_height, mask="auto")
    canvas.setStrokeColor(RULE); canvas.setLineWidth(.6)
    canvas.line(48, height-39, width-48, height-39)
    canvas.setFont("DM-Bold", 7.6); canvas.setFillColor(TEAL)
    canvas.drawString(48, height-28, "R.O.B. VISION")
    canvas.setFillColor(MUTED); canvas.drawRightString(width-48, height-28, label.upper())
    canvas.line(48, 43, width-48, 43)
    canvas.setFont("DM", 7); canvas.drawString(48, 29, "UNO Q · VIRTUAL ROBOT COMPANION")
    canvas.drawRightString(width-48, 29, f"{doc.page:02d}")
    canvas.restoreState()


def build_book(filename: str, title: str, subtitle: str, chapter_files: list[str],
               page_size=A4):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / filename
    doc = SimpleDocTemplate(str(path), pagesize=page_size, leftMargin=48,
                            rightMargin=48, topMargin=58, bottomMargin=58,
                            title=f"R.O.B. Vision - {title}", author="R.O.B. Vision project")
    st = styles()
    available_width = page_size[0] - 96
    story = [Spacer(1, page_size[1] - 130)]
    for n, name in enumerate(chapter_files, 1):
        chapter_starts_page = (n == 1 or page_size[1] > page_size[0]
                               or name in {"TROUBLESHOOTING.md", "DASHBOARD_DESIGN.md", "UNO_Q_MATRIX_DISPLAY.md"})
        image_height = (300 if name == "MEET_BUDDY.md"
                        else 135 if name == "UNO_Q_MATRIX_DISPLAY.md"
                        else 430 if page_size[1] > page_size[0] else 285)
        chapter_label = ("STORY" if name == "MEET_BUDDY.md"
                         else "TECHNICAL REFERENCE" if title == "Technical Reference"
                         else "MATRIX DISPLAY GUIDE" if title == "Matrix Display Guide"
                         else "USER GUIDE")
        story.extend(markdown_story(DOCS / name, available_width, st, n,
                                    new_page=chapter_starts_page,
                                    max_image_height=image_height,
                                    chapter_label=chapter_label))
    doc.build(story,
              onFirstPage=lambda c, d: cover(c, d, title, subtitle, page_size[0] > page_size[1]),
              onLaterPages=lambda c, d: body_page(c, d, title))
    return path


def build_quick():
    path = OUTPUT / "R.O.B.-Vision-Quick-Reference.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=48, rightMargin=48,
                            topMargin=58, bottomMargin=53,
                            title="R.O.B. Vision - Quick Reference", author="R.O.B. Vision project")
    story = markdown_story(DOCS / "QUICK_REFERENCE.md", A4[0]-96, styles(compact=True),
                           chapter_number=None, new_page=False)
    doc.build(story, onFirstPage=lambda c, d: body_page(c, d, "Quick Reference"),
              onLaterPages=lambda c, d: body_page(c, d, "Quick Reference"))
    return path


if __name__ == "__main__":
    generated = [
        build_book("R.O.B.-Vision-User-Guide.pdf", "User Guide",
                   "Play, preview, setup, and problem solving",
                   ["MEET_BUDDY.md", "USER_GUIDE.md", "GAMEPLAY_GUIDE.md", "SETUP_GUIDE.md", "INSTALLATION_GUIDE.md", "TROUBLESHOOTING.md"]),
        build_book("R.O.B.-Vision-Technical-Reference.pdf", "Technical Reference",
                   "Architecture, frame protocol, networking, hardware, and verification",
                   ["TECHNICAL_ARCHITECTURE.md", "HISTORICAL_MANUAL_NOTES.md", "GYROMITE_MANUAL_NOTES.md",
                    "STACK_UP_MANUAL_NOTES.md", "GAME_IDENTIFICATION.md",
                    "optical-input.md", "ROM_SIGNAL_ANALYSIS.md", "DASHBOARD_DESIGN.md",
                    "HARDWARE_BUILD_GUIDE.md", "CONFIGURATION_REFERENCE.md",
                    "SAFETY_AND_SECURITY.md", "VERIFICATION_PLAN.md"],
                   page_size=landscape(A4)),
        build_book("R.O.B.-Vision-Matrix-Display-Guide.pdf", "Matrix Display Guide",
                   "UNO Q status animations and display states",
                   ["UNO_Q_MATRIX_DISPLAY.md"], page_size=landscape(A4)),
        build_quick(),
    ]
    WEB_GUIDES.mkdir(parents=True, exist_ok=True)
    for path in generated:
        shutil.copy2(path, WEB_GUIDES / path.name)
        print(path)
