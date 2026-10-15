"""Geometry checks for PDF pills, independent of locally installed CJK fonts."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
try:
    from build_cv import PillTags,table
except ImportError:
    PillTags=None

@unittest.skipIf(PillTags is None,'ReportLab is optional for site-only validation')
class PDFLayoutTests(unittest.TestCase):
    def tags(self,labels,width):
        result=PillTags(labels)
        result.font_name='Helvetica'
        result.wrap(width,1000)
        return result

    def assert_bounds(self,result):
        for x,y,w,h,paragraph in result.placements:
            self.assertGreaterEqual(x,0)
            self.assertGreaterEqual(y,-.001)
            self.assertLessEqual(x+w,result.width+.001)
            self.assertLessEqual(y+h,result.height+.001)
            self.assertGreaterEqual(w-paragraph.width,result.pad_x*2-.001)
            self.assertGreaterEqual(h-paragraph.height,result.pad_y*2-.001)

    def test_tags_have_measured_internal_padding(self):
        result=self.tags(['Weight Quantization','Vision Transformers'],400)
        self.assert_bounds(result)
        self.assertEqual(len(result.placements),2)
        first,second=result.placements
        self.assertGreaterEqual(second[0]-first[0]-first[2],result.gap-.001)
        self.assertEqual(first[1],second[1])

    def test_tags_wrap_at_narrow_bounds_without_shrinking_type(self):
        result=self.tags(['Neural Architecture Learning','VeryLongUnbrokenResearchMethodLabel','Short'],100)
        self.assert_bounds(result)
        self.assertEqual(result.font_size,9)
        self.assertGreater(len({row[1] for row in result.placements}),1)
        self.assertTrue(all(row[4].style.fontSize==9 for row in result.placements))

    def test_empty_tag_set_is_safe(self):
        result=self.tags([],300)
        self.assertEqual(result.height,0)
        self.assertEqual(result.placements,[])

    def test_career_rows_cannot_split_internally(self):
        result=table([['date','course']],[100,300],header=False)
        self.assertEqual(result.splitByRow,1)
        self.assertEqual(result.splitInRow,0)


    def test_rounded_panel_geometry_keeps_padding_inside_corners(self):
        result=table([['date','course']],[100,300],header=False,pad=5,
                     surface='table-body',rounded=True)
        self.assertEqual(result._cornerRadii,[5,5,5,5])
        for cell in result._cellStyles[0]:
            self.assertGreaterEqual(cell.leftPadding,5)
            self.assertGreaterEqual(cell.rightPadding,5)
            self.assertGreaterEqual(cell.topPadding,5)
            self.assertGreaterEqual(cell.bottomPadding,5)

class FinishedPDFOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from pypdf import PdfReader
        except ImportError:
            raise unittest.SkipTest('pypdf is optional for site-only validation')
        cls.read_pdf = staticmethod(PdfReader)
        cls.root = Path(__file__).resolve().parents[1]

    def test_complete_sections_follow_teaching_first_order_at_readable_size(self):
        for lang, career, ai, programming, other in [
            ('EN', 'Professional Experience', 'AI & Data Education',
             'Programming, Data Structures & Algorithms Education', 'Other Activities')]:
            reader = self.read_pdf(self.root / 'assets' / f'Choi-Soon-Ho-CV-{lang}.pdf')
            self.assertEqual(len(reader.pages), 3)
            pages = [page.extract_text() for page in reader.pages]
            career_page=2
            programming_page=1
            self.assertNotIn(career, pages[0].splitlines())
            self.assertIn(career, pages[career_page])
            self.assertIn('2024.03-2024.05', pages[career_page])
            self.assertIn('2014.06-2015.01', pages[career_page])
            self.assertNotIn(ai, ''.join(pages))
            self.assertIn('교육 경력' if lang=='KO' else 'Teaching Experience',pages[0])
            self.assertIn('2026.08-2026.10', pages[0])
            self.assertNotIn(programming, ''.join(pages))
            self.assertIn('Do IT!',pages[1])
            other_page=next(i for i,page in enumerate(pages) if other in page)
            self.assertGreaterEqual(other_page,career_page)
            self.assertNotIn('(계속)', ''.join(pages))
            self.assertNotIn('(continued)', ''.join(pages))
            self.assertIn('KimAnNa', pages[other_page])
            role = '제1저자' if lang == 'KO' else 'First author'
            self.assertEqual(sum(page.count(role) for page in pages), 3)
            self.assertTrue(any(page.count(role)==3 for page in pages))
            self.assertIn('Cadet', pages[other_page])

    def test_approved_korean_editorial_cv_is_four_pages(self):
        reader = self.read_pdf(self.root / 'assets' / 'Choi-Soon-Ho-CV-KO.pdf')
        self.assertEqual(len(reader.pages), 4)
        pages = [page.extract_text() for page in reader.pages]
        text = '\n'.join(pages)
        self.assertIn('현재 활동', pages[0])
        self.assertIn('학위·자격', pages[0])
        self.assertIn('주요 강의 경험', pages[0])
        self.assertIn('하나생명', pages[1])
        self.assertIn('디지털새싹', pages[2])
        self.assertIn('연구활동', pages[3])
        self.assertIn('경력', pages[3])
        self.assertIn('2014.06-2015.01', pages[3])
        self.assertIn('컴퓨터공학·전자공학', text)
        self.assertEqual(text.count('보조강사'), 3)
        self.assertIn('PBL 퍼실리테이터', text)
        self.assertIn('NCS 확인강사', text)
        self.assertNotIn('주강사', text)
        self.assertNotIn('교안 준비', text)
        self.assertNotIn('교안 구성', text)
        self.assertIn('Soon Ho Choi', text)
        self.assertIn('Soo Yeon Yoon', text)
        self.assertIn('Soo-Yeon Yoon', text)
        self.assertNotIn('KimAnNa', text)  # The website retains this full-history record.

    def test_embedded_korean_fonts_keep_unicode_maps(self):
        for lang in ['KO', 'EN']:
            reader = self.read_pdf(self.root / 'assets' / f'Choi-Soon-Ho-CV-{lang}.pdf')
            font_names = set()
            for page in reader.pages:
                for reference in page['/Resources']['/Font'].values():
                    font = reference.get_object()
                    if font.get('/Subtype') != '/TrueType':
                        continue
                    font_names.add(str(font['/BaseFont']))
                    self.assertIn('/ToUnicode', font)
                    self.assertIn('/FontFile2', font['/FontDescriptor'].get_object())
            self.assertTrue(any('NanumMyeongjoBold' in name for name in font_names))
            self.assertTrue(any('NanumGothic' in name for name in font_names))
