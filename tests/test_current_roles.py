"""HOME current roles stay distinct from course and employment histories."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from content import DATA, LANGUAGES, current_role_records, validate
import site_sections


class CurrentRoleTests(unittest.TestCase):
    def test_exact_curated_roles_and_months(self):
        rows = current_role_records()
        self.assertEqual([row['id'] for row in rows], ['educore', 'modulabs', 'coderland', 'elice'])
        self.assertEqual([row['start'] for row in rows], ['2026-08', '2026-06', '2023-03', '2023-01'])
        self.assertTrue(all(row['end'] is None for row in rows))
        self.assertEqual(rows[-1]['title'], {'ko': '프리랜서 강사', 'en': 'Freelance instructor'})
        for row in rows:
            self.assertTrue(all(lang in row['title'] for lang in LANGUAGES))
        self.assertEqual(len(DATA['teaching']), 14)

    def test_linked_dates_reuse_source_and_closed_role_disappears(self):
        records = copy.deepcopy(DATA['teaching'])
        row = next(row for row in records if row['id'] == 'goyang-educore-2026-08')
        row['start'] = '2026-07'
        with patch.dict(DATA, teaching=records):
            self.assertEqual(current_role_records()[0]['start'], '2026-07')
        row['end'] = '2026-10'
        with patch.dict(DATA, teaching=records):
            self.assertNotIn('educore', [item['id'] for item in current_role_records()])
        standalone = copy.deepcopy(DATA['currentRoles'])
        standalone[-1]['end'] = '2026-10'
        with patch.dict(DATA, currentRoles=standalone):
            self.assertNotIn('elice', [item['id'] for item in current_role_records()])

    def test_home_section_is_separate_bilingual_and_not_collapsed(self):
        output = site_sections.current_roles()
        self.assertEqual(output.count('data-current-role='), 4)
        self.assertIn('현직', output)
        self.assertIn('Current roles', output)
        self.assertNotIn('fold-section', output)
        self.assertNotIn('data-teaching=', output)
        self.assertNotIn('data-career-detail=', output)
        page = (Path(__file__).resolve().parents[1] / 'index.html').read_text()
        self.assertLess(page.index('class="current-roles"'), page.index('id="snow-cv-papers"'))
        self.assertLess(page.index('class="current-roles"'), page.index('id="snow-cv-career"'))
        self.assertEqual(page.count('data-current-role='), 4)

    def test_missing_or_duplicate_role_references_stop_build(self):
        records = copy.deepcopy(DATA['currentRoles'])
        records[0]['teaching'] = 'missing'
        with patch.dict(DATA, currentRoles=records), self.assertRaisesRegex(ValueError, 'Unknown current role teaching reference'):
            validate()
        records = copy.deepcopy(DATA['currentRoles'])
        records[0]['start'] = '2026-08'
        with patch.dict(DATA, currentRoles=records), self.assertRaisesRegex(ValueError, 'Duplicated current role facts'):
            validate()
        records = copy.deepcopy(DATA['currentRoles'])
        records[1]['id'] = records[0]['id']
        with patch.dict(DATA, currentRoles=records), self.assertRaisesRegex(ValueError, 'Duplicate current role ID'):
            validate()

    def test_invalid_standalone_date_or_translation_stops_build(self):
        records = copy.deepcopy(DATA['currentRoles'])
        records[-1]['start'] = '2023-13'
        with patch.dict(DATA, currentRoles=records), self.assertRaisesRegex(ValueError, 'Invalid current role start'):
            validate()
        records = copy.deepcopy(DATA['currentRoles'])
        del records[-1]['title']['en']
        with patch.dict(DATA, currentRoles=records), self.assertRaisesRegex(ValueError, 'Missing current role translation'):
            validate()

    def test_empty_current_roles_omit_section(self):
        with patch.dict(DATA, currentRoles=[]):
            self.assertEqual(site_sections.current_roles(), '')


if __name__ == '__main__':
    unittest.main()
