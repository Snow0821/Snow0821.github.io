"""Test the actual public pages, their accessibility and the publication boundary."""
import hashlib
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from content import DATA, bibtex, reference
from design import DESIGN, css_tokens
from rendered_site import LANGUAGES, PAGES, ROOT, SECTIONS, DocumentParser, page, page_path, section, text


def contrast(first, second):
    def luminance(value):
        rgb = [int(value[i:i+2], 16) / 255 for i in (1, 3, 5)]
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055)**2.4 for c in rgb]
        return sum(c*w for c, w in zip(linear, (0.2126, 0.7152, 0.0722)))
    low, high = sorted((luminance(first), luminance(second)))
    return (high + 0.05) / (low + 0.05)


class PublicDesignTests(unittest.TestCase):
    def test_text_links_and_controls_have_readable_contrast(self):
        for mode, palette in DESIGN['palette'].items():
            for fg in ('ink', 'secondary', 'accent', 'date'):
                for bg in ('paper', 'tint'):
                    self.assertGreaterEqual(contrast(palette[fg], palette[bg]), 4.5, (mode, fg, bg))
            self.assertGreaterEqual(contrast(palette['selected'], palette['on-selected']), 4.5)
            self.assertGreaterEqual(contrast(palette['control-border'], palette['paper']), 3)

    def test_local_fonts_load_without_blocking_text(self):
        css = (ROOT/'assets/site.css').read_text()
        faces = re.findall(r'@font-face\s*\{([^}]+)\}', css)
        self.assertTrue(faces)
        for face in faces:
            self.assertRegex(face, r'font-display\s*:\s*swap')
            filename = re.search(r'url\(["\']?([^)"\']+)', face)[1]
            self.assertNotIn('://', filename)
            self.assertIn((ROOT/'assets'/filename).read_bytes()[:4], [b'wOFF',b'wOF2'])
        for font in ('Pretendard','NanumMyeongjo'):
            self.assertTrue((ROOT/'licenses'/f'{font}-OFL.txt').exists())

    def test_static_pages_have_a_single_landmark_and_unique_identifiers(self):
        for lang in LANGUAGES:
            for tab in PAGES:
                doc = page(lang, tab)
                with self.subTest(lang=lang, page=tab):
                    self.assertEqual(doc.find('html').get('lang'), lang)
                    self.assertEqual(len(doc.findall('.//main')), 1)
                    self.assertEqual(len(doc.findall('.//main//h1')), 1)
                    self.assertTrue(text(doc.find('.//title')))
                    self.assertGreater(len(text(doc.find('.//main'))), 100)
                    ids = [el.get('id') for el in doc.iter() if 'id' in el.attrib]
                    self.assertEqual(len(set(ids)), len(ids))
                    self.assertFalse(any(el.tag in ('details','summary') or 'aria-expanded' in el.attrib
                                         for el in doc.iter()))
                    self.assertFalse(any(el.get('role') in ('tab','tabpanel','tablist') for el in doc.iter()))

    def test_documents_reference_current_styles_and_interactions(self):
        for lang in LANGUAGES:
            for tab in PAGES:
                html = page_path(lang, tab).read_text()
                self.assertIn(css_tokens(), html)
                for ext in ('js','css'):
                    filename = 'site.' + ext
                    digest = hashlib.sha256((ROOT/'assets'/filename).read_bytes()).hexdigest()[:12]
                    self.assertIn('/assets/' + filename + '?v=' + digest, html)

    def test_language_alternates_and_skip_links_point_to_the_right_page(self):
        for lang in LANGUAGES:
            for tab in PAGES:
                doc = page(lang,tab)
                canonical = doc.find('.//link[@rel="canonical"]').get('href')
                site_path = page_path(lang,tab).relative_to(ROOT).as_posix().removesuffix('index.html')
                self.assertEqual(canonical, urljoin(DATA['profile']['portfolioUrl'], site_path))
                alts = {a.get('hreflang'):a.get('href') for a in doc.findall('.//link[@rel="alternate"]')}
                self.assertEqual(set(alts), {'en','ko','x-default'})
                self.assertEqual(alts['x-default'], alts['ko'])
                self.assertEqual(alts[lang], canonical)
                self.assertTrue(any(a.get('href') == '#'+doc.find('.//main').get('id') for a in doc.iter('a')))

    def test_internal_links_assets_and_bookmarks_resolve(self):
        host = urlsplit(DATA['profile']['portfolioUrl']).hostname
        for lang in LANGUAGES:
            for tab in PAGES:
                doc = page(lang,tab)
                base = doc.find('.//link[@rel="canonical"]').get('href')
                for el in doc.iter():
                    raw = el.get('href') if el.tag in ('a','link') else el.get('src')
                    if not raw:
                        continue
                    link = urlsplit(urljoin(base, raw))
                    if link.hostname != host or link.scheme not in ('https','http'):
                        continue
                    path = ROOT / unquote(link.path).lstrip('/')
                    if path.is_dir():
                        path /= 'index.html'
                    with self.subTest(page=base, target=raw):
                        self.assertTrue(path.is_file(), raw)
                        if link.fragment and path.suffix == '.html':
                            self.assertIn('id="' + unquote(link.fragment) + '"', path.read_text())

    def test_each_publication_has_working_citation_and_bibtex_targets(self):
        for lang in LANGUAGES:
            works = page(lang,'portfolio')
            self.assertEqual(len(works.findall('.//*[@data-paper]')), 3)
            for paper in DATA['papers']:
                article = works.find(f'.//*[@id="paper-{paper["id"]}"]')
                self.assertIsNotNone(article)
                targets = {b.get('data-copy') for b in article.iter('button')}
                self.assertEqual(targets, {'ref-'+paper['id'], 'bib-'+paper['id']})
                for prefix, expected in [('ref',reference(paper,lang)), ('bib',bibtex(paper))]:
                    template = article.find(f'.//template[@id="{prefix}-{paper["id"]}"]')
                    self.assertIsNotNone(template)
                    self.assertEqual(''.join(template.itertext()).strip(), expected.strip())
                self.assertIsNotNone(article.find('.//*[@role="status"]'))
                self.assertIn(paper['url'], [a.get('href') for a in article.iter('a')])

    def test_career_categories_have_navigable_headings_and_honest_empty_states(self):
        for lang in LANGUAGES:
            doc = page(lang,'career')
            for key in SECTIONS:
                node = section(lang,key)
                self.assertTrue(text(node.find('h2')))
                self.assertTrue(any(link.get('href') == '#'+key for link in doc.iter('a')))
            for key in ('awards','writing'):
                self.assertIsNone(section(lang,key).find('.//article'))

    def test_public_html_excludes_private_sources_course_materials_and_pending_claims(self):
        for lang in LANGUAGES:
            for tab in PAGES:
                html = page_path(lang,tab).read_text()
                for private in ('mail.google.com','drive.google.com','docs.google.com','chatgpt.com/library',
                                '/learn/prompt-engineering','robotics-story-snow','프롬프트에서 에이전트 시스템으로',
                                '가중치별 학습률 조절의 설계와','한국IT서비스학회'):
                    self.assertNotIn(private, html, (lang,tab,private))

    def test_old_course_url_redirects_without_serving_the_lesson(self):
        legacy = (ROOT/'learn/prompt-engineering/index.html').read_text()
        parser = DocumentParser()
        parser.feed(legacy)
        parser.close()
        robots = parser.root.find('.//meta[@name="robots"]')
        refresh = parser.root.find('.//meta[@http-equiv="refresh"]')
        self.assertIn('noindex', robots.get('content').lower())
        self.assertEqual(refresh.get('content').lower().replace(' ', ''), '0;url=/portfolio/')
        self.assertTrue(any(a.get('href') == '/portfolio/' for a in parser.root.iter('a')))
        self.assertNotIn('프롬프트에서 에이전트 시스템으로', legacy)

    def test_responsive_and_keyboard_styles_do_not_depend_on_animation(self):
        css = (ROOT/'assets/site.css').read_text()
        self.assertIn(':focus-visible',css)
        self.assertRegex(css,r'@media\s*\(max-width\s*:\s*\d+px\)')
        self.assertIn('@media print',css)
        self.assertNotRegex(css,r'(?:^|[;{])\s*(?:animation|backdrop-filter)\s*:')

    def test_quantization_figure_links_to_the_paper_and_has_an_alternative(self):
        for lang in LANGUAGES:
            figure = page(lang).find('.//figure')
            self.assertIsNotNone(figure)
            image = figure.find('.//img')
            self.assertGreater(len(image.get('alt','')), 10)
            self.assertTrue(int(image.get('width')) > 0 and int(image.get('height')) > 0)
            self.assertTrue(any(a.get('href','').endswith('#paper-2025') for a in figure.iter('a')))
