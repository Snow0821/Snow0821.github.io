"""Regression checks for shared edits, derived summaries, and build guards."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from content import DATA, LOCALES, localized, reference, teaching_columns, teaching_records, experience_records, validate, write_if_changed
from rendered_site import page, section, text


class SharedContentTests(unittest.TestCase):


    def test_education_is_separate_from_qualifications(self):
        education = text(section("ko", "education"))
        qualifications = text(section("ko", "credentials"))
        self.assertIn("공학석사", education)
        self.assertIn("국민대학교", education)
        self.assertNotIn("NCS", education)
        self.assertIn("NCS", qualifications)
        self.assertNotIn("공학석사", qualifications)

    def test_course_reference_uses_the_updated_title_in_each_language(self):
        course = next(r for r in teaching_records() if r['course'] == 'lginnotek')
        changed = {'ko': '변경된 공통 과정', 'en': 'Updated shared course'}
        with patch.dict(DATA['courses']['lginnotek'], title=changed):
            for lang, title in changed.items():
                self.assertEqual(teaching_columns(course, lang)['subject'], title)

    def test_detailed_school_records_are_confined_to_the_career_route(self):
        for lang in ("ko", "en"):
            home = page(lang)
            career = section(lang, "teaching")
            self.assertIsNone(home.find('.//*[@data-detail="jeohyeon"]'))
            self.assertIsNotNone(career.find('.//*[@data-detail="jeohyeon"]'))

    def test_source_records_preserve_unique_programs_and_details(self):
        from collections import Counter
        self.assertEqual([group['id'] for group in DATA['teachingGroups']], ['ai-data','programming'])
        self.assertEqual(len(teaching_records()), len(DATA['teaching']))
        self.assertEqual(DATA['courses']['algorithms']['group'], 'programming')
        self.assertEqual(DATA['courses']['codyssey']['group'], 'ai')
        self.assertEqual(DATA['courses']['codyssey']['title']['ko'], 'AI Native 과정 · 코디세이')
        self.assertEqual(DATA['courses']['hanalife']['group'], 'ai')
        views=teaching_records()
        self.assertEqual(Counter(item['id'] for item in views), Counter(item['id'] for item in DATA['teaching']))
        expected=Counter(detail['id'] for item in DATA['teaching'] for detail in item['details'])
        actual=Counter(detail['id'] for item in views for detail in item['details'])
        self.assertEqual(actual, expected)
        for source in DATA['teaching']:
            self.assertEqual(next(row for row in views if row['id']==source['id'])['details'], source['details'])
        self.assertTrue(all(n == 1 for n in expected.values()))

    def test_school_courses_use_verified_categories(self):
        by_group={group:set() for group in ['ai','data','programming']}
        for item in teaching_records():
            for detail in item['details']:
                for track in detail.get('tracks') or [detail]:
                    if track.get('group') in by_group:
                        key=detail['id']+'-'+track['id'] if track is not detail else detail['id']
                        by_group[track['group']].add(key)
        self.assertTrue({'mirae','munchang','sudo-ai','munhak-ai','jamsil-girls-ai'} <= by_group['ai'])
        self.assertTrue({'hwagok','sudo-data','haseong-data','munhak-data','jamsil-girls-data'} <= by_group['data'])
        self.assertTrue({'cheongwon-girls','ansan-design','seoul-robot','handong-a','handong-b','haseong-python'} <= by_group['programming'])
        self.assertNotIn('hwagok',by_group['programming'])
        self.assertNotIn('mirae',by_group['programming'])
        for item in teaching_records():
            for detail in item['details']:
                if detail['id'] in ['sudo','haseong','munhak','jamsil-girls']:
                    for track in detail['tracks']:
                        self.assertNotIn('start',track)  # Unverified dates remain absent.
                        self.assertNotIn('end',track)

    def test_unified_history_preserves_all_track_curricula(self):
        records = teaching_records()
        self.assertEqual(len(records), len(DATA['teaching']))
        source_ids = [item['id'] for item in records]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertGreaterEqual(sum(len(item['details']) for item in records), 31)
        for item in records:
            source_details = [detail['id'] for detail in item['details']]
            self.assertEqual(len(source_details), len(set(source_details)))
        merged = {detail['id']:detail for item in records for detail in item['details'] if detail.get('tracks')}
        self.assertEqual(set(merged), {'sudo', 'munhak', 'jamsil-girls', 'haseong'})
        for detail in merged.values():
            expected={'data','programming'} if detail['id']=='haseong' else {'ai','data'}
            self.assertEqual({track['group'] for track in detail['tracks']}, expected)
            for track in detail['tracks']:
                for lang in ['ko','en']:
                    self.assertTrue(track['title'][lang].strip())
                    self.assertTrue(track['curriculum'][lang].strip())
        for lang in ["ko", "en"]:
            school_records = section(lang, "teaching").findall('.//*[@data-detail]')
            display_ids = [node.get('data-detail') for node in school_records]
            for school_id in merged:
                self.assertEqual(display_ids.count(school_id), 1)


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


    def test_goyang_has_three_distinct_completed_courses(self):
        item = next(row for row in DATA['teaching'] if row['id'] == 'goyang-educore-2026-08')
        self.assertEqual([r['id'] for r in item['details']],
                         ['goyang-web-1', 'goyang-web-2', 'goyang-codex'])
        dates = [(r['start'][:7], r['end'][:7]) for r in item['details']]
        self.assertEqual(dates, [('2026-08', '2026-09'), ('2026-09', '2026-09'), ('2026-10', '2026-10')])
        self.assertIn('Codex', text(section("ko", "teaching")))
        self.assertNotIn('10월 종료 예정', text(page("ko").find(".//main")))

    def test_elice_and_educore_curricula_are_separate(self):
        elice=next(item for item in DATA['teaching'] if item['id']=='donghaeng-elice-2023')
        educore=next(item for item in DATA['teaching'] if item['id']=='donghaeng-educore-2025')
        self.assertNotEqual(elice['course'], educore['course'])
        self.assertEqual(elice['start'], '2024-09')
        self.assertIn('학교별', teaching_columns(elice, 'ko')['subject'])
        self.assertIn('AI 프로젝트 교육', teaching_columns(educore, 'ko')['subject'])
        self.assertIn('책임 있는 AI·SDGs', educore['details'][0]['curriculum']['ko'])
        self.assertIn('발표 및 단계별 피드백', educore['details'][0]['curriculum']['ko'])
        for item in educore['details'][1:]:
            self.assertNotIn('로그인', item['curriculum']['ko'])

    def test_educore_school_programs_reuse_five_existing_details(self):
        item = next(row for row in DATA['teaching'] if row['id']=='donghaeng-educore-2025')
        self.assertEqual(len(item['details']), 5)
        expected = {'jeohyeon': ('2025-04', '2025-07'), 'guryong': ('2025-04', '2025-07'),
                    'seowon': ('2025-05', '2025-07'), 'seoul-digitech': ('2025-04', '2025-06'),
                    'yeongjong': ('2025-05', '2025-06')}
        self.assertEqual({row['id']:(row['start'],row['end']) for row in item['details']}, expected)
        self.assertEqual(len({row['programTitle']['ko'] for row in item['details']}), 3)
        output = text(section('ko', 'teaching'))
        for row in item['details']:
            self.assertIn(row['programTitle']['ko'], output)
        summary = next(row for row in teaching_records() if row['id']==item['id'])
        self.assertTrue(all(row['title']['ko'] in summary['schoolSummary']['ko'] for row in item['details']))
        self.assertIn('교통신호', output)
        self.assertIn('산불 예측', output)
        self.assertIn('책임 있는 소비', output)

    def test_work_projects_and_training_have_distinct_destinations(self):
        employment = text(section("ko", "employment"))
        training = text(section("ko", "training"))
        projects = text(page("ko", "portfolio").find(".//main"))
        self.assertIn("마이마부", employment)
        self.assertIn("42", training)
        self.assertNotIn("42서울", employment)
        self.assertIn("KimAnNa", projects)

    def test_ted_and_game_planning_are_professional_experience(self):
        employment = section("ko", "employment")
        self.assertIsNotNone(employment.find('.//*[@data-record="ted"]'))
        self.assertIsNotNone(employment.find('.//*[@data-record="manlev"]'))
        self.assertIn("프론트엔드", text(employment))
        self.assertIn("기획", text(employment))
        self.assertNotIn("OpenAIThon", text(employment))


    def test_notitle_preserves_confirmed_role_and_dates_without_invented_details(self):
        row = next(item for item in DATA['otherExperience'] if item['id']=='notitle')
        self.assertEqual((row['start'],row['end']), ('2024-03','2024-05'))
        self.assertEqual(row['role'], {'ko':'풀스택 개발자','en':'Full-stack developer'})
        self.assertEqual(row['group'], 'development')
        self.assertEqual(row['description'], {'ko':'백엔드 FastAPI · 프론트엔드 Next.js·React.','en':'Backend: FastAPI · Frontend: Next.js and React.'})
        for lang in ('ko', 'en'):
            employment = section(lang, 'employment')
            ids = [node.get('data-record') for node in employment.iter() if 'data-record' in node.attrib]
            self.assertEqual(ids.count('notitle'), 1)
            self.assertLess(ids.index('notitle'), ids.index('ted'))

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
        for lang in ('ko', 'en'):
            urls = [link.get('href') for link in page(lang, 'portfolio').iter('a')]
            self.assertIn(capstone['url'], urls)

        self.assertEqual((rows['manlev']['start'],rows['manlev']['end']), ('2014','2015'))
        self.assertFalse(any('AIZEN' in str(item) for item in DATA['otherExperience']))

    def test_kdigital_records_participation_and_verified_year(self):
        row = next(item for item in DATA['otherExperience'] if item['id']=='goorm-kdigital-nlp')
        self.assertEqual((row['start'], row['end']), ('2022', '2022'))
        self.assertEqual(row['group'], 'activities')
        self.assertNotIn('수료', row['role']['ko'])
        self.assertNotIn('completed', row['role']['en'].lower())
        self.assertIn('AI 자연어 처리 전문가 양성 과정', row['title']['ko'])
        self.assertNotIn('4기', str(row))
        self.assertIsNotNone(section('ko', 'training').find('.//*[@data-record="goorm-kdigital-nlp"]'))
        self.assertFalse(any('K-Digital' in str(item) for item in DATA['qualifications']))

    def test_42seoul_records_participation_without_a_completion_claim(self):
        row = next(item for item in DATA['otherExperience'] if item['id'] == '42seoul')
        self.assertEqual(row['title'], {'ko':'42서울', 'en':'42 Seoul'})
        self.assertEqual((row['start'], row['end']), ('2020', '2021'))
        self.assertEqual(row['careerCategory'], 'training')
        self.assertIn('라피신', row['role']['ko'])
        self.assertIn('Cadet', row['role']['en'])
        self.assertNotIn('수료', str(row))
        self.assertNotIn('졸업', str(row))
        self.assertEqual(len(section('ko','training').findall('.//*[@data-record="42seoul"]')), 1)
        self.assertIsNone(section('ko','employment').find('.//*[@data-record="42seoul"]'))

    def test_invalid_detail_dates_and_roles_stop_build(self):
        changed=copy.deepcopy(DATA['teaching'])
        changed[0]['details'][0]['start']='2026-13'
        with patch.dict(DATA, teaching=changed), self.assertRaisesRegex(ValueError, 'Invalid career date'):
            validate()
        changed[0]['details'][0]['start']='2026-08'
        changed[0]['details'][0]['role']='unknown'
        with patch.dict(DATA, teaching=changed), self.assertRaisesRegex(ValueError, 'Unknown detail role'):
            validate()


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


    def test_mincoding_groups_two_assignments_without_duplicate_teaching_rows(self):
        row=next(item for item in experience_records() if item['id']=='mincoding')
        self.assertEqual((row['start'],row['end']),('2025','2025'))
        self.assertEqual([s['id'] for s in row['assignments']],['tacademy-mincoding-2025','sds-mincoding-2025'])
        self.assertEqual([s['role'] for s in row['assignments']],['instructor','assistant'])
        for lang in ['ko','en']:
            self.assertIn('T',row['description'][lang])
            self.assertIn('SDS',row['description'][lang])
            self.assertIn(DATA['roles']['assistant'][lang],row['description'][lang])
        self.assertIsNone(section('ko', 'employment').find('.//*[@data-record="mincoding"]'))
        for course in row['assignments']:
            self.assertEqual(len(section('ko', 'teaching').findall(f'.//*[@data-record="{course["id"]}"]')), 1)


if __name__ == '__main__':
    unittest.main()
