"""The bilingual theme tree prioritizes real work and preserves the full index."""
import json
import unittest
from urllib.parse import urlsplit

from rendered_site import ROOT, page, text


class PortfolioThemesTests(unittest.TestCase):
    def test_branches_precede_the_index_and_link_to_existing_public_details(self):
        themes = json.loads((ROOT / 'data/portfolio-themes.json').read_text())
        for lang in ('ko', 'en'):
            doc = page(lang, 'portfolio')
            trees = doc.findall('.//ol[@class="theme-branches"]')
            self.assertEqual(len(trees), 1)
            cards = trees[0].findall('li')
            self.assertEqual(len(cards), len(themes))
            self.assertLess(list(doc.iter()).index(trees[0]),
                            list(doc.iter()).index(doc.find('.//ul[@class="work-entries"]')))
            index_urls = {node.get('href') for node in doc.find('.//ul[@class="work-entries"]').iter('a')}
            for card, theme in zip(cards, themes):
                self.assertEqual(text(card.find('h3')), theme['title'][lang])
                lead = card.find('.//a[@class="theme-lead"]')
                related = card.findall('.//ul[@class="theme-children"]/li/a')
                self.assertEqual(len(related), len(theme['related']))
                for link, key in zip([lead, *related], [theme['representative'], *theme['related']]):
                    url = link.get('href')
                    self.assertIn(url, index_urls)
                    path = urlsplit(url)
                    self.assertTrue(path.fragment.endswith('-' + key))
                    target = page(lang, 'career') if path.path else doc
                    self.assertIsNotNone(target.find(f'.//*[@id="{path.fragment}"]'), url)
