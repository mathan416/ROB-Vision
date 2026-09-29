#!/usr/bin/env python3
"""Build the current project guides from their editable Markdown sources."""

from __future__ import annotations

import html
import posixpath
import re
import shutil
from pathlib import Path
from urllib.parse import quote

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Group, Line, Polygon, Rect, String
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
        if not target.startswith(("https://", "http://", "#")):
            target = "https://github.com/mathan416/ROB-Vision/blob/main/" + quote(
                posixpath.normpath("docs/" + target), safe="/#")
        if target.startswith("#"):
            return label
        return f'<link href="{html.escape(target, quote=True)}" color="#246B7C">{label}</link>'

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


def system_responsibilities_diagram(width: float) -> Drawing:
    """Vector companion to the Mermaid system flow in the technical source."""
    height = 226
    scale = width / 746
    diagram = Drawing(width, height)
    contents = Group()
    contents.scale(scale, 1)
    diagram.add(contents)

    def add(shape):
        contents.add(shape)

    def label(x, y, value, size=8, bold=False, color=BODY):
        add(String(x, y, value, fontName="DM-Bold" if bold else "DM",
                   fontSize=size, fillColor=color, textAnchor="middle"))

    def box(x, y, w, h, lines, fill=colors.white, stroke=RULE):
        add(Rect(x, y, w, h, 9, 9, fillColor=fill, strokeColor=stroke,
                      strokeWidth=1.2))
        mid = y + h / 2
        if len(lines) == 1:
            label(x + w / 2, mid - 3, lines[0], 8.4, True, NAVY)
        else:
            label(x + w / 2, mid + 4, lines[0], 8.3, True, NAVY)
            label(x + w / 2, mid - 9, lines[1], 7.1, False, MUTED)

    def arrow(points, color=TEAL):
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.7))
        (x1, y1), (x2, y2) = points[-2:]
        if x2 > x1:
            tip = [x2, y2, x2 - 7, y2 + 4, x2 - 7, y2 - 4]
        elif x2 < x1:
            tip = [x2, y2, x2 + 7, y2 + 4, x2 + 7, y2 - 4]
        elif y2 > y1:
            tip = [x2, y2, x2 - 4, y2 - 7, x2 + 4, y2 - 7]
        else:
            tip = [x2, y2, x2 - 4, y2 + 7, x2 + 4, y2 + 7]
        add(Polygon(tip, fillColor=color, strokeColor=color))

    add(Rect(0, 16, 354, 188, 14, 14,
                  fillColor=colors.HexColor("#EFF5F7"), strokeColor=RULE, strokeWidth=1))
    add(Rect(392, 16, 354, 188, 14, 14,
                  fillColor=colors.HexColor("#EFF5F7"), strokeColor=RULE, strokeWidth=1))
    label(177, 191, "GAME HOST / RETROPIE OR BATOCERA", 8.6, True, TEAL)
    label(569, 191, "ARDUINO UNO Q", 8.6, True, TEAL)

    box(20, 125, 140, 42, ["Launch / exit hook"])
    box(20, 55, 140, 48, ["RetroArch + core", "FCEUmm / Nestopia wrapper"])
    box(190, 55, 140, 48, ["Frame receiver"])
    box(190, 125, 140, 42, ["Raw Buddy pad + Router", "Merged Gyromite Player 2"])
    box(408, 87, 135, 70, ["Controller", "Virtual game model"],
        colors.HexColor("#E4F2F1"), TEAL)
    box(570, 125, 155, 42, ["Controller Router", "Shared 13 x 8 Matrix"])
    box(570, 47, 155, 42, ["Browser dashboard"])

    arrow([(160, 79), (190, 79)])
    label(175, 89, "frames", 6.6)
    arrow([(260, 103), (260, 125)])
    label(291, 112, "uinput", 6.6)
    arrow([(330, 78), (372, 78), (372, 121), (408, 121)])
    label(369, 66, "authenticated command", 6.6)
    arrow([(408, 101), (330, 101)], ORANGE)
    label(369, 107, "pad state", 6.6, color=ORANGE)
    arrow([(160, 146), (176, 146), (176, 174), (380, 174), (380, 146), (408, 146)])
    label(278, 179, "authenticated launch / exit", 6.6)
    arrow([(543, 145), (570, 145)])
    arrow([(543, 100), (555, 100), (555, 68), (570, 68)])
    label(616, 99, "state snapshot", 6.6)
    return diagram


def journey_route_diagram(width: float, route: str) -> Drawing:
    """Portrait vector companions to the two Mermaid history diagrams."""
    height = 166 if route == "frames" else 150
    diagram = Drawing(width, height)
    contents = Group()
    contents.scale(width / 499, 1)
    diagram.add(contents)

    def add(shape):
        contents.add(shape)

    def label(x, y, value, size=7.4, bold=False, color=BODY):
        add(String(x, y, value, fontName="DM-Bold" if bold else "DM",
                   fontSize=size, fillColor=color, textAnchor="middle"))

    def box(x, y, w, h, title, detail="", accent=False):
        add(Rect(x, y, w, h, 8, 8,
                 fillColor=colors.HexColor("#E4F2F1") if accent else colors.white,
                 strokeColor=TEAL if accent else RULE, strokeWidth=1.1))
        label(x + w / 2, y + h / 2 + (3 if detail else -2), title, 7.8, True, NAVY)
        if detail:
            label(x + w / 2, y + h / 2 - 10, detail, 6.7, color=MUTED)

    def arrow(points, color=TEAL):
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.6))
        (x1, y1), (x2, y2) = points[-2:]
        if x2 > x1:
            tip = [x2, y2, x2 - 6, y2 + 3.5, x2 - 6, y2 - 3.5]
        elif x2 < x1:
            tip = [x2, y2, x2 + 6, y2 + 3.5, x2 + 6, y2 - 3.5]
        elif y2 > y1:
            tip = [x2, y2, x2 - 3.5, y2 - 6, x2 + 3.5, y2 - 6]
        else:
            tip = [x2, y2, x2 - 3.5, y2 + 6, x2 + 3.5, y2 + 6]
        add(Polygon(tip, fillColor=color, strokeColor=color))

    add(Rect(0, 8, 499, height - 16, 12, 12,
             fillColor=colors.HexColor("#EFF5F7"), strokeColor=RULE))
    if route == "camera":
        label(249, 132, "CAMERA ROUTE / TESTED IN SEPTEMBER 2026", 8.1, True, TEAL)
        box(12, 69, 142, 51, "Console", "NES game + emulator")
        box(179, 69, 142, 51, "Modern LCD", "Kiyo Pro camera")
        box(346, 69, 142, 51, "UNO Q", "Light decoder + Buddy", True)
        box(179, 18, 142, 32, "Console Player 2")
        arrow([(154, 94), (179, 94)])
        arrow([(321, 94), (346, 94)])
        arrow([(417, 69), (417, 34), (321, 34)], ORANGE)
        arrow([(179, 34), (83, 34), (83, 69)], ORANGE)
        label(249, 57, "Gyromite pad state returns to the game", 6.6, color=ORANGE)
    elif route == "frames":
        label(249, 148, "FRAME LINK / CURRENT RELEASE PATH", 8.1, True, TEAL)
        box(10, 91, 105, 44, "Original core", "Runs the NES game")
        box(129, 91, 105, 44, "Frame wrapper", "Classifies video")
        box(248, 91, 105, 44, "Local receiver", "Checks full words")
        box(367, 91, 122, 44, "UNO Q model", "Moves virtual Buddy", True)
        box(129, 24, 105, 35, "RetroArch video")
        box(248, 24, 105, 35, "Virtual Player 2")
        arrow([(115, 113), (129, 113)])
        arrow([(234, 113), (248, 113)])
        arrow([(353, 113), (367, 113)])
        arrow([(181, 91), (181, 59)])
        arrow([(300, 91), (300, 59)])
        arrow([(427, 91), (427, 76), (334, 76), (334, 91)], ORANGE)
        label(423, 65, "Gyromite pad state", 6.5, color=ORANGE)
    else:
        raise ValueError(f"Unknown journey diagram: {route}")
    return diagram


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
    mermaid_count = 0

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
            flush()
            if line.startswith("```mermaid"):
                i += 1
                mermaid = []
                while i < len(lines) and not lines[i].startswith("```"):
                    mermaid.append(lines[i])
                    i += 1
                if i < len(lines):
                    i += 1
                source = "\n".join(mermaid)
                if path.name == "TECHNICAL_ARCHITECTURE.md" and all(
                        f"{node}[" in source
                        for node in ("HOOK", "WRAPPER", "RECEIVER", "PAD", "MODEL", "MATRIX", "WEB")):
                    picture = system_responsibilities_diagram(usable_width)
                elif path.name == "ENGINEERING_JOURNEY.md":
                    mermaid_count += 1
                    required = (("CONSOLE", "CAMERA", "UNO", "P2") if mermaid_count == 1
                                else ("CORE", "WRAPPER", "VIDEO", "RECEIVER", "MODEL", "PAD"))
                    if mermaid_count > 2 or not all(f"{node}[" in source for node in required):
                        raise ValueError(f"Unsupported Mermaid diagram in {path}")
                    picture = journey_route_diagram(usable_width,
                                                    "camera" if mermaid_count == 1 else "frames")
                else:
                    raise ValueError(f"Unsupported Mermaid diagram in {path}")
                story.extend([picture, Spacer(1, 9)])
                continue
            i += 1; code = []
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
    canvas.drawString(55, 67, "VERSION 0.1.7")
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
    vertical_margin = 36 if title == "Technical Reference" else 58
    doc = SimpleDocTemplate(str(path), pagesize=page_size, leftMargin=48,
                            rightMargin=48, topMargin=vertical_margin,
                            bottomMargin=vertical_margin,
                            title=f"R.O.B. Vision - {title}", author="R.O.B. Vision project")
    st = styles(compact=title in {"Technical Reference", "Engineering Journey", "Technical Test Results"})
    if title == "Technical Reference":
        st["body"].spaceAfter = 6
    elif title == "Engineering Journey":
        st["body"].leading = 11.8
        st["body"].spaceAfter = 4
        st["h2"].spaceBefore = 10
    elif title == "Game Manual":
        st["body"].leading = 11.8
        st["body"].spaceAfter = 5
        st["h2"].spaceBefore = 9
        st["h2"].spaceAfter = 6
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
                         else "TECHNICAL TEST RESULTS" if title == "Technical Test Results"
                         else "ENGINEERING JOURNEY" if title == "Engineering Journey"
                         else "INSTALLATION & SETUP" if title == "Installation & Setup"
                         else "GAME MANUAL" if title == "Game Manual"
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
                   ["MEET_BUDDY.md", "USER_GUIDE.md", "GAMEPLAY_GUIDE.md", "SETUP_GUIDE.md", "CONTROLLER_ROUTER.md", "INSTALLATION_GUIDE.md", "TROUBLESHOOTING.md"]),
        build_book("R.O.B.-Vision-Technical-Reference.pdf", "Technical Reference",
                   "Architecture, frame protocol, virtual model, pairing, and verification",
                   ["TECHNICAL_ARCHITECTURE.md"],
                   page_size=landscape(A4)),
        build_book("R.O.B.-Vision-Technical-Test-Results.pdf", "Technical Test Results",
                   "Optical capture, Kiyo Pro row tests, and libretro frame evidence",
                   ["TEST_RESULTS_TECHNICAL.md"],
                   page_size=landscape(A4)),
        build_book("R.O.B.-Vision-Engineering-Journey.pdf", "Engineering Journey",
                   "How camera experiments led to the libretro frame link",
                   ["ENGINEERING_JOURNEY.md"]),
        build_book("R.O.B.-Vision-Installation-and-Setup.pdf", "Installation & Setup",
                   "One command per device, pairing, and first game check",
                   ["INSTALLATION_AND_SETUP.md"]),
        build_book("R.O.B.-Vision-Game-Manual.pdf", "Game Manual",
                   "Play Gyromite and Stack-Up with Buddy",
                   ["GAME_MANUAL.md"]),
        build_book("R.O.B.-Vision-Matrix-Display-Guide.pdf", "Matrix Display Guide",
                   "UNO Q status animations and display states",
                   ["UNO_Q_MATRIX_DISPLAY.md"], page_size=landscape(A4)),
        build_quick(),
    ]
    WEB_GUIDES.mkdir(parents=True, exist_ok=True)
    for path in generated:
        shutil.copy2(path, WEB_GUIDES / path.name)
        print(path)
