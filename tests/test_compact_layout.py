"""A complete career directory and concise research views share the public data."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from content import DATA, localized, period, validate, teaching_records
from rendered_site import page, section, text
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
        for lang in ('ko','en'):
            article = section(lang,'teaching').find(f'.//*[@data-record="{row["id"]}"]')
            for key in ('provider', 'organization', 'subject'):
                self.assertIn(values[lang][key], text(article))
        lg=next(row for row in teaching_records() if row['course']=='lgcns-coding')
        self.assertEqual(teaching_columns(lg,'en')['provider'],'')
        self.assertEqual(teaching_columns(lg,'en')['audience'],'LG CNS employees’ children')
        self.assertEqual(teaching_columns(lg,'en')['subject'],'Children’s Coding School')
        hana=next(row for row in teaching_records() if row['course']=='hanalife')
        self.assertEqual(teaching_columns(hana,'en')['organization'],'Elice Coding')

    def test_verified_enterprise_context_preserves_client_and_program_separation(self):
        from content import teaching_columns
        hana=next(row for row in teaching_records() if row['course']=='hanalife')
        values=teaching_columns(hana,'ko')
        self.assertEqual(values['provider'],'K-하이테크플랫폼')
        self.assertEqual(values['audience'],'하나생명 임직원')
        self.assertEqual(values['organizationLabel'],'운영: 엘리스그룹')
        self.assertEqual(values['subject'],'AI로 설계하는 데이터 서비스 실무(STEP 2)')
        self.assertIn('PRD',hana['summary']['ko'])
        lg=next(row for row in teaching_records() if row['course']=='lginnotek')
        self.assertEqual(teaching_columns(lg,'ko')['provider'],'')
        self.assertEqual(teaching_columns(lg,'ko')['audience'],'LG이노텍 임직원')
        self.assertEqual(teaching_columns(lg,'ko')['subject'],'AI·AX Lv2 집체교육')
        self.assertIn('56시간', lg['details'][0]['note']['ko'])
        self.assertIn('56시간', lg['summary']['ko'])
        for row in [hana,lg]:
            self.assertEqual(row['organization'],'elice')
            self.assertNotIn('source_refs',str(row))
            self.assertNotIn('mail.google.com',str(row))

    def test_main_document_and_contact_links_resolve_to_the_expected_targets(self):
        from content import cv_filename
        for lang in ['ko', 'en']:
            urls = [link.get('href') for link in page(lang).iter('a')]
            self.assertIn('mailto:' + DATA['profile']['email'], urls)
            for social in DATA['profile']['links']:
                self.assertIn(social['url'], urls)
            self.assertIn('/assets/' + cv_filename(lang), urls)
        self.assertEqual(DATA['profile']['portfolioUrl'], 'https://snow0821.github.io/')

    def test_reported_and_scheduled_hours_stay_distinct(self):
        teaching = section('ko', 'teaching')
        by_id = lambda key: text(teaching.find(f'.//*[@data-record="{key}"]'))
        self.assertIn('56시간', by_id('lginnotek-elice-2026-07'))
        hana = by_id('hanalife-2026-10')
        self.assertIn('8시간 편성', hana)
        incheon = by_id('incheon-ablearn-2026-11')
        self.assertIn('아이디어를 콘텐츠로, AI 크리에이터', incheon)
        self.assertIn('편성', incheon)
        self.assertNotIn('취업 준비 키트', incheon)
        self.assertNotIn('11.10', incheon)
        self.assertIn('90분', by_id('jingwang-educore-2026-10'))
        self.assertNotIn('196', by_id('aba3-elice-2026-11'))

    def test_first_authorship_is_visible_on_its_own_language_page(self):
        from content import authors, display_authors
        self.assertEqual(len(DATA['papers']), 3)
        for paper in DATA['papers']:
            self.assertEqual(paper['authorRole'], 'first')
            for lang, role in [('ko','제1저자'),('en','First author')]:
                names = display_authors(paper, lang)
                self.assertEqual(names[0], authors(paper)[0] + ' (' + role + ')')
                self.assertEqual(names[1:], authors(paper)[1:])
                html = publications.detail(paper,lang)
                self.assertIn(names[0], html)
                self.assertEqual(html.count(role), 1)
            unconfirmed = dict(paper)
            unconfirmed.pop('authorRole')
            self.assertEqual(display_authors(unconfirmed, 'en'), authors(unconfirmed))
            self.assertNotIn('First author', publications.detail(unconfirmed, 'en'))

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

    def test_research_topics_follow_each_paper_in_both_languages(self):
        for paper in DATA['papers']:
            self.assertTrue(paper['topics'])
            for tag in paper['topics']:
                for lang in ['ko', 'en']:
                    self.assertIn(localized(tag,lang), publications.detail(paper,lang))
        changed = copy.deepcopy(DATA['papers'][0])
        changed['topics'] = [{'ko':'바뀐 주제', 'en':'A changed topic'}]
        self.assertIn('A changed topic', publications.detail(changed,'en'))
        self.assertIn('바뀐 주제', publications.detail(changed,'ko'))

    def test_topic_validation_rejects_duplicate_or_empty_tags(self):
        for tags in [[{'ko':'같음','en':'same'}]*2, [{'ko':'','en':'empty'}],
                     [{'ko':'같음','en':'same'}]*3, [{'ko':'번역 없음'}]]:
            papers = copy.deepcopy(DATA['papers'])
            papers[0]['topics'] = tags
            with patch.dict(DATA, papers=papers), self.assertRaisesRegex(ValueError, 'Invalid paper topics'):
                validate()

    def test_research_topics_and_their_translations_are_preserved(self):
        for topic in DATA['researchTopics']:
            self.assertTrue(topic['ko'].strip())
            self.assertTrue(topic['en'].strip())
        with patch.dict(DATA, researchTopics=[{'ko':'번역 없음'}]), self.assertRaisesRegex(ValueError,'Invalid research topics'):
            validate()

    def test_degree_records_and_registration_fields_are_separate(self):
        self.assertEqual(len(DATA['education']), 2)
        self.assertEqual(len(DATA['qualifications']), 1)
        for lang in ('ko', 'en'):
            self.assertNotIn('NCS', text(section(lang, 'education')))
            self.assertIn('NCS', text(section(lang, 'credentials')))

    def test_interest_history_is_preserved_without_a_separate_page(self):
        self.assertEqual(len(DATA['interests']), 3)
        for lang in ('ko','en'):
            self.assertFalse(any('/interests' in link.get('href','') for link in page(lang).iter('a')))

    def test_reading_the_detailed_course_list_preserves_source_data(self):
        row = next(item for item in teaching_records() if item['id']=='donghaeng-educore-2025')
        before = copy.deepcopy(row)
        for lang in ['ko','en']:
            article = section(lang,'teaching').find(f'.//*[@data-record="{row["id"]}"]')
            for school in row['details']:
                display = text(article.find(f'.//*[@data-detail="{school["id"]}"]'))
                self.assertIn(school['title'][lang], display)
                self.assertIn(period(school,lang), display)
                self.assertIn(school['programTitle'][lang], display)
        self.assertEqual(row, before)

    def test_institution_program_headings_do_not_merge_distinct_sources(self):
        from content import teaching_display_columns, teaching_subject
        by_id = {item['id']:item for item in teaching_records()}
        expected = {
            'donghaeng-educore-2025':'에듀코어센터 / 청소년 SW동행',
            'donghaeng-elice-2023':'엘리스그룹 / SW동행',
            'goyang-educore-2026-08':'에듀코어센터 / 고양 스마트시티즌',
            'codyssey-modulabs-2026-06':'모두의연구소 / 코디세이',
        }
        for record,heading in expected.items():
            institution,program=heading.split(' / ')
            columns=teaching_display_columns(by_id[record], 'ko')
            self.assertEqual(columns['organizationLines'],[institution])
            self.assertEqual(columns['provider'],program)
            output = site_sections.teaching_row(by_id[record], 'ko')
            for part in heading.split(' / '):
                self.assertIn(part, output)
        self.assertEqual(teaching_subject(by_id['codyssey-modulabs-2026-06'],'ko'), 'AI Native 과정')
        self.assertEqual(teaching_display_columns(by_id['algorithms-coderland-2023-03'],'ko')['organizationLines'], ['코더랜드'])
        self.assertEqual(len(by_id), len(DATA['teaching']))
        self.assertGreaterEqual(sum(len(row['details']) for row in by_id.values()), 31)

    def test_program_name_edit_propagates_and_requires_both_languages(self):
        changed = {'ko':'새 사업명','en':'Updated program'}
        target = next(r for r in teaching_records() if r['course'] == 'donghaeng')
        with patch.dict(DATA['courses']['donghaeng'], program=changed):
            for lang in ['ko','en']:
                self.assertIn(changed[lang], site_sections.teaching_row(target,lang))
        with patch.dict(DATA['courses']['donghaeng'], program={'ko':'번역 없음'}), self.assertRaisesRegex(ValueError,'Invalid program translation'):
            validate()


if __name__ == '__main__':
    unittest.main()
