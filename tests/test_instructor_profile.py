"""The one-page self-introduction stays person-centered and additive."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import site_sections

DATA = json.loads((ROOT / 'data/instructor-profile.json').read_text())


class InstructorProfileTests(unittest.TestCase):
    def test_profile_is_person_centered_and_bilingual(self):
        self.assertEqual(DATA['title']['ko'], '최순호 강사 소개')
        self.assertEqual(len(DATA['paragraphs']), 2)
        self.assertEqual(len(DATA['experience']), 3)
        for value in [DATA['title'], DATA['role'], *DATA['paragraphs'], DATA['education'],
                      DATA['research'], DATA['cardTitle'], DATA['cardDescription']]:
            self.assertEqual(set(value), {'ko', 'en'})
            self.assertTrue(all(value.values()))
        self.assertIn('최순호입니다', DATA['paragraphs'][0]['ko'])
        text = json.dumps(DATA, ensure_ascii=False)
        for rejected in ['AI로 직접 만들어 보는 하루', '클래스 구성 예시', '클래스 문의하기', '일정·시간·인원·비용']:
            self.assertNotIn(rejected, text)

    def test_only_supported_contact_and_credentials(self):
        portfolio = json.loads((ROOT / 'data/portfolio.json').read_text())
        self.assertEqual(DATA['email'], portfolio['profile']['email'])
        self.assertEqual(DATA['url'], portfolio['profile']['portfolioUrl'])
        text = ' '.join(item['description']['ko'] for item in DATA['experience'])
        self.assertIn('Codex 업무 비서 제작 과정 진행 중', text)
        self.assertIn('학습 이슈 조율', text)
        self.assertIn('자료구조·알고리즘', text)
        self.assertNotIn('하나생명', json.dumps(DATA, ensure_ascii=False))
        self.assertTrue(all(p['authorRole'] == 'first' for p in portfolio['papers']))

    def test_download_is_inside_existing_document_area(self):
        html = (ROOT / 'index.html').read_text()
        documents = site_sections.documents()
        self.assertIn(documents, html)
        self.assertEqual(html.count('id="instructor-profile"'), 1)
        self.assertIn('class="document-card document-card-profile"', documents)
        self.assertIn(f'href="assets/{DATA["pdfFilename"]}" download=', documents)
        self.assertTrue((ROOT / 'assets' / DATA['pdfFilename']).is_file())
        for section in ['snow-panel-home', 'snow-panel-publications', 'snow-panel-teaching']:
            self.assertEqual(html.count(f'id="{section}"'), 1)
        self.assertNotIn('id="oneday"', html)
        self.assertNotIn('One-Day-Class', html)
        self.assertNotIn('AI 원데이클래스', html)

    def test_pdf_is_one_a4_page_with_full_text_embedded_fonts_and_links(self):
        try:
            from pypdf import PdfReader
        except ImportError:
            self.skipTest('pypdf is optional for site-only validation')
        pdf = PdfReader(ROOT / 'assets' / DATA['pdfFilename'])
        self.assertEqual(len(pdf.pages), 1)
        page = pdf.pages[0]
        self.assertAlmostEqual(float(page.mediabox.width), 595.276, delta=.1)
        self.assertAlmostEqual(float(page.mediabox.height), 841.890, delta=.1)
        compact = ''.join(page.extract_text().split())
        for value in [DATA['title']['ko'], DATA['email'], *[x['ko'] for x in DATA['paragraphs']], DATA['education']['ko'], DATA['research']['ko']]:
            self.assertIn(''.join(value.split()), compact)
        links = {str(x.get_object()['/A']['/URI']) for x in page.get('/Annots', [])
                 if x.get_object().get('/A', {}).get('/S') == '/URI'}
        self.assertIn('mailto:' + DATA['email'], links)
        self.assertIn(DATA['url'], links)
        embedded = []
        for reference in page['/Resources']['/Font'].values():
            font = reference.get_object()
            if 'Nanum' in str(font.get('/BaseFont', '')):
                descriptor = font['/FontDescriptor'].get_object()
                self.assertTrue(any(key in descriptor for key in ['/FontFile', '/FontFile2', '/FontFile3']))
                embedded.append(str(font['/BaseFont']))
        self.assertGreaterEqual(len(embedded), 3)


if __name__ == '__main__':
    unittest.main()
