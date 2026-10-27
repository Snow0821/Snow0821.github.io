"""Build the Korean A4 instructor profile from shared, reviewed public copy.

Usage: python scripts/build_instructor_profile.py [--output /tmp/profile.pdf]
Default output is assets/<pdfFilename>. INSTRUCTOR_PROFILE_OUTPUT_DIR (or
CV_OUTPUT_DIR) can redirect it. Local Nanum fonts are embedded; no network is
needed. The PDF is deterministic and an unchanged file is not rewritten.
"""

from __future__ import annotations

import argparse
from html import escape
from io import BytesIO
import json
import os
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
COPY_PATH = ROOT / "data/instructor-profile.json"
DESIGN_PATH = ROOT / "data/design.json"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _ko(value: dict) -> str:
    text = value["ko"]
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Displayed copy requires non-empty Korean text")
    return text


def _register_fonts(design: dict) -> None:
    typography = design["typography"]
    font_dir = Path(os.environ.get("CV_FONT_DIR", str(ROOT / "assets/fonts")))
    for name, filename in (
        ("ProfileBody", typography["pdfRegularFile"]),
        ("ProfileBold", typography["pdfBoldFile"]),
        ("ProfileHeading", typography["pdfHeadingFile"]),
    ):
        path = font_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing embedded font: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily("ProfileBody", normal="ProfileBody", bold="ProfileBold")


def build(output_path: str | Path | None = None) -> Path:
    """Create the profile PDF and return its path, without changing site files."""
    data = _read_json(COPY_PATH)
    design = _read_json(DESIGN_PATH)
    _register_fonts(design)
    colors = {key: HexColor(value) for key, value in design["palette"]["light"].items()}
    destination = Path(output_path) if output_path else Path(
        os.environ.get("INSTRUCTOR_PROFILE_OUTPUT_DIR", os.environ.get("CV_OUTPUT_DIR", str(ROOT / "assets")))
    ) / data["pdfFilename"]

    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4, pageCompression=1, invariant=1,
                    initialFontName="ProfileBody", initialFontSize=11, lang="ko-KR")
    canvas.setTitle(_ko(data["title"]))
    canvas.setAuthor("최순호")
    canvas.setSubject(_ko(data["role"]))
    canvas.setCreator("ReportLab / scripts/build_instructor_profile.py")
    canvas.setKeywords("최순호, 강사 소개, 프로그래밍, AI 교육, 신경망 연구")
    canvas.setViewerPreference("DisplayDocTitle", "true")

    page_width, page_height = A4
    margin = 44.0
    width = page_width - margin * 2
    y = page_height - 50.0
    minimum_bottom = 38.0
    canvas.setFillColor(colors["paper"])
    canvas.rect(0, 0, page_width, page_height, stroke=0, fill=1)

    def paragraph(
        text: str,
        top: float,
        *,
        x: float = margin,
        available_width: float = width,
        size: float = 11.0,
        leading: float = 18.5,
        font: str = "ProfileBody",
        color: str = "ink",
    ) -> float:
        # Space-based wrapping avoids splitting Korean words. TrueType text
        # stays searchable and copyable, rather than becoming an image.
        style = ParagraphStyle(
            "instructor-profile", fontName=font, fontSize=size, leading=leading,
            textColor=colors[color], wordWrap="LTR", splitLongWords=False,
        )
        normalized = text.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
        flowable = Paragraph(escape(normalized).replace("\n", "<br/>"), style)
        _, height = flowable.wrap(available_width, page_height)
        bottom = top - height
        if bottom < minimum_bottom:
            raise ValueError(f"One-page layout overflow at {text[:45]!r}: bottom={bottom:.1f}")
        flowable.drawOn(canvas, x, bottom)
        return bottom

    # AI-painted paper background; all biographical text stays live and searchable.
    background_path = ROOT / data["backgroundAsset"]
    if not background_path.is_file():
        raise FileNotFoundError(f"Missing profile background: {background_path}")
    background = ImageReader(str(background_path))
    image_width, image_height = background.getSize()
    scale = max(page_width / image_width, page_height / image_height)
    drawn_width, drawn_height = image_width * scale, image_height * scale
    canvas.drawImage(background, (page_width-drawn_width)/2, (page_height-drawn_height)/2,
                     width=drawn_width, height=drawn_height, mask='auto')
    # A light paper veil keeps the painted texture while protecting small type.
    canvas.saveState()
    canvas.setFillColor(colors["paper"])
    canvas.setFillAlpha(.25)
    canvas.rect(0, 0, page_width, page_height, fill=1, stroke=0)
    canvas.restoreState()
    paragraph("강사 소개", 793, available_width=265, size=10.5, leading=15,
              font="ProfileBold", color="secondary")
    paragraph(_ko(data["name"]), 764, available_width=265, size=36, leading=45,
              font="ProfileHeading")
    paragraph("CHOI SOON HO", 712, available_width=265, size=10, leading=15,
              font="ProfileBold", color="secondary")
    paragraph(_ko(data["role"]), 683, available_width=270, size=10.5, leading=16)
    paragraph(_ko(data["shortBio"]), 657, available_width=260, size=10.5,
              leading=16, color="secondary")

    y = 604
    y = paragraph(_ko(data["experienceTitle"]), y, size=19, leading=25, font="ProfileHeading")
    y -= 17
    for index, experience in enumerate(data["experience"]):
        top = y
        paragraph(_ko(experience["period"]), top-1, available_width=100,
                  size=9.5, leading=15, color="date", font="ProfileBold")
        x = margin + 115
        available = width - 115
        y = paragraph(_ko(experience["organization"]), top, x=x, available_width=available,
                      size=11.8, leading=17, font="ProfileBold")
        y -= 3
        y = paragraph(_ko(experience["role"]), y, x=x, available_width=available,
                      size=10.5, leading=15, color="accent")
        y -= 5
        y = paragraph(_ko(experience["description"]), y, x=x, available_width=available,
                      size=10.5, leading=16, color="secondary")
        y = min(y, top-63) - 12

    y -= 8
    y = paragraph(_ko(data["educationTitle"]), y, size=19, leading=25, font="ProfileHeading")
    y -= 14
    education_top = y
    column_width = (width - 28) / 2
    bottoms = []
    for index, education in enumerate(data["educationRecords"]):
        x = margin + index * (column_width + 28)
        top = paragraph(str(education["year"]), education_top, x=x,
                        available_width=column_width, size=10, leading=15,
                        color="date", font="ProfileBold") - 5
        top = paragraph(_ko(education["degree"]), top, x=x, available_width=column_width,
                        size=13, leading=19, font="ProfileBold") - 5
        top = paragraph(_ko(education["school"]), top, x=x, available_width=column_width,
                        size=10.5, leading=16) - 3
        top = paragraph(_ko(education["field"]), top, x=x, available_width=column_width,
                        size=10.5, leading=16, color="secondary")
        bottoms.append(top)
    y = min(bottoms) - 23
    y = paragraph(_ko(data["paperTitle"]), y, size=14, leading=20, font="ProfileHeading") - 7
    paper = data["representativePaper"]
    y = paragraph(paper["title"], y, size=11, leading=16, font="ProfileBold") - 5
    y = paragraph(paper["venue"] + " · " + _ko(paper["authorRole"]), y,
                  size=10, leading=15, color="ink")

    footer_y = 58
    if y < footer_y + 28:
        raise ValueError(f"Profile content overlaps footer: y={y}")
    canvas.setStrokeColor(colors["line"])
    canvas.setLineWidth(.6)
    canvas.line(margin, footer_y+20, page_width-margin, footer_y+20)
    link_size = 10
    email = data["email"]
    web_url = data["url"]
    web_label = web_url.removeprefix("https://").rstrip("/")
    email_width = pdfmetrics.stringWidth(email, "ProfileBody", link_size)
    web_width = pdfmetrics.stringWidth(web_label, "ProfileBody", link_size)
    canvas.setFillColor(colors["ink"])
    canvas.setFont("ProfileBody", link_size)
    canvas.drawString(margin, footer_y, email)
    canvas.drawRightString(page_width-margin, footer_y, web_label)
    canvas.setFillColor(colors["ink"])
    canvas.setFont("ProfileBody", 9.5)
    canvas.drawCentredString(page_width/2, footer_y, _ko(data["asOf"]))
    canvas.linkURL(f"mailto:{email}", (margin, footer_y-3, margin+email_width, footer_y+12), relative=0, thickness=0)
    canvas.linkURL(web_url, (page_width-margin-web_width, footer_y-3, page_width-margin, footer_y+12), relative=0, thickness=0)

    canvas.showPage()
    canvas.save()
    result = buffer.getvalue()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or destination.read_bytes() != result:
        destination.write_bytes(result)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Explicit PDF file path; default is assets/<pdfFilename>")
    args = parser.parse_args()
    print(build(args.output))


if __name__ == "__main__":
    main()
