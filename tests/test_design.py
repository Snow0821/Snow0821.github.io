"""Shared design and semantic responsive-table regression checks."""
import unittest,sys,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from design import DESIGN,TYPE,COLUMNS,css_tokens
from content import teaching_records,teaching_columns
import site_sections

def luminance(value):
    rgb=[int(value[i:i+2],16)/255 for i in (1,3,5)]
    linear=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb]
    return sum(c*w for c,w in zip(linear,[.2126,.7152,.0722]))

class SharedDesignTests(unittest.TestCase):
    def test_palette_text_pairs_have_aa_contrast(self):
        for mode,palette in DESIGN['palette'].items():
            for text in ['ink','secondary','accent']:
                for background in ['paper','tint','beige']:
                    values=sorted([luminance(palette[text]),luminance(palette[background])])
                    ratio=(values[1]+.05)/(values[0]+.05)
                    self.assertGreaterEqual(ratio,4.5,(mode,text,background,ratio))
    def test_requested_provisional_palette_is_shared(self):
        self.assertEqual(DESIGN['identityPalette'],
                         {'white':'#FFFFFF','charcoal':'#303735','mint':'#A8CFC3','beige':'#E8DFD0'})
        self.assertEqual(DESIGN['palette']['light']['ink'],'#303735')
        self.assertEqual(DESIGN['palette']['light']['accent'],'#253B53')
        self.assertIn('provisional',DESIGN['paletteStatus'])

    def test_web_and_pdf_tokens_keep_readable_sizes_and_column_proportions(self):
        self.assertGreaterEqual(TYPE['webBody'],16)
        self.assertGreaterEqual(TYPE['webSecondary'],14)
        self.assertGreaterEqual(TYPE['pdfBody'],10)
        self.assertGreaterEqual(TYPE['pdfSecondary'],9)
        self.assertEqual(sum(COLUMNS),100)
        self.assertIn('--teaching-provider-width:23%',css_tokens())
        root=Path(__file__).resolve().parents[1]
        self.assertIn(css_tokens(),(root/'index.html').read_text())
    def test_semantic_table_and_native_disclosure_controls(self):
        records=teaching_records('ai-data')
        html=site_sections.teaching_table(records)
        self.assertEqual(html.count('<th scope="col">'),3)
        self.assertEqual(html.count('<td '),3*len(records))
        self.assertIn('role="table"',html)
        self.assertIn('<caption class="sr-only">',html)
        for attrs in re.findall(r'<button ([^>]+)>',html):
            self.assertIn('type="button"',attrs)
            self.assertIn('aria-controls=',attrs)
            self.assertIn('data-title-ko=',attrs)
            self.assertIn('data-title-en=',attrs)
        css=(Path(__file__).resolve().parents[1]/'assets/site.css').read_text()
        self.assertIn('@media (max-width: 720px)',css)
        self.assertIn('.teaching-table td { display: block; width: 100%; }',css)
        self.assertIn(':focus-visible',css)
        self.assertIn('width: 44px; height: 44px',css)
    def test_decomposition_preserves_provider_course_role(self):
        for row in teaching_records():
            for lang in ['ko','en']:
                values=teaching_columns(row,lang)
                self.assertTrue(values['organization'])
                self.assertTrue(values['subject'])
                self.assertTrue(values['role'])
