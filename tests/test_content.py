"""Regression checks for shared edits, derived summaries, and build guards."""
import copy
import re
from html import escape
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from content import DATA, LOCALES, localized, reference, teaching_values, teaching_records, validate, write_if_changed
import site_sections


class SharedContentTests(unittest.TestCase):
    def test_generated_page_versions_the_current_stylesheet(self):
        import hashlib
        root=Path(__file__).resolve().parents[1]
        digest=hashlib.sha256((root/'assets/site.css').read_bytes()).hexdigest()[:12]
        self.assertIn(f'assets/site.css?v={digest}', (root/'index.html').read_text())

    def test_icon_urls_resolve_beside_stylesheet(self):
        assets = Path(__file__).resolve().parents[1] / 'assets'
        urls = re.findall(r"--icon:url\('([^']+)'\)", site_sections.profile())
        self.assertEqual(len(urls), len(DATA['profile']['links']) + 1)
        for url in urls:
            self.assertTrue((assets / url).is_file(), f'Missing icon: {url}')

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
            self.assertEqual(site_sections.teaching_summary().count('Updated shared course'), 1)
            self.assertEqual(site_sections.teaching_detail().count('Updated shared course'), 2)  # Visible title + translated accessible label.
            records = [item for item in DATA['teaching'] if item['course'] == 'donghaeng']
            self.assertEqual(len(records), 1)
            for item in records:
                self.assertEqual(teaching_values(item, 'en')['course'], changed['en'])

    def test_program_details_are_additive_and_not_in_home_summary(self):
        detail=site_sections.teaching_detail()
        summary=site_sections.teaching_summary()
        self.assertNotIn('학교·업체별 상세 이력', detail)
        self.assertIn('class="career-toggle cursor-interaction"', detail)
        self.assertIn('data-career-detail="jeohyeon"', detail)
        self.assertNotIn('data-career-detail=', summary)
        views=[item for group in ['ai-data','programming','unclassified'] for item in teaching_records(group)]
        self.assertEqual(detail.count('class="career-details"'), len(views)+sum(bool(row.get('description') or row.get('note')) for row in DATA['otherExperience']))
        expected=sum(len(item.get('details', [])) for item in views)
        self.assertEqual(detail.count('data-career-detail='), expected)

    def test_merged_themes_preserve_unique_program_and_detail_sources(self):
        from collections import Counter
        self.assertEqual([group['id'] for group in DATA['teachingGroups']], ['ai-data','programming'])
        self.assertEqual(len(teaching_records()),14)
        self.assertEqual(DATA['courses']['algorithms']['group'], 'programming')
        self.assertEqual(DATA['courses']['codyssey']['group'], 'ai')
        self.assertEqual(DATA['courses']['codyssey']['title']['ko'], 'AI Native 과정 · 코디세이')
        self.assertEqual(DATA['courses']['hanalife']['group'], 'ai')
        views=[item for group in ['ai-data','programming','unclassified'] for item in teaching_records(group)]
        self.assertEqual({item.get('sourceId',item['id']) for item in views}, {item['id'] for item in DATA['teaching']})
        expected=Counter({detail['id']:len(detail.get('tracks',[])) or 1 for item in DATA['teaching'] for detail in item['details']})
        actual=Counter()
        for item in views:
            for detail in item['details']:
                actual[detail.get('sourceDetail', detail['id'])] += len(detail.get('courseTracks', [])) or 1
        self.assertEqual(actual, expected)
        detail=site_sections.teaching_detail()
        summary=site_sections.teaching_summary()
        self.assertEqual(detail.count('class="history-group'),4)
        for item in views:
            for output in [summary,detail]:
                self.assertEqual(output.count(f'data-teaching="{item["id"]}"'),1)
        self.assertEqual(len(expected),30)
        self.assertIn('<small>22</small>',summary)
        self.assertEqual(teaching_records('unclassified'),[])

    def test_school_courses_use_verified_categories(self):
        by_group={group:{detail['id'] for item in teaching_records(group) for detail in item['details']} for group in ['ai','data','programming']}
        self.assertTrue({'mirae','munchang','sudo-ai','munhak-ai','jamsil-girls-ai'} <= by_group['ai'])
        self.assertTrue({'hwagok','sudo-data','haseong-data','munhak-data','jamsil-girls-data'} <= by_group['data'])
        self.assertTrue({'cheongwon-girls','ansan-design','seoul-robot','handong-a','handong-b','haseong-python'} <= by_group['programming'])
        self.assertNotIn('hwagok',by_group['programming'])
        self.assertNotIn('mirae',by_group['programming'])
        for group in ['ai','data','programming']:
            for item in teaching_records(group):
                for detail in item['details']:
                    if detail.get('sourceDetail') in ['sudo','haseong','munhak','jamsil-girls']:
                        self.assertIn('periodNote',detail)

    def test_ai_data_display_merges_sources_and_preserves_actual_tracks(self):
        records = teaching_records('ai-data')
        self.assertEqual(len(records), 9)
        source_ids = [item.get('sourceId', item['id']) for item in records]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertEqual(sum(len(item['details']) for item in records), 20)
        for item in records:
            source_details = [detail.get('sourceDetail', detail['id']) for detail in item['details']]
            self.assertEqual(len(source_details), len(set(source_details)))
        merged = {detail['sourceDetail']:detail for item in records for detail in item['details']
                  if detail.get('courseTracks')}
        self.assertEqual(set(merged), {'sudo', 'munhak', 'jamsil-girls'})
        output = site_sections.teaching_detail()
        for detail in merged.values():
            self.assertEqual({track['group'] for track in detail['courseTracks']}, {'ai','data'})
            for track in detail['courseTracks']:
                for lang in ['ko','en']:
                    self.assertIn(escape(track['title'][lang]), output)
                    self.assertIn(escape(track['curriculum'][lang]), output)
        for output in [site_sections.teaching_summary(), site_sections.teaching_detail()]:
            self.assertIn('인공지능·데이터 교육', output)
            self.assertIn('AI &amp; Data Education', output)
            self.assertNotIn('data-teaching="saessak-elice-2023-ai"', output)
            self.assertNotIn('data-teaching="saessak-elice-2023-data"', output)

    def test_display_topic_groups_cannot_overlap(self):
        groups = copy.deepcopy(DATA['teachingGroups'])
        groups[1]['topics'] = ['data','programming']
        with patch.dict(DATA, teachingGroups=groups), self.assertRaisesRegex(ValueError, 'Overlapping teaching display topics'):
            validate()

    def test_invalid_course_tracks_stop_build(self):
        changed=copy.deepcopy(DATA['teaching'])
        item=next(item for item in changed if item['course']=='saessak')
        detail=next(detail for detail in item['details'] if detail['id']=='sudo')
        detail['tracks'][0]['group']='missing'
        with patch.dict(DATA, teaching=changed), self.assertRaisesRegex(ValueError, 'Unknown track group'):
            validate()


    def test_simple_career_buttons_have_unique_accessible_targets(self):
        output=site_sections.teaching_detail()
        buttons=re.findall(r'<button type="button" class="career-toggle cursor-interaction"([^>]+)>(.*?)</button>',output)
        self.assertEqual(len(buttons),sum(len(teaching_records(group)) for group in ['ai-data','programming','unclassified'])+sum(bool(row.get('description') or row.get('note')) for row in DATA['otherExperience']))
        targets=[]
        for attrs,body in buttons:
            self.assertIn('aria-expanded="false"',attrs)
            self.assertIn('aria-label="',attrs)
            target=re.search(r'aria-controls="([^"]+)"',attrs)[1]
            targets.append(target)
            self.assertEqual(output.count(f'id="{target}" hidden'),1)
            self.assertEqual(body,'<span class="career-sign" aria-hidden="true">+</span>')
        self.assertEqual(len(targets),len(set(targets)))
        self.assertNotIn('<summary',output)

    def test_generated_page_versions_the_current_script(self):
        import hashlib
        root=Path(__file__).resolve().parents[1]
        digest=hashlib.sha256((root/'assets/site.js').read_bytes()).hexdigest()[:12]
        self.assertIn(f'assets/site.js?v={digest}',(root/'index.html').read_text())

    def test_goyang_has_three_distinct_courses_with_verified_months(self):
        item=next(item for item in DATA['teaching'] if item['id']=='goyang-educore-2026-08')
        self.assertEqual(len(item['details']), 3)
        self.assertEqual([(detail['start'], detail['end']) for detail in item['details']],
                         [('2026-08', '2026-09'), ('2026-09', '2026-09'), ('2026-10', None)])
        self.assertEqual([detail['id'] for detail in item['details']],
                         ['goyang-web-1', 'goyang-web-2', 'goyang-codex'])
        self.assertEqual([detail['title']['ko'] for detail in item['details']],
                         ['AI 웹 제작 과정 · 1차', 'AI 웹 제작 과정 · 2차', 'Codex 업무 비서 과정'])
        for output in [site_sections.teaching_summary(), site_sections.teaching_detail()]:
            self.assertIn('AI 웹 제작 과정 · Codex 업무 비서 과정', output)
            self.assertIn('AI-assisted web development course · Codex work assistant course', output)
        codex=item['details'][2]
        self.assertIn('진행 중', codex['note']['ko'])
        self.assertIn('scheduled', codex['note']['en'])
        output=site_sections.teaching_details(item)
        self.assertEqual(output.count('data-career-detail='), 3)
        self.assertIn('2026.08–2026.09', output)
        self.assertIn('2026.10 (10월 종료 예정)', output)
        self.assertNotIn('goyang-citizens', output)

    def test_elice_and_educore_curricula_are_separate(self):
        elice=next(item for item in DATA['teaching'] if item['id']=='donghaeng-elice-2023')
        educore=next(item for item in DATA['teaching'] if item['id']=='donghaeng-educore-2025')
        self.assertNotEqual(elice['course'], educore['course'])
        self.assertEqual(elice['start'], '2024-09')
        self.assertIn('학교별', teaching_values(elice, 'ko')['course'])
        self.assertIn('AI 프로젝트 교육', teaching_values(educore, 'ko')['course'])
        self.assertIn('로그인', educore['details'][0]['curriculum']['ko'])
        for item in educore['details'][1:]:
            self.assertNotIn('로그인', item['curriculum']['ko'])

    def test_educore_school_programs_reuse_five_existing_details(self):
        item = next(row for row in DATA['teaching'] if row['id']=='donghaeng-educore-2025')
        self.assertEqual(len(item['details']), 5)
        self.assertEqual(sum(len(row.get('details', [])) for row in DATA['teaching']), 30)
        expected = {'jeohyeon': ('2025-04', '2025-07'), 'guryong': ('2025-04', '2025-07'),
                    'seowon': ('2025-05', '2025-07'), 'seoul-digitech': ('2025-04', '2025-06'),
                    'yeongjong': ('2025-05', '2025-06')}
        self.assertEqual({row['id']:(row['start'],row['end']) for row in item['details']}, expected)
        self.assertEqual(len({row['programTitle']['ko'] for row in item['details']}), 3)
        output = site_sections.teaching_details(item)
        for row in item['details']:
            self.assertIn(row['programTitle']['ko'], output)
        summary = next(row for row in teaching_records('ai') if row['id']==item['id'])
        self.assertTrue(all(row['title']['ko'] in summary['schoolSummary']['ko'] for row in item['details']))
        self.assertIn('교통신호', output)
        self.assertIn('산불 예측', output)
        self.assertIn('책임 있는 소비', output)

    def test_non_program_experience_is_separate(self):
        output=site_sections.other_experience()+site_sections.other_experience(group='activities')
        self.assertEqual(output.count('data-other-experience='), 8)
        self.assertIn('프론트엔드 개발자', output)
        self.assertNotIn('data-teaching=', output)

    def test_ted_and_game_planning_are_professional_experience(self):
        development = site_sections.other_experience()
        activities = site_sections.other_experience(group='activities')
        self.assertEqual(development.count('data-other-experience='), 4)
        self.assertIn('data-other-experience="ted"', development)
        self.assertIn('data-other-experience="manlev"', development)
        self.assertIn('Professional Experience', development)
        self.assertIn('게임기획자', development)
        self.assertIn('프론트엔드 개발자', development)
        self.assertNotIn('개발 경력', development)
        self.assertNotIn('openaithon', development)
        self.assertEqual(activities.count('data-other-experience='), 4)
        self.assertIn('data-other-experience="openaithon"', activities)
        self.assertNotIn('data-other-experience="manlev"', activities)
        self.assertIn('data-other-experience="42seoul"', activities)
        self.assertIn('기타 활동', activities)
        self.assertIn('Other Activities', activities)
        for output in [site_sections.teaching_summary(), site_sections.teaching_detail()]:
            self.assertEqual(output.count('data-other-experience="openaithon"'), 1)

    def test_redundant_teaching_scope_copy_is_removed(self):
        for output in [site_sections.teaching_summary(), site_sections.teaching_detail()]:
            self.assertNotIn('학교별 확인된 과정으로 분류했습니다', output)
            self.assertNotIn('Grouped by verified school-specific courses', output)
            self.assertNotIn('공통 활동기간을 중복 합산하지 않습니다', output)
            self.assertNotIn('shared activity periods are not added together', output)
            self.assertIn('data-teaching="donghaeng-educore-2025"', output)
        self.assertIn('data-career-detail="jeohyeon"', site_sections.teaching_detail())

    def test_notitle_preserves_confirmed_role_and_dates_without_invented_details(self):
        row = next(item for item in DATA['otherExperience'] if item['id']=='notitle')
        self.assertEqual((row['start'],row['end']), ('2024-03','2024-05'))
        self.assertEqual(row['role'], {'ko':'풀스택 개발자','en':'Full-stack developer'})
        self.assertEqual(row['group'], 'development')
        self.assertEqual(row['description'], {'ko':'백엔드 FastAPI · 프론트엔드 Next.js·React.','en':'Backend: FastAPI · Frontend: Next.js and React.'})
        for output in [site_sections.teaching_summary(),site_sections.teaching_detail()]:
            self.assertEqual(output.count('data-other-experience="notitle"'),1)
        detail=site_sections.other_experience()
        self.assertIn('aria-controls="snow-career-notitle"',detail)
        self.assertLess(detail.index('data-other-experience="notitle"'),detail.index('data-other-experience="ted"'))

    def test_verified_project_additions_preserve_scope_and_date_precision(self):
        rows = {item['id']:item for item in DATA['otherExperience']}
        cleaning = rows['cleaning-service']
        self.assertEqual((cleaning['start'], cleaning['end']), ('2018-12', '2019-01'))
        self.assertEqual(cleaning['group'], 'development')
        self.assertNotIn('CleanUP', str(cleaning))
        self.assertNotIn('React Native', str(cleaning))
        self.assertNotIn('출시', str(cleaning))
        capstone = rows['kimanna-capstone']
        self.assertEqual((capstone['start'], capstone['end']), ('2018', '2018'))
        self.assertEqual(capstone['group'], 'activities')
        self.assertEqual(capstone['url'], 'https://github.com/Snowiner/KimAnNa2')
        self.assertNotIn('팀장', str(capstone))
        self.assertNotIn('team lead', str(capstone))
        for output in [site_sections.teaching_summary(), site_sections.teaching_detail()]:
            for key in ['cleaning-service', 'kimanna-capstone']:
                self.assertEqual(output.count('data-other-experience="'+key+'"'), 1)
            self.assertIn('href="https://github.com/Snowiner/KimAnNa2"', output)
        self.assertNotIn('kimanna-capstone', site_sections.other_experience())
        self.assertNotIn('cleaning-service', site_sections.other_experience(group='activities'))
        self.assertEqual((rows['manlev']['start'],rows['manlev']['end']), ('2014-06','2015-01'))
        self.assertFalse(any('AIZEN' in str(item) for item in DATA['otherExperience']))

    def test_kdigital_completion_uses_verified_year_only_once(self):
        row = next(item for item in DATA['otherExperience'] if item['id']=='goorm-kdigital-nlp')
        self.assertEqual((row['start'], row['end']), ('2022', '2022'))
        self.assertEqual(row['group'], 'activities')
        self.assertEqual(row['role'], {'ko':'수료', 'en':'Completed'})
        self.assertIn('AI 자연어 처리 전문가 양성 과정', row['title']['ko'])
        self.assertNotIn('4기', str(row))
        for output in [site_sections.teaching_summary(), site_sections.teaching_detail()]:
            self.assertEqual(output.count('data-other-experience="goorm-kdigital-nlp"'), 1)
        self.assertNotIn('goorm-kdigital-nlp', site_sections.other_experience())
        self.assertFalse(any('K-Digital' in str(item) for item in DATA['qualifications']))

    def test_42seoul_starts_at_la_piscine_without_completion_claim(self):
        row = next(item for item in DATA['otherExperience'] if item['id']=='42seoul')
        self.assertEqual(row['title'], {'ko':'42서울', 'en':'42 Seoul'})
        self.assertEqual((row['start'], row['end']), ('2020-07', '2021-11'))
        self.assertEqual(row['group'], 'activities')
        self.assertIn('라피신: 2020.07–2020.08', row['description']['ko'])
        self.assertIn('본과정: 2020.09–2021.11', row['description']['ko'])
        self.assertNotIn('졸업', row['description']['ko'])
        self.assertNotIn('수료', row['description']['ko'])
        output = site_sections.other_experience(group='activities')
        self.assertEqual(output.count('data-other-experience="42seoul"'), 1)
        self.assertLess(output.index('data-other-experience="42seoul"'), output.index('data-other-experience="openaithon"'))
        self.assertNotIn('42seoul', site_sections.other_experience())

    def test_invalid_detail_dates_and_roles_stop_build(self):
        changed=copy.deepcopy(DATA['teaching'])
        changed[0]['details'][0]['start']='2026-13'
        with patch.dict(DATA, teaching=changed), self.assertRaisesRegex(ValueError, 'Invalid career date'):
            validate()
        changed[0]['details'][0]['start']='2026-08'
        changed[0]['details'][0]['role']='unknown'
        with patch.dict(DATA, teaching=changed), self.assertRaisesRegex(ValueError, 'Unknown detail role'):
            validate()

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

