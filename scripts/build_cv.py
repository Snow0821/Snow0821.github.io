"""Render reviewed document copy as searchable and printable A4 PDFs."""
from html import escape
from io import BytesIO
import os
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

from build_documents import DOCUMENTS, ROOT, read_copy, write_if_changed

INK = "#202C2B"
ACCENT = "#285D50"
MUTED = "#4C5E59"
RULE = "#CBD4CD"
MARGIN = 45
PAGE_W, PAGE_H = A4
TEXT_W = PAGE_W - 2 * MARGIN
EMAIL = "sosaror@gmail.com"
PORTFOLIO = "https://snow0821.github.io/"
# Font, point size, line height, gap above the block, text colour.
TYPE = {
    "heading": ("Heading", 16.5, 22, 19, ACCENT),
    "lead": ("Bold", 12.2, 17.3, 10, INK),
    "meta": ("Regular", 10.0, 14, 1.5, MUTED),
    "body": ("Regular", 11.0, 16.7, 2.5, INK),
}


def configure_fonts():
    directory = Path(os.environ.get("CV_FONT_DIR", ROOT / "assets" / "fonts"))
    for label, filename in (("Regular", "NanumGothic-Regular.ttf"), ("Bold", "NanumGothic-Bold.ttf"),
                            ("Heading", "NanumMyeongjo-Bold.ttf")):
        pdfmetrics.registerFont(TTFont(label, str(directory / filename)))


def output_path(filename):
    return Path(os.environ.get("CV_OUTPUT_DIR", ROOT / "assets")) / filename


def prepare(block):
    font, size, leading, gap, color = TYPE[block["role"]]
    value = "<br/>".join(escape(line) for line in block["text"].splitlines())
    if block.get("link"):
        color = ACCENT
        value = f'<link href="{escape(block["link"], quote=True)}" underline="yes" color="{ACCENT}">{value}</link>'
    style = ParagraphStyle(block["role"], fontName=font, fontSize=size, leading=leading,
                           textColor=HexColor(color), splitLongWords=True, spaceShrinkage=0.0)
    paragraph = Paragraph(value, style)
    _, height = paragraph.wrap(TEXT_W, PAGE_H)
    return paragraph, height, gap


def draw_footer(canvas, date, page_number, count):
    canvas.setStrokeColor(HexColor(RULE))
    canvas.line(MARGIN, 46, PAGE_W - MARGIN, 46)
    canvas.setFillColor(HexColor(MUTED))
    canvas.setFont("Regular", 9)
    x = MARGIN
    for label, url in ((PORTFOLIO.removeprefix("https://").rstrip("/"), PORTFOLIO),
                       (EMAIL, f"mailto:{EMAIL}")):
        width = pdfmetrics.stringWidth(label, "Regular", 9)
        canvas.drawString(x, 30, label)
        canvas.linkURL(url, (x, 27, x + width, 39), thickness=0)
        x += width + 12
    canvas.drawRightString(PAGE_W - MARGIN, 30, f"{date.replace('-', '.')}   ·   {page_number}/{count}")


def render(title, subtitle, lang, date, pages, filename):
    configure_fonts()
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4, invariant=True, pageCompression=True,
                    initialFontName="Regular", lang="ko-KR" if lang == "ko" else "en")
    canvas.setAuthor("Choi Soon Ho")
    canvas.setTitle(title)
    canvas.setSubject(subtitle)
    canvas.setViewerPreference("DisplayDocTitle", "true")
    for index, page in enumerate(pages, 1):
        canvas.setStrokeColor(HexColor(RULE))
        canvas.setFillColor(HexColor(INK))
        if index == 1:
            canvas.setFont("Heading", 26)
            canvas.drawString(MARGIN, PAGE_H - 59, title)
            canvas.setFillColor(HexColor(MUTED))
            canvas.setFont("Regular", 10.5)
            canvas.drawString(MARGIN, PAGE_H - 81, subtitle)
            top = PAGE_H - 97
        else:
            canvas.setFont("Bold", 11)
            canvas.drawString(MARGIN, PAGE_H - 44, title)
            top = PAGE_H - 57
        canvas.setLineWidth(.65)
        canvas.line(MARGIN, top, PAGE_W - MARGIN, top)
        start_y = top - 14
        rows = [prepare(item) for item in page["blocks"]]
        total_gap = sum(gap for _, _, gap in rows[1:])
        available_gap = start_y - 58 - sum(height for _, height, _ in rows)
        scale = min(1, available_gap / total_gap) if total_gap else 1
        if scale < .26:
            raise ValueError(f"{title}, page {index} has too much text ({available_gap=:.1f})")
        y = start_y
        for row_no, (paragraph, height, gap) in enumerate(rows):
            if row_no:
                y -= gap * scale
            y -= height
            paragraph.drawOn(canvas, MARGIN, y)
        draw_footer(canvas, date, index, len(pages))
        canvas.showPage()
    canvas.save()
    write_if_changed(Path(filename), buffer.getvalue())
    return filename


def build(lang):
    if lang not in ("ko", "en"):
        raise ValueError(f"Unknown CV language: {lang!r}")
    copy = read_copy("cv")
    korean = lang == "ko"
    return render("최순호 · 국문 CV" if korean else "Choi Soon Ho · Curriculum Vitae",
                  "독립연구자 · AI·CS 강사" if korean else "Independent researcher · AI and computer science instructor",
                  lang, copy["updated"], copy["pages" if korean else "english_pages"],
                  output_path(f"Choi-Soon-Ho-CV-{lang.upper()}.pdf"))


def build_career_statement():
    copy = read_copy("career-statement")
    return render("최순호 · 경력기술서", "독립연구자 · AI·CS 강사", "ko", copy["updated"], copy["pages"],
                  output_path(DOCUMENTS["career-statement"][1]))


if __name__ == "__main__":
    import sys
    for language in sys.argv[1:] or ("ko", "en"):
        print(build(language))
