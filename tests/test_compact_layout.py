"""Shared facts feed three displays; PDF-only condensation is presentation logic."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from content import DATA, LOCALES, localized, period, validate, teaching_records
import build_site
import publications
import site_sections


class CompactPresentationTests(unittest.TestCase):
    def test_teaching_columns_separate_verified_provider_and_actual_course(self):
        from content import teaching_columns
        row = next(row for row in teaching_records() if row['course']=='goyang')
        values = {lang:teaching_columns(row,lang) for lang in ['ko','en']}
        self.assertEqual(values['ko']['provider'], '고양 스마트시티즌')
        self.assertEqual(values['ko']['organization'], '에듀코어센터')
        self.assertEqual(values['ko']['subject'], 'AI 웹 제작 과정 · Codex 업무 비서 과정')
        for summary in [True,False]:
            html=site_sections.teaching_entry(row,summary)
            self.assertEqual(html.count('<td '),3)
            provider=html.split('<td class="teaching-provider"')[1].split('</td>')[0]
            course=html.split('<td class="teaching-course"')[1].split('</td>')[0]
            self.assertIn('고양 스마트시티즌',provider)
            self.assertIn('에듀코어센터',provider)
            self.assertIn('AI 웹 제작 과정',course)
            self.assertIn('class="teaching-role"',course)
            self.assertNotIn('고양 스마트시티즌',course.split('class="teaching-course-title"')[1].split('</h4>' if not summary else '</strong>')[0])
        lg=next(row for row in teaching_records() if row['course']=='lgcns-coding')
        self.assertEqual(teaching_columns(lg,'en')['provider'],'LG CNS')
        self.assertEqual(teaching_columns(lg,'en')['subject'],'Children’s Coding School')
        hana=next(row for row in teaching_records() if row['course']=='hanalife')
        self.assertEqual(teaching_columns(hana,'en')['organization'],'Elice Coding')

    def test_editorial_cv_uses_readable_type_and_verified_contact(self):
        try:
            import build_cv
        except ImportError:
            self.skipTest('ReportLab is optional for site-only validation')
        self.assertGreaterEqual(build_cv.STYLES['body'].fontSize, 10)
        self.assertGreaterEqual(build_cv.STYLES['small'].fontSize, 9)
        self.assertGreaterEqual(build_cv.STYLES['label'].fontSize, 9)
        self.assertEqual(DATA['profile']['email'], 'sosaror@gmail.com')
        self.assertEqual(DATA['profile']['portfolioUrl'], 'https://snow0821.github.io/')

    def test_verified_duty_summaries_are_shared_without_numeric_claims(self):
        selected = [row for row in teaching_records() if row.get('summary')]
        self.assertEqual({row['id'] for row in selected}, {'codyssey-modulabs-2026-06','hanalife-2026-10'})
        for row in selected:
            for lang in ['ko','en']:
                self.assertFalse(any(character.isdigit() for character in row['summary'][lang]))
                self.assertIn(row['summary'][lang], site_sections.teaching_entry(row, True))
                self.assertIn(row['summary'][lang], site_sections.teaching_entry(row, False))
        self.assertEqual(DATA['roles']['materials']['en'], 'Teaching materials writing & revision')

    def test_confirmed_first_authorship_reaches_both_web_views_and_cv_values(self):
        from content import authors, display_authors
        self.assertEqual(len(DATA['papers']), 3)
        for paper in DATA['papers']:
            self.assertEqual(paper['authorRole'], 'first')
            for lang, role in [('ko','제1저자'),('en','First author')]:
                names = display_authors(paper, lang)
                self.assertEqual(names[0], authors(paper)[0] + ' (' + role + ')')
                self.assertEqual(names[1:], authors(paper)[1:])
                for html in [publications.summary(paper), publications.detail(paper)]:
                    self.assertIn(names[0], html)
                    self.assertEqual(html.count(role), 1)
            unconfirmed = dict(paper)
            unconfirmed.pop('authorRole')
            self.assertEqual(display_authors(unconfirmed, 'en'), authors(unconfirmed))
            self.assertNotIn('First author', publications.summary(unconfirmed))

    def test_first_author_annotation_does_not_change_citations(self):
        from content import reference, bibtex
        for paper in DATA['papers']:
            original = dict(paper)
            original.pop('authorRole')
            self.assertEqual(bibtex(paper), bibtex(original))
            for lang in ['ko','en']:
                self.assertEqual(reference(paper, lang), reference(original, lang))

    def test_first_authorship_must_match_author_order(self):
        papers = copy.deepcopy(DATA['papers'])
        papers[0]['authors'].reverse()
        with patch.dict(DATA, papers=papers), self.assertRaisesRegex(ValueError,'First-author role conflicts'):
            validate()
        papers = copy.deepcopy(DATA['papers'])
        papers[0]['authorRole'] = 'corresponding'
        with patch.dict(DATA, papers=papers), self.assertRaisesRegex(ValueError,'Unknown author role'):
            validate()

    def test_research_tags_follow_each_paper_in_both_web_views(self):
        for paper in DATA['papers']:
            self.assertTrue(paper['topics'])
            for tag in paper['topics']:
                for lang in ['ko', 'en']:
                    self.assertIn(localized(tag,lang), publications.summary(paper))
                    self.assertIn(localized(tag,lang), publications.detail(paper))
        changed = copy.deepcopy(DATA['papers'][0])
        changed['topics'] = [{'ko':'바뀐 주제', 'en':'A changed topic'}]
        self.assertIn('A changed topic', publications.summary(changed))
        self.assertIn('A changed topic', publications.detail(changed))

    def test_topic_validation_rejects_duplicate_or_empty_tags(self):
        for tags in [[{'ko':'같음','en':'same'}]*2, [{'ko':'','en':'empty'}],
                     [{'ko':'같음','en':'same'}]*3, [{'ko':'번역 없음'}]]:
            papers = copy.deepcopy(DATA['papers'])
            papers[0]['topics'] = tags
            with patch.dict(DATA, papers=papers), self.assertRaisesRegex(ValueError, 'Invalid paper topics'):
                validate()

    def test_research_heading_and_area_tags_are_shared_and_bilingual(self):
        self.assertEqual(LOCALES['ko']['section.publications'], '연구활동')
        self.assertEqual(LOCALES['en']['section.publications'], 'Research Activities')
        self.assertIn('연구활동', build_site.navigation())
        self.assertIn('Research Activities', build_site.navigation())
        tags = publications.research_tags()
        for tag in DATA['researchTopics']:
            self.assertIn(tag['ko'], tags)
            self.assertIn(tag['en'], tags)
        changed = [{'ko':'새로운 연구 분야','en':'Changed research area'}]
        with patch.dict(DATA, researchTopics=changed):
            self.assertIn('Changed research area', publications.research_tags())
        with patch.dict(DATA, researchTopics=[{'ko':'번역 없음'}]), self.assertRaisesRegex(ValueError,'Invalid research topics'):
            validate()

    def test_degree_heading_preserves_separate_qualification_data(self):
        self.assertEqual(LOCALES['ko']['section.education'], '학위')
        self.assertEqual(LOCALES['en']['section.education'], 'Degrees')
        self.assertEqual(LOCALES['ko']['section.education_qualifications'], '학위·자격')
        self.assertEqual(LOCALES['en']['section.education_qualifications'], 'Degrees & Qualifications')
        self.assertEqual(len(DATA['education']), 2)
        self.assertEqual(len(DATA['qualifications']), 1)
        self.assertNotIn('NCS', site_sections.education())

    def test_no_standalone_interest_tab_or_home_section(self):
        nav = build_site.navigation()
        self.assertEqual(nav.count('role="tab"'), 3)
        self.assertNotIn('interests', nav)
        page = (Path(__file__).resolve().parents[1] / 'index.html').read_text()
        self.assertNotIn('snow-panel-interests', page)
        self.assertNotIn('snow-cv-interests', page)
        self.assertEqual(len(DATA['interests']), 3)  # Preserve source history.

    def test_cv_omits_school_dates_without_changing_history(self):
        # Optional ReportLab dependency must not become required for site-only builds.
        try:
            import build_cv
        except ImportError:
            self.skipTest('ReportLab is optional for site-only validation')
        row = next(item for item in teaching_records('ai') if item['id']=='donghaeng-educore-2025')
        before = copy.deepcopy(row)
        html = site_sections.teaching_details(row)
        for lang in ['ko', 'en']:
            # Inspect content only; the first column retains the overall business period.
            with patch.object(build_cv, 'p', side_effect=lambda value, *args: value):
                rows = build_cv.teaching_pdf_rows(row, lang)
            courses = ' '.join(part for record in rows for part in record[2] if isinstance(part,str))
            self.assertEqual(len(rows), 1)
            for program in {detail['programTitle'][lang] for detail in row['details']}:
                self.assertIn(program, courses)
            self.assertNotIn('2025.', courses)
            for school in row['details']:
                self.assertIn(school['title'][lang], courses)
                self.assertIn(period(school, lang), html)
        self.assertEqual(row, before)

    def test_institution_program_headings_do_not_merge_distinct_sources(self):
        from content import teaching_heading, teaching_subject
        by_id = {item['id']:item for item in teaching_records()}
        expected = {
            'donghaeng-educore-2025':'에듀코어센터 / 청소년 SW동행',
            'donghaeng-elice-2023':'엘리스코딩 / SW동행',
            'goyang-educore-2026-08':'에듀코어센터 / 고양 스마트시티즌',
            'codyssey-modulabs-2026-06':'모두의연구소 / 코디세이',
        }
        for record,heading in expected.items():
            self.assertEqual(teaching_heading(by_id[record], 'ko'), heading)
            for output in [site_sections.teaching_summary(), site_sections.teaching_detail()]:
                for part in heading.split(' / '):
                    self.assertIn(part, output)
        self.assertEqual(teaching_subject(by_id['codyssey-modulabs-2026-06'],'ko'), 'AI Native 과정')
        self.assertEqual(teaching_heading(by_id['algorithms-coderland-2023-03'],'ko'), '코더랜드')
        self.assertEqual(len(by_id), 14)
        self.assertEqual(sum(len(row['details']) for row in by_id.values()), 30)

    def test_program_name_edit_propagates_and_requires_both_languages(self):
        changed = {'ko':'새 사업명','en':'Updated program'}
        with patch.dict(DATA['courses']['donghaeng'], program=changed):
            self.assertIn('Updated program', site_sections.teaching_summary())
            self.assertIn('Updated program', site_sections.teaching_detail())
        with patch.dict(DATA['courses']['donghaeng'], program={'ko':'번역 없음'}), self.assertRaisesRegex(ValueError,'Invalid program translation'):
            validate()


if __name__ == '__main__':
    unittest.main()
