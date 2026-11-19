"""The instructor handout is a public, single-page summary with official role dates."""
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
PROFILE = json.loads((ROOT / "data/instructor-profile.json").read_text(encoding="utf-8"))


def compact(value):
    return re.sub(r'\s+', '', value)


class InstructorProfileTests(unittest.TestCase):
    def test_profile_content_and_document_links(self):
        self.assertEqual(PROFILE["title"]["ko"], "최순호 강사 소개")
        self.assertEqual(len(PROFILE["current"]), 2)
        self.assertEqual({row["organization"]["ko"] for row in PROFILE["current"]}, {"엘리스그룹", "코더랜드"})
        experiences = {row["organization"]["ko"]: row for row in PROFILE["experience"]}
        self.assertEqual(experiences["모두의연구소 · 코디세이"]["period"]["ko"], "2026.06.01–10.31")
        self.assertEqual(experiences["고양 스마트시티즌 · 에듀코어센터"]["period"]["ko"], "2026.08–10")
        self.assertIn("AI 크리에이터", experiences["에이블런 · 인천 AI디지털배움터"]["description"]["ko"])
        for item in PROFILE["paragraphs"]:
            self.assertEqual(set(item), {"ko", "en"})
            self.assertTrue(all(item.values()))
        self.assertIn("://dblp.org/", PROFILE["representativePaper"]["url"])
        self.assertTrue((ROOT / "assets" / PROFILE["pdfFilename"]).is_file())

    def test_clickable_one_page_with_searchable_text(self):
        try:
            from pypdf import PdfReader
            from build_instructor_profile import build
        except ImportError:
            self.skipTest("Optional PDF dependencies are unavailable")
        with tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir) / "profile.pdf"
            build(output)
            self.assertEqual(output.read_bytes(), (ROOT / "assets" / PROFILE["pdfFilename"]).read_bytes())
            pdf = PdfReader(output)
            self.assertEqual(len(pdf.pages), 1)
            page = pdf.pages[0]
            self.assertAlmostEqual(float(page.mediabox.width), 595.276, delta=.1)
            self.assertAlmostEqual(float(page.mediabox.height), 841.890, delta=.1)
            words = compact(page.extract_text())
            expected = [PROFILE["name"]["ko"], PROFILE["shortBio"]["ko"], PROFILE["representativePaper"]["title"],
                        PROFILE["updated"].replace("-", "."), PROFILE["email"]]
            for roles in ("current", "experience"):
                for row in PROFILE[roles]:
                    expected.extend(row[key]["ko"] for key in ("organization", "role", "period", "description"))
            for education in PROFILE["educationRecords"]:
                expected.extend(education[key]["ko"] for key in ("school", "field", "degree"))
            for field in expected:
                self.assertIn(compact(field), words)
            links = {str(annotation.get_object()["/A"]["/URI"]) for annotation in page["/Annots"]}
            self.assertEqual(links, {PROFILE["url"], "mailto:" + PROFILE["email"], PROFILE["representativePaper"]["url"]})
