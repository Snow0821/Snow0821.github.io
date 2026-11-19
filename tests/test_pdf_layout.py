"""The public CVs and career statement retain their intended content, links and page layouts."""
from html import unescape
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from build_documents import DOCUMENTS, read_copy


def compact(text):
    return re.sub(r'\s+', '', text)


class DocumentReadingTests(unittest.TestCase):
    def test_reading_pages_show_source_text(self):
        for slug, (_, filename) in DOCUMENTS.items():
            copy = read_copy(slug)
            html = (ROOT / slug / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'href="../assets/{filename}"', html)
            self.assertNotRegex(html.lower(), r'<(details|summary|script)\b')
            self.assertIn(copy["updated"], html)
            visible = compact(unescape(re.sub(r'<[^>]+>', '', html)))
            for page in copy["pages"]:
                for block in page["blocks"]:
                    self.assertIn(compact(block["text"]), visible)
                    if block.get("link"):
                        self.assertIn(block["link"], html)


class FinishedPDFOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from pypdf import PdfReader
            from build_cv import build, build_career_statement
        except ImportError:
            raise unittest.SkipTest("Optional PDF dependencies are unavailable")
        cls.reader = staticmethod(PdfReader)
        cls.build = staticmethod(build)
        cls.build_career = staticmethod(build_career_statement)

    def test_files_rebuild_without_relying_on_reviewed_binary_copies(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict('os.environ', {"CV_OUTPUT_DIR": directory}):
                built = [self.build("ko"), self.build("en"), self.build_career()]
            for file in built:
                self.assertEqual(file.read_bytes(), (ROOT / "assets" / file.name).read_bytes())

    def test_all_reviewed_blocks_are_searchable_in_their_own_pdf_pages(self):
        for slug, key, filename, length in [
            ("cv", "pages", DOCUMENTS["cv"][1], 2),
            ("cv", "english_pages", "Choi-Soon-Ho-CV-EN.pdf", 3),
            ("career-statement", "pages", DOCUMENTS["career-statement"][1], 4),
        ]:
            copy = read_copy(slug)
            pdf = self.reader(ROOT / "assets" / filename)
            self.assertEqual(len(pdf.pages), length)
            for index, (page, source) in enumerate(zip(pdf.pages, copy[key]), 1):
                visible = compact(page.extract_text())
                self.assertIn(copy["updated"].replace("-", "."), visible)
                self.assertIn(f"{index}/{length}", visible)
                for block in source["blocks"]:
                    self.assertIn(compact(block["text"]), visible, block["text"])
                links = {str(a.get_object()["/A"]["/URI"]) for a in page["/Annots"]}
                self.assertTrue({b["link"] for b in source["blocks"] if "link" in b}.issubset(links))
                for link in links:
                    self.assertNotRegex(link, r'drive\.google|docs\.google|mail\.google|/learn/')
                for reference in page['/Resources']['/Font'].values():
                    font = reference.get_object()
                    if font.get('/Subtype') == '/TrueType':
                        self.assertIn('/ToUnicode', font)
                        self.assertIn('/FontFile2', font['/FontDescriptor'].get_object())

    def test_verified_current_roles_and_awards(self):
        for lang in ("KO", "EN"):
            reader = self.reader(ROOT / "assets" / f"Choi-Soon-Ho-CV-{lang}.pdf")
            all_text = " ".join(page.extract_text() for page in reader.pages)
            self.assertIn("아이디어를 콘텐츠로, AI 크리에이터" if lang == "KO" else "Ideas into Content: AI Creator", all_text)
            self.assertIn("코치" if lang == "KO" else "Coach", all_text)
            self.assertIn("정보올림피아드" if lang == "KO" else "Olympiad", all_text)
            self.assertNotIn("3년 연속", all_text)
            self.assertNotIn("우수논문상", all_text)
            self.assertNotIn("12.31", all_text)
