"""Active coaching and contracts keep their own source and completion state."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from content import DATA, LANGUAGES, current_role_records, period, validate
from rendered_site import page, section, text


class CurrentRoleTests(unittest.TestCase):
    def test_only_current_coaching_and_teaching_appear(self):
        expected = ['aba3-elice-2026-11', 'algorithms-coderland-2023-03']
        self.assertEqual([row['teaching'] for row in current_role_records()], expected)
        for lang in LANGUAGES:
            home = text(page(lang).find('.//main'))
            self.assertIn('코더랜드' if lang == 'ko' else 'Coderland', home)
            self.assertIn('비즈니스 에이전트' if lang == 'ko' else 'Business Agent', home)
            self.assertNotIn('10월 종료 예정' if lang == 'ko' else 'Planned end: October', home)
            self.assertNotIn('2023.01–현재' if lang == 'ko' else '2023.01–Present', home)

    def test_current_titles_are_translated(self):
        for row in current_role_records():
            for lang in LANGUAGES:
                self.assertTrue(row['title'][lang].strip())

    def test_linked_start_and_closure_follow_course(self):
        rows = copy.deepcopy(DATA['teaching'])
        row = next(r for r in rows if r['id'] == 'aba3-elice-2026-11')
        row['start'] = '2026-10'
        with patch.dict(DATA, teaching=rows):
            self.assertEqual(current_role_records()[0]['start'], '2026-10')
            row['end'] = '2026-12'
            row.pop('plannedEnd')
            self.assertEqual([r['teaching'] for r in current_role_records()], ['algorithms-coderland-2023-03'])

    def test_elice_coaching_has_a_project_period_and_a_planned_end(self):
        row = next(r for r in DATA['teaching'] if r['id'] == 'aba3-elice-2026-11')
        self.assertEqual((row['start'], row['end'], row['plannedEnd']), ('2026-11', None, '2026-12'))
        self.assertIn('2026.11.11', period(row, 'ko'))
        self.assertIn('12.18', period(row, 'ko'))
        self.assertIn('예정', period(row, 'ko'))
        self.assertIn('scheduled', period(row, 'en').lower())
        self.assertNotIn('196', text(section('ko', 'teaching')))

    def test_retired_activities_have_completed_source_dates(self):
        sources = {r['id']: r for r in DATA['teaching']}
        for key in ('goyang-educore-2026-08', 'codyssey-modulabs-2026-06'):
            row = sources[key]
            self.assertEqual(row['end'][:7], '2026-10')
            self.assertFalse(row.get('plannedEnd'))
            for detail in row['details']:
                self.assertIsNotNone(detail['end'])
                self.assertFalse(detail.get('plannedEnd'))
        self.assertIn('2026.10.31', period(sources['codyssey-modulabs-2026-06'], 'ko'))
        self.assertIn('27', sources['goyang-educore-2026-08']['summary']['ko'])

    def test_coderland_appointment_is_distinct_from_online_teaching_start(self):
        row = next(r for r in DATA['teaching'] if r['id'] == 'algorithms-coderland-2023-03')
        self.assertEqual(row['start'], '2023-03')
        self.assertIsNone(row['end'])
        self.assertIn('2023.01.19', row['details'][0]['note']['ko'])

    def test_active_roles_still_have_full_career_entries(self):
        for row in current_role_records():
            for lang in LANGUAGES:
                found = section(lang, 'teaching').findall(f'.//*[@data-record="{row["teaching"]}"]')
                self.assertEqual(len(found), 1)

    def test_invalid_or_closed_planned_period_is_rejected(self):
        for planned, end, message in [('2026-13', None, 'Invalid planned end'),
                                      ('2026-10', None, 'Reversed planned period'),
                                      ('2026-12', '2026-12', 'Planned end requires ongoing status')]:
            rows = copy.deepcopy(DATA['teaching'])
            coach = next(r for r in rows if r['id'] == 'aba3-elice-2026-11')
            coach['plannedEnd'], coach['end'] = planned, end
            with patch.dict(DATA, teaching=rows), self.assertRaisesRegex(ValueError, message):
                validate()

    def test_unknown_duplicated_or_untranslated_current_roles_are_rejected(self):
        updates = [
            ('teaching', 'missing', 'Unknown current role teaching reference'),
            ('start', '2026-11', 'Duplicated current role facts'),
            ('id', DATA['currentRoles'][1]['id'], 'Duplicate current role ID'),
            ('title', {'ko':'코치'}, 'Missing current role translation'),
        ]
        for key, value, message in updates:
            roles = copy.deepcopy(DATA['currentRoles'])
            roles[0][key] = value
            with self.subTest(key=key), patch.dict(DATA, currentRoles=roles), self.assertRaisesRegex(ValueError, message):
                validate()

    def test_all_closed_or_empty_selections_produce_no_current_activities(self):
        with patch.dict(DATA, currentRoles=[]):
            self.assertEqual(current_role_records(), [])
