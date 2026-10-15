"""Regression checks for shared edits, derived summaries, and build guards."""
import copy
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from content import DATA, LOCALES, localized, reference, teaching_values, validate, write_if_changed
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
            self.assertEqual(site_sections.teaching_detail().count('Updated shared course'), 1)
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
        self.assertEqual(detail.count('class="career-details"'), len(DATA['teaching'])+len(DATA['otherExperience']))
        expected=sum(len(item.get('details', [])) for item in DATA['teaching'])
        self.assertEqual(detail.count('data-career-detail='), expected)

    def test_four_themes_preserve_every_program_once(self):
        from content import teaching_records
        self.assertEqual([group['id'] for group in DATA['teachingGroups']], ['ai','data','programming'])
        self.assertEqual([len(teaching_records(group['id'])) for group in DATA['teachingGroups']], [6,1,7])
        self.assertEqual(DATA['courses']['donghaeng-data']['group'], 'data')
        self.assertEqual(DATA['courses']['algorithms']['group'], 'programming')
        self.assertEqual(DATA['courses']['codyssey']['group'], 'programming')
        self.assertEqual(DATA['courses']['hanalife']['group'], 'ai')
        detail=site_sections.teaching_detail()
        summary=site_sections.teaching_summary()
        self.assertEqual(detail.count('class="history-group'),4)
        for item in DATA['teaching']:
            for output in [summary,detail]:
                self.assertEqual(output.count(f'data-teaching="{item["id"]}"'),1)
        for item in DATA['otherExperience']:
            for output in [summary,detail]:
                self.assertEqual(output.count(f'data-other-experience="{item["id"]}"'),1)
        self.assertEqual(detail.count('data-career-detail='),30)
        self.assertIn('<small>17</small>',summary)
        self.assertEqual([len(item['details']) for item in DATA['teaching'] if item['course'] in ['saessak','donghaeng-data']], [5,7])

    def test_simple_career_buttons_have_unique_accessible_targets(self):
        output=site_sections.teaching_detail()
        buttons=re.findall(r'<button type="button" class="career-toggle cursor-interaction"([^>]+)>(.*?)</button>',output)
        self.assertEqual(len(buttons),17)
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
        codex=item['details'][2]
        self.assertIn('진행 중', codex['note']['ko'])
        self.assertIn('scheduled', codex['note']['en'])
        output=site_sections.teaching_details(item)
        self.assertEqual(output.count('data-career-detail='), 3)
        self.assertIn('2026.08–2026.09', output)
        self.assertIn('2026.10–현재', output)
        self.assertNotIn('goyang-citizens', output)

    def test_elice_and_educore_curricula_are_separate(self):
        elice=next(item for item in DATA['teaching'] if item['id']=='donghaeng-elice-2023')
        educore=next(item for item in DATA['teaching'] if item['id']=='donghaeng-educore-2025')
        self.assertNotEqual(elice['course'], educore['course'])
        self.assertEqual(elice['start'], '2024-09')
        self.assertIn('데이터', teaching_values(elice, 'ko')['course'])
        self.assertIn('AI 활용 웹앱', teaching_values(educore, 'ko')['course'])
        self.assertIn('로그인', educore['details'][0]['curriculum']['ko'])
        for item in educore['details'][1:]:
            self.assertNotIn('로그인', item['curriculum']['ko'])

    def test_non_program_experience_is_separate(self):
        output=site_sections.other_experience()
        self.assertEqual(output.count('data-other-experience='), 3)
        self.assertIn('프론트엔드 개발자', output)
        self.assertNotIn('data-teaching=', output)

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

