"""Regression checks for shared edits, derived summaries, and build guards."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from content import DATA, LOCALES, localized, reference, teaching_values, validate, write_if_changed
import site_sections


class SharedContentTests(unittest.TestCase):
    def test_education_is_separate_from_qualifications(self):
        education = site_sections.education()
        qualification = site_sections.qualifications()
        self.assertIn('공학석사', education)
        self.assertIn('국민대학교', education)
        self.assertNotIn('NCS', education)
        self.assertIn('NCS', qualification)
        self.assertNotIn('공학석사', qualification)

    def test_one_course_edit_reaches_both_web_views_and_cv_values(self):
        changed = {'ko': '변경된 공통 과정', 'en': 'Updated shared course'}
        with patch.dict(DATA['courses']['donghaeng'], title=changed):
            self.assertEqual(site_sections.teaching_summary().count('Updated shared course'), 2)
            self.assertEqual(site_sections.teaching_detail().count('Updated shared course'), 2)
            records = [item for item in DATA['teaching'] if item['course'] == 'donghaeng']
            self.assertEqual(len(records), 2)
            for item in records:
                self.assertEqual(teaching_values(item, 'en')['course'], changed['en'])

    def test_qualification_count_and_latest_preview_are_derived(self):
        item = {'id': 'new', 'year': 2027, 'title': {'ko': '새 자격', 'en': 'New qualification'},
                'field': {'ko': '분야', 'en': 'Field'}}
        with patch.dict(DATA, qualifications=DATA['qualifications'] + [item]):
            output = site_sections.qualifications()
            self.assertIn('<small>2</small>', output)
            summary = output.split('<p class="fold-preview">')[1].split('</p>')[0]
            self.assertIn('New qualification', summary)
            self.assertIn('2027', summary)

    def test_unknown_references_stop_the_build(self):
        changed = copy.deepcopy(DATA['teaching'])
        changed[0]['course'] = 'missing-course'
        with patch.dict(DATA, teaching=changed), self.assertRaisesRegex(ValueError, 'Unknown course'):
            validate()

    def test_missing_translation_stops_the_build(self):
        changed = dict(LOCALES['en'])
        changed.pop('ui.download_cv')
        with patch.dict(LOCALES, en=changed), self.assertRaisesRegex(ValueError, 'Locale keys differ'):
            validate()

    def test_english_fallback_and_single_author_reference(self):
        self.assertEqual(localized({'en': 'English only'}, 'ko'), 'English only')
        paper = dict(DATA['papers'][0], authors=['choi'])
        self.assertTrue(reference(paper, 'en').startswith('S. H. Choi,'))

    def test_unchanged_output_is_not_rewritten(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'page.html'
            self.assertTrue(write_if_changed(path, 'same content'))
            stamp = path.stat().st_mtime_ns
            self.assertFalse(write_if_changed(path, 'same content'))
            self.assertEqual(path.stat().st_mtime_ns, stamp)


if __name__ == '__main__':
    unittest.main()
