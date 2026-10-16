"""Single teaching history preserves source detail and verified relationship roles."""
import copy,re,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from content import DATA, teaching_history_records, current_role_records, experience_records, school_program_groups, teaching_columns, teaching_relationships, detail_program_titles, validate
import site_sections

class UnifiedTeachingTests(unittest.TestCase):
    def test_history_is_one_source_per_program_sorted_by_completion(self):
        expected=['hanalife-2026-10','lginnotek-elice-2026-07','paju-ablearn-2026-05','donghaeng-educore-2025','ai-workshop-elice-2024-12','saessak-elice-2023','donghaeng-elice-2023','lgcns-elice-2024-02','gosaek-gosaek-2023']
        self.assertEqual([r['id'] for r in teaching_history_records()],expected)
        for html in [site_sections.teaching_summary(),site_sections.teaching_detail()]:
            self.assertEqual(re.findall(r'data-teaching="([^"]+)"',html),expected)
            self.assertEqual(html.count('<table '),1)
            for heading in ['인공지능·데이터 교육','프로그래밍·자료구조·알고리즘 교육','AI &amp; Data Education']:
                self.assertNotIn(heading,html)
        self.assertNotIn('snow-history-ai-data',site_sections.teaching_detail())
        self.assertNotIn('snow-history-programming',site_sections.teaching_detail())

    def test_all_original_details_and_track_curricula_are_displayed_once(self):
        from html import escape
        html=site_sections.current_roles()+site_sections.teaching_detail()
        ids=[d['id'] for item in DATA['teaching'] for d in item['details']]
        self.assertEqual(len(ids),31)
        self.assertCountEqual(re.findall(r'data-career-detail="([^"]+)"',html),ids)
        tracks=[t for item in DATA['teaching'] for d in item['details'] for t in d.get('tracks',[])]
        self.assertEqual(len(tracks),8)
        for track in tracks:
            for lang in ['ko','en']:
                self.assertIn(escape(track['curriculum'][lang]),html)

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
        self.assertNotIn('주최',str(DATA))
        self.assertNotIn('Host',str(DATA))

    def test_current_dates_and_mincoding_scope_stay_distinct(self):
        roles={r['teaching']:r for r in current_role_records()}
        coder=roles['algorithms-coderland-2023-03']
        self.assertEqual(coder['start'],'2023-03')
        self.assertIn('프리랜서',coder['title']['ko'])
        self.assertNotIn('2023-01-19',str(DATA))
        for key in ['goyang-educore-2026-08','codyssey-modulabs-2026-06']:
            self.assertIsNone(roles[key]['end']);self.assertEqual(roles[key]['plannedEnd'],'2026-10')
        mincoding=next(r for r in experience_records() if r['id']=='mincoding')
        self.assertEqual([a['role'] for a in mincoding['assignments']],['instructor','assistant'])
        self.assertTrue(all('operator' not in a for a in mincoding['assignments']))
        self.assertEqual(mincoding['start'],'2025')

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
        for lang in ['ko','en']:
            for item in rows.values():
                detail=site_sections.teaching_details(item)
                for line in teaching_detail_context(item,lang):
                    self.assertIn(line,detail)

    def test_pdf_main_history_omits_administrative_labels(self):
        from pypdf import PdfReader
        root=Path(__file__).resolve().parents[1]
        for lang in ['KO','EN']:
            pages=PdfReader(root/'assets'/f'Choi-Soon-Ho-CV-{lang}.pdf').pages
            content=''.join(page.extract_text() for page in pages)
            for label in ['사업 주관','AI 분과 주관','운영:','사업기관:','Operator:','Program institution:','AI division lead:']:
                self.assertNotIn(label,content)
            if lang == 'EN':
                self.assertIn('Program / Institution', content)
                self.assertIn('Audience / Teaching', content)
            else:
                self.assertIn('교육 경력', content)
                self.assertIn('하나생명 임직원', content)

