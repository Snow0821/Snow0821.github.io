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
            for text in ['ink','secondary','accent','date']:
                for background in ['paper','tint','beige','table-meta','table-body']:
                    values=sorted([luminance(palette[text]),luminance(palette[background])])
                    ratio=(values[1]+.05)/(values[0]+.05)
                    self.assertGreaterEqual(ratio,4.5,(mode,text,background,ratio))
    def test_review_ready_palette_preserves_original_identity_reference(self):
        self.assertEqual(DESIGN['identityPalette'],
                         {'white':'#FFFFFF','charcoal':'#303735','mint':'#A8CFC3','beige':'#E8DFD0'})
        self.assertEqual(DESIGN['palette']['light']['ink'],'#303B40')
        self.assertEqual(DESIGN['palette']['light']['accent'],'#203C4B')
        self.assertEqual(DESIGN['palette']['light']['paper'],'#FFFFFF')
        self.assertEqual(DESIGN['palette']['light']['tint'],'#F0F6F2')
        self.assertEqual(DESIGN['palette']['light']['beige'],'#F5F1E9')
        self.assertIn('approved refined B editorial',DESIGN['paletteStatus'])
        self.assertEqual(set(DESIGN['palette']['light']),set(DESIGN['palette']['dark']))
        self.assertNotIn('camel',DESIGN['paletteCandidates'])
        self.assertEqual(DESIGN['palette']['light']['camel'],'#B68D64')
        self.assertEqual(DESIGN['palette']['dark']['camel'],'#B68D64')
        self.assertIn('--camel:',css_tokens())

    def test_web_and_pdf_tokens_keep_readable_sizes_and_column_proportions(self):
        self.assertEqual(TYPE['webBody'],16)
        self.assertEqual(TYPE['webSecondary'],14)
        self.assertGreaterEqual(TYPE['pdfBody'],10)
        self.assertGreaterEqual(TYPE['pdfSecondary'],9)
        self.assertEqual(sum(COLUMNS),100)
        self.assertIn('--teaching-provider-width:22%',css_tokens())
        root=Path(__file__).resolve().parents[1]
        current=re.search(r'<style id="snow-design-tokens">([^<]+)</style>',(root/'index.html').read_text())[1]
        self.assertEqual(css_tokens(),current)
    def test_control_outlines_meet_non_text_contrast(self):
        for mode,palette in DESIGN['palette'].items():
            self.assertNotEqual(palette['control-border'],palette['line'])
            for background in ['paper','tint','beige','table-meta','table-body']:
                low,high=sorted([luminance(palette['control-border']),luminance(palette[background])])
                self.assertGreaterEqual((high+.05)/(low+.05),3,(mode,background))
        css=(Path(__file__).resolve().parents[1]/'assets/site.css').read_text()
        for selector in ['.language','.action','select','.career-toggle']:
            rule=' '.join(re.findall(r'(?m)^\s*'+re.escape(selector)+r' \{([^}]+)\}',css))
            self.assertIn('border: 1px solid var(--control-border);',rule,selector)
        self.assertIn('border-bottom: 1px solid var(--line);',css)

    def test_web_and_pdf_share_local_heading_identity(self):
        root=Path(__file__).resolve().parents[1]
        css=(root/'assets/site.css').read_text()
        face=re.search(r'@font-face \{([^}]+)\}',css)[1]
        self.assertIn('font-family: "Nanum Myeongjo";',face)
        self.assertIn('font-weight: 700;',face)
        self.assertIn('font-display: swap;',face)
        font_path=re.search(r'url\("([^"\)]+)"\)',face)[1]
        self.assertEqual(font_path,'fonts/NanumMyeongjo-Bold.woff')
        self.assertEqual((root/'assets'/font_path).read_bytes()[:4],b'wOFF')
        self.assertTrue((root/'licenses/NanumMyeongjo-OFL.txt').is_file())
        self.assertEqual(TYPE['webHeadingWeight'],700)
        self.assertIn('--font-display-weight:700;',css_tokens())
        self.assertEqual(TYPE['pdfRegularFile'],'NanumGothic-Regular.ttf')
        self.assertEqual(TYPE['pdfBoldFile'],'NanumGothic-Bold.ttf')
        self.assertEqual(TYPE['pdfHeadingFile'],'NanumMyeongjo-Bold.ttf')
        self.assertIn('.panel-heading h2, .cv-heading, .fold-toggle, .history-group h3 { font-family: var(--font-display-family); font-weight: var(--font-display-weight); }',css)
        identity=re.search(r'\.cv-identity h1 \{([^}]+)\}',css)[1]
        self.assertIn('font-weight: var(--font-display-weight);',identity)

    def test_secondary_type_uses_one_readable_token(self):
        css=(Path(__file__).resolve().parents[1]/'assets/site.css').read_text()
        self.assertNotRegex(css,r'font-size:\s*(?:12|13|14)px')
        for selector in ['.aside-label','.cv-year','.record-meta','.paper-venue',
                         '.copy-status','.paper-topics li','.topic-tag','.resource-description',
                         '.history-meta','.career-detail-note','.teaching-period',
                         '.teaching-cell-label','.fold-preview','.footer']:
            rule=' '.join(re.findall(r'(?m)^\s*'+re.escape(selector)+r' \{([^}]+)\}',css))
            self.assertIn('font-size: var(--font-secondary-size);',rule,selector)
        self.assertIn('font: 400 var(--font-secondary-size)/1.8 var(--font-body-family);',css)

    def test_headers_and_tags_use_shared_surface_roles(self):
        css=(Path(__file__).resolve().parents[1]/'assets/site.css').read_text()
        for selector,background in [('.teaching-table th','tint'),('.paper-topics li','tint'),('.topic-tag','beige')]:
            rule=' '.join(re.findall(r'(?m)^\s*'+re.escape(selector)+r' \{([^}]+)\}',css))
            self.assertIn(f'background: var(--{background});',rule,selector)
            self.assertIn('color: var(--accent);',rule,selector)

    def test_camel_is_decorative_without_recoloring_text_or_controls(self):
        root=Path(__file__).resolve().parents[1]
        css=(root/'assets/site.css').read_text()
        self.assertNotIn('color: var(--camel)',css)
        for selector in ['.cv-identity','.cv-heading','.teaching-table th']:
            rule=' '.join(re.findall(r'(?m)^\s*'+re.escape(selector)+r' \{([^}]+)\}',css))
            self.assertIn('var(--camel)',rule,selector)
        code=(root/'scripts/build_cv.py').read_text()
        self.assertIn("('LINEABOVE', (0, header_index), (-1, header_index), .65, CAMEL)",code)
        self.assertNotIn('textColor=CAMEL',code)

    def test_teaching_body_surfaces_match_pdf_columns(self):
        root=Path(__file__).resolve().parents[1]
        css=(root/'assets/site.css').read_text()
        self.assertIn('.teaching-table th { padding: 9px 12px;',css)
        self.assertIn('.teaching-table td { padding: var(--space-row) 12px;',css)
        self.assertIn('.teaching-table td { padding: 10px 0; border: 0; }',css)
        self.assertIn('.teaching-table tbody td { background: var(--paper); }',css)
        self.assertIn('.teaching-table tbody td.teaching-course { background: var(--paper); }',css)
        code=(root/'scripts/build_cv.py').read_text()
        self.assertIn("('BACKGROUND', (0, header_index+1), (1, -1), HexColor(PALETTE['table-meta']))",code)
        self.assertIn("('BACKGROUND', (2, header_index+1), (2, -1), HexColor(PALETTE['table-body']))",code)
        self.assertIn('career_table.repeatRows = (header_index,)',code)

    def test_shared_panels_use_white_paper_and_restrained_radius(self):
        self.assertEqual(DESIGN['palette']['light']['paper'], '#FFFFFF')
        self.assertEqual(DESIGN['radius'], {'webPanel': 0, 'webTable': 0, 'pdfPanel': 5})
        self.assertIn('--panel-radius:0px;', css_tokens())
        self.assertIn('--table-radius:0px;', css_tokens())
        css=(Path(__file__).resolve().parents[1]/'assets/site.css').read_text()
        self.assertIn('background: var(--paper); border-radius: var(--panel-radius);', css)
        self.assertIn('border-collapse: separate; border-spacing: 0;', css)
        self.assertNotRegex(css, r'(?:teaching-table|current-roles|paper)\s*\{[^}]*overflow:\s*hidden')

    def test_semantic_table_and_native_disclosure_controls(self):
        records=teaching_records()
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
