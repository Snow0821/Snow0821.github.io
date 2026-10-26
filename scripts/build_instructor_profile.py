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
    margin = 52.0
    width = page_width - margin * 2
    y = page_height - 50.0
    minimum_bottom = 46.0
    canvas.setFillColor(colors["paper"])
    canvas.rect(0, 0, page_width, page_height, stroke=0, fill=1)

    def paragraph(
        text: str,
        top: float,
        *,
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
        _, height = flowable.wrap(width, page_height)
        bottom = top - height
        if bottom < minimum_bottom:
            raise ValueError(f"One-page layout overflow at {text[:45]!r}: bottom={bottom:.1f}")
        flowable.drawOn(canvas, margin, bottom)
        return bottom

    y = paragraph(_ko(data["title"]), y, size=29, leading=38, font="ProfileHeading")
    y -= 8
    y = paragraph(_ko(data["role"]), y, size=11, leading=16, color="secondary")
    y -= 26

    for index, text in enumerate(data["paragraphs"]):
        if index:
            y -= 13
        y = paragraph(_ko(text), y)

    y -= 26
    y = paragraph(_ko(data["experienceTitle"]), y, size=14, leading=20, font="ProfileHeading")
    y -= 11
    for index, experience in enumerate(data["experience"]):
        if index:
            y -= 12
        heading = _ko(experience["organization"]) + "  |  " + _ko(experience["role"])
        y = paragraph(heading, y, size=10.5, leading=16, font="ProfileBold")
        y -= 3
        y = paragraph(_ko(experience["description"]), y, size=10.5, leading=16, color="secondary")

    y -= 24
    y = paragraph(_ko(data["backgroundTitle"]), y, size=14, leading=20, font="ProfileHeading")
    y -= 9
    y = paragraph(_ko(data["education"]), y, size=10.5, leading=17)
    y -= 5
    y = paragraph(_ko(data["research"]), y, size=10.5, leading=17, color="secondary")

    y -= 24
    canvas.setStrokeColor(colors["line"])
    canvas.setLineWidth(0.6)
    canvas.line(margin, y, page_width - margin, y)
    y -= 15
    y = paragraph(_ko(data["contactTitle"]), y, size=10.5, leading=15, font="ProfileBold", color="secondary")
    y -= 7
    link_size = 10.5
    baseline = y - 10.5
    if baseline < minimum_bottom:
        raise ValueError(f"One-page layout overflow at contact links: {baseline:.1f}")
    email = data["email"]
    web_url = data["url"]
    web_label = web_url.removeprefix("https://").rstrip("/")
    web_width = pdfmetrics.stringWidth(web_label, "ProfileBody", link_size)
    email_width = pdfmetrics.stringWidth(email, "ProfileBody", link_size)
    web_x = page_width - margin - web_width
    if margin + email_width + 20 > web_x:
        raise ValueError("Contact addresses do not fit on one line")
    canvas.setFillColor(colors["accent"])
    canvas.setFont("ProfileBody", link_size)
    canvas.drawString(margin, baseline, email)
    canvas.drawString(web_x, baseline, web_label)
    canvas.linkURL(f"mailto:{email}", (margin, baseline - 3, margin + email_width, baseline + 12), relative=0, thickness=0)
    canvas.linkURL(web_url, (web_x, baseline - 3, web_x + web_width, baseline + 12), relative=0, thickness=0)

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
