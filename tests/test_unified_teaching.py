"""Single teaching history preserves source detail and verified relationship roles."""
import copy,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from content import DATA, teaching_history_records, experience_records, school_program_groups, teaching_columns, detail_program_titles, validate
from rendered_site import page, section, text

class UnifiedTeachingTests(unittest.TestCase):
    def test_history_keeps_one_record_per_course(self):
        for lang in ('ko', 'en'):
            career = page(lang, 'career')
            articles = [el.get('data-record') for el in career.iter() if 'data-record' in el.attrib]
            self.assertEqual(len(articles), len(set(articles)))
            for course in DATA['teaching']:
                with self.subTest(course=course['id'], language=lang):
                    self.assertEqual(articles.count(course['id']), 1)

    def test_school_tracks_remain_with_their_school(self):
        rows = [detail for course in DATA['teaching'] for detail in course['details'] if detail.get('tracks')]
        self.assertEqual({row['id'] for row in rows}, {'sudo', 'munhak', 'jamsil-girls', 'haseong'})
        self.assertEqual(sum(len(row['tracks']) for row in rows), 8)
        for lang in ('ko', 'en'):
            for row in rows:
                public = section(lang, 'teaching').findall(f'.//*[@data-detail="{row["id"]}"]')
                self.assertEqual(len(public), 1)
                for track in row['tracks']:
                    self.assertTrue(track['curriculum'][lang])
                for title in detail_program_titles(row):
                    self.assertIn(title[lang], text(public[0]))

    def test_school_role_and_title_associations_are_not_lost(self):
        rows={r['id']:r for r in teaching_history_records()}
        groups=school_program_groups(rows['saessak-elice-2023'],'ko')
        hwagok=next(g for g in groups if '화곡고등학교' in g['schools'])
        self.assertEqual(hwagok['role'],'보조강사')
        self.assertEqual(len(next(g for g in groups if '수도전기공업고등학교' in g['schools'])['titles']),3)
        groups=school_program_groups(rows['donghaeng-elice-2023'],'ko')
        handong=next(g for g in groups if '한동글로벌학교' in g['schools'])
        self.assertEqual(handong['titles'],[])
        self.assertEqual(len([d for d in rows['donghaeng-elice-2023']['details'] if d['id'].startswith('handong')]),2)

    def test_program_roles_do_not_transfer_between_operators(self):
        rows={r['id']:r for r in teaching_history_records()}
        edu=teaching_columns(rows['donghaeng-educore-2025'],'ko')
        elice=teaching_columns(rows['donghaeng-elice-2023'],'ko')
        self.assertEqual(edu['organizationLines'],['AI 분과 주관: 동아사이언스','운영: 에듀코어센터'])
        self.assertEqual(elice['organizationLines'],['운영: 엘리스그룹'])
        self.assertEqual(teaching_columns(rows['saessak-elice-2023'],'ko')['organizationLines'],['사업 주관·운영: 엘리스그룹'])
        self.assertNotIn('동아사이언스',str(elice))
        self.assertNotIn('주최',str(rows['donghaeng-elice-2023']))
        self.assertNotIn('Host',str(rows['donghaeng-elice-2023']))

    def test_mincoding_assignments_keep_their_distinct_roles(self):
        mincoding = next(row for row in experience_records() if row['id'] == 'mincoding')
        self.assertEqual([r['role'] for r in mincoding['assignments']], ['instructor', 'assistant'])
        self.assertEqual(mincoding['start'], '2025')
        self.assertTrue(all(r['organization'] == 'mincoding' for r in mincoding['assignments']))

    def test_support_does_not_become_individual_event_organizer(self):
        rows={r['id']:r for r in DATA['teaching']}
        self.assertEqual([r['role'] for r in rows['hanalife-2026-10']['relationships']],['ministry','program_management'])
        self.assertEqual(teaching_columns(rows['hanalife-2026-10'],'ko')['organizationLines'],['운영: 엘리스그룹'])
        roles={r['role'] for r in rows['codyssey-modulabs-2026-06']['relationships']}
        self.assertEqual(roles,{'program_institution','support','affiliation'})
        self.assertEqual([r['role'] for r in rows['goyang-educore-2026-08']['relationships']],['program_body'])
        self.assertEqual(rows['paju-ablearn-2026-05']['activeMonths'],['2026-05','2026-07'])

    def test_invalid_relationship_roles_or_translations_are_rejected(self):
        rows=copy.deepcopy(DATA['teaching']);rows[0]['relationships']=[{'role':'host','name':{'ko':'a','en':'b'}}]
        with patch.dict(DATA,teaching=rows),self.assertRaisesRegex(ValueError,'Unknown relationship role'):
            validate()
        rows[0]['relationships']=[{'role':'lead','name':{'ko':'a'}}]
        with patch.dict(DATA,teaching=rows),self.assertRaisesRegex(ValueError,'Missing relationship translation'):
            validate()

    def test_reader_friendly_summary_preserves_relationships_in_detail(self):
        from content import teaching_display_columns,teaching_detail_context
        rows={r['id']:r for r in teaching_history_records()}
        for lang in ['ko','en']:
            for item in rows.values():
                value=teaching_display_columns(item,lang)
                self.assertEqual(value['subject'],teaching_columns(item,lang)['subject'])
                self.assertEqual(value['audience'],teaching_columns(item,lang)['audience'])
                for line in value['organizationLines']:
                    self.assertNotIn(':',line)
        edu=rows['donghaeng-educore-2025']
        self.assertEqual(teaching_display_columns(edu,'ko')['organizationLines'],['에듀코어센터'])
        self.assertIn('AI 분과 주관: 동아사이언스',teaching_detail_context(edu,'ko'))
        self.assertIn('운영: 에듀코어센터',teaching_detail_context(edu,'ko'))
        for lang in ['ko', 'en']:
            item = section(lang, 'teaching').find('.//*[@data-record="donghaeng-educore-2025"]')
            self.assertIn(edu['operator'][lang], text(item))
