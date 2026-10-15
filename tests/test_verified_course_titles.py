"""Verified course names remain associated with their own schools and tracks."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from content import DATA,teaching_records,detail_program_titles,school_program_groups,school_teaching_summaries,school_names
import site_sections

class VerifiedCourseTitlesTests(unittest.TestCase):
    def records(self,course):
        return [r for group in ['ai-data','programming'] for r in teaching_records(group) if r['course']==course]

    def test_schools_and_formal_names_reach_all_three_surfaces(self):
        import build_cv
        from html import escape, unescape
        for row in self.records('donghaeng-data')+self.records('saessak')+self.records('donghaeng'):
            for lang in ['ko','en']:
                expected=[title for group in school_program_groups(row,lang) for title in group['titles']]
                summary=site_sections.teaching_entry(row,True)
                details=site_sections.teaching_entry(row,False)
                with patch.object(build_cv,'p',side_effect=lambda value,*a,**k:value):
                    rendered=str(build_cv.teaching_pdf_rows(row,lang))
                for title in expected:
                    self.assertIn(escape(title),details)
                    self.assertIn(escape(title),summary)
                    self.assertIn(escape(title),rendered)
                names=school_names(row,lang)
                expected_schools=list(dict.fromkeys(d.get('schoolTitle',d['title'])[lang].split(' · ')[0] for d in row['details']))
                self.assertEqual(names,expected_schools)
                for school in names:
                    for output in [summary,rendered]:
                        self.assertIn(school,unescape(output))
                school_block=summary.split('<div class="teaching-programs">')[1].split('</div>')[0]
                self.assertNotIn('cv-sub',school_block)
                for role in DATA['roles'].values():
                    self.assertNotIn('>'+role[lang]+'<',school_block)
                self.assertNotIn('2024.',school_block)

    def test_school_only_names_do_not_duplicate_classes_or_erase_details(self):
        row=next(r for r in self.records('donghaeng-data') if r['id'].endswith('programming'))
        self.assertEqual(school_names(row,'ko'),['하성고등학교','한동글로벌학교'])
        self.assertEqual(len([d for d in row['details'] if d['id'].startswith('handong')]),2)
        self.assertIn('한동글로벌학교 · A반',site_sections.teaching_details(row))
        self.assertIn('한동글로벌학교 · B반',site_sections.teaching_details(row))
        for item in self.records('donghaeng-data')+self.records('saessak')+self.records('donghaeng'):
            for lang in ['ko','en']:
                self.assertTrue(school_teaching_summaries(item,lang))

    def test_sudo_tracks_merge_without_duplicate_course_names(self):
        row=next(r for r in self.records('saessak') if r['id'].endswith('ai-data'))
        sudo=next(d for d in row['details'] if d['sourceDetail']=='sudo')
        titles=detail_program_titles(sudo)
        self.assertEqual(len(titles),3)
        self.assertEqual(len({t['ko'] for t in titles}),3)
        self.assertEqual(len(next(t for t in sudo['courseTracks'] if t['id']=='data')['programTitles']),2)
        self.assertEqual(len(next(t for t in sudo['courseTracks'] if t['id']=='ai')['programTitles']),1)

    def test_formal_titles_are_not_borrowed_for_handong(self):
        row=next(r for r in self.records('donghaeng-data') if r['id'].endswith('programming'))
        for detail in row['details']:
            if detail['id'].startswith('handong'):
                self.assertEqual(detail_program_titles(detail),[])
        groups=school_program_groups(row,'ko')
        untitled=next(g for g in groups if not g['titles'])
        self.assertEqual(untitled['schools'],['한동글로벌학교'])
        self.assertNotIn('한동글로벌학교',next(g for g in groups if g['titles'])['schools'])

    def test_scope_and_unresolved_dates_are_preserved(self):
        details={d['id']:d for row in DATA['teaching'] for d in row.get('details',[])}
        self.assertEqual(details['munhak']['start'],'2024-09')
        for key in ['handong-a','handong-b']:
            self.assertEqual((details[key]['start'],details[key]['end']),('2024-10','2024-10'))
        title=details['cheongwon-girls']['programTitles'][0]
        self.assertEqual((title['verifiedTeachingStart'],title['verifiedTeachingEnd']),('2024-11','2024-12'))
        self.assertEqual(details['cheongwon-girls']['start'],'2024-09')
        row=next(r for r in self.records('saessak') if r['id'].endswith('programming'))
        self.assertIn('2024.11–2024.12',site_sections.teaching_details(row))
        groups=school_program_groups(row,'ko')
        self.assertTrue(all('2024.' not in title for g in groups for title in g['titles']))

    def test_sangincheon_is_foundations_not_borrowed_ai_prediction(self):
        row=next(r for r in DATA['teaching'] if r['course']=='donghaeng-data')
        detail=next(d for d in row['details'] if d['id']=='sangincheon')
        self.assertEqual((detail['start'],detail['end']),('2024-11','2024-11'))
        self.assertEqual(detail['role'],'lead')
        self.assertEqual(detail['group'],'data')
        self.assertIn('Orange3 기초',detail['curriculum']['ko'])
        self.assertNotIn('회귀',detail['curriculum']['ko'])
        self.assertNotIn('분류',detail['curriculum']['ko'])
        self.assertNotIn('AI 맞춤형 운동 처방',str(detail))

    def test_paju_dates_show_discontinuous_months_and_verified_course(self):
        from content import period,teaching_columns
        row=next(r for r in DATA['teaching'] if r['course']=='paju')
        self.assertEqual(row['activeMonths'],['2026-05','2026-07'])
        self.assertEqual(period(row,'ko'),'2026.05 · 2026.07')
        self.assertIn('공공 홍보 및 행정 보고서',teaching_columns(row,'ko')['subject'])
        self.assertEqual(row['role'],'assistant')

    def test_assignment_only_schools_are_not_added_as_completed_records(self):
        titles=[d['title']['ko'] for r in DATA['teaching'] for d in r['details']]
        self.assertNotIn('서울정덕초등학교',titles)
        self.assertNotIn('서울대현초등학교',titles)

    def test_gosaek_program_and_subject_are_distinct(self):
        from content import teaching_columns
        row=next(r for r in DATA['teaching'] if r['course']=='gosaek')
        values=teaching_columns(row,'ko')
        self.assertEqual(values['provider'],'주문형강좌')
        self.assertEqual(values['subject'],'정보과학')
        self.assertEqual(values['organization'],'고색고등학교')
        self.assertEqual((row['start'],row['end']),('2023-08','2023-12'))


    def test_verified_operator_is_separate_from_audience_and_legal_entity(self):
        from content import teaching_columns
        rows={r['id']:r for r in DATA['teaching']}
        for key in ['donghaeng-elice-2023','saessak-elice-2023','ai-workshop-elice-2024-12','hanalife-2026-10','lginnotek-elice-2026-07','lgcns-elice-2024-02']:
            self.assertEqual(rows[key]['operator']['ko'],'엘리스그룹')
            self.assertNotIn('contracting_legal_entity',rows[key])
        self.assertEqual(rows['donghaeng-educore-2025']['operator']['ko'],'에듀코어센터')
        hana=teaching_columns(rows['hanalife-2026-10'],'ko')
        self.assertNotIn('하나생명',hana['provider']+hana['organizationLabel'])
        self.assertIn('하나생명',hana['audience'])
        gosaek=teaching_columns(rows['gosaek-gosaek-2023'],'ko')
        self.assertEqual(gosaek['audience'],'고색고등학교')
        self.assertEqual(gosaek['organizationLabel'],'')
        for lang in ['ko','en']:
            html=site_sections.teaching_entry(rows['hanalife-2026-10'],True)
            middle=html.split('class="teaching-provider"')[1].split('</td>')[0]
            right=html.split('class="teaching-course"')[1].split('</td>')[0]
            self.assertNotIn(rows['hanalife-2026-10']['audience'][lang],middle)
            self.assertIn(rows['hanalife-2026-10']['audience'][lang],right)

    def test_workshop_uses_verified_round_and_event_without_inventing_date(self):
        row=next(r for r in DATA['teaching'] if r['course']=='ai-workshop')
        course=DATA['courses']['ai-workshop']
        self.assertEqual(course['program']['ko'],'디지털새싹 2024년도 3기')
        self.assertEqual(course['eventTitle']['ko'],'겨울방학 강사대상 사전 원격교육(손쉽게 공부하는 인공지능)')
        self.assertEqual(row['role'],'instructor')
        self.assertFalse(row['showRole'])
        self.assertEqual((row['start'],row['end']),('2024-12','2025-01'))
        self.assertNotIn('hours',row)


class DirectSchoolCourseTitleTests(unittest.TestCase):
    def test_jamsil_direct_course_is_distinct_from_munhak_project(self):
        rows = {detail['id']: detail for row in DATA['teaching'] for detail in row['details']}
        self.assertEqual(rows['jamsil-girls']['programTitles'][0]['ko'],
                         '디지털 문제 해결 프로젝트: 건강한 삶(심화)')
        self.assertEqual(rows['munhak']['programTitles'][0]['ko'],
                         'AI 맞춤형 운동 처방 프로그램')
        self.assertNotIn('AI 맞춤형 운동 처방 프로그램', str(rows['jamsil-girls']))
        self.assertIn('Orange3', rows['jamsil-girls']['curriculum']['ko'])
        self.assertEqual(rows['jamsil-girls']['start'], '2024-10')
        self.assertEqual(rows['jamsil-girls']['end'], '2024-10')
        for school in ['handong-a', 'handong-b']:
            self.assertFalse(rows[school].get('programTitles'))
            self.assertIn('Python', rows[school]['curriculum']['ko'])
