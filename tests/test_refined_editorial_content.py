"""Approved editorial CV wording and paper-specific source-name regressions."""
import copy
import json
import sys
import unittest
from html import escape
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from content import DATA, authors, bibtex, current_role_records, display_authors, reference, validate
import publications


# Source IDs and date precision are preserved; the workshop role corrects a verified attribution error.
SOURCE_SCOPE = {'goyang-educore-2026-08': ['2026-08', None, 'instructor', '2026-10', None],
 'codyssey-modulabs-2026-06': ['2026-06', None, 'facilitator', '2026-10', None],
 'algorithms-coderland-2023-03': ['2023-03', None, 'online', None, None],
 'lginnotek-elice-2026-07': ['2026-07', '2026-07', 'instructor', None, None],
 'tacademy-mincoding-2025': ['2025', '2025', 'instructor', None, None],
 'sds-mincoding-2025': ['2025', '2025', 'assistant', None, None],
 'donghaeng-educore-2025': ['2025-04', '2025-07', 'instructor', None, None],
 'donghaeng-elice-2023': ['2024-09', '2024-11', 'instructor', None, None],
 'saessak-elice-2023': ['2023-05', '2024-12', 'instructor', None, None],
 'gosaek-gosaek-2023': ['2023-08', '2023-12', 'instructor', None, None],
 'hanalife-2026-10': ['2026-10', '2026-10', 'instructor', None, None],
 'paju-ablearn-2026-05': ['2026-05', '2026-07', 'assistant', None, ['2026-05', '2026-07']],
 'ai-workshop-elice-2024-12': ['2024-12', '2025-01', 'instructor', None, None],
 'lgcns-elice-2024-02': ['2024-02', '2024-02', 'instructor', None, None],
 'goyang-web-1': ['2026-08', '2026-09', 'instructor', None, None],
 'goyang-web-2': ['2026-09', '2026-09', 'instructor', None, None],
 'goyang-codex': ['2026-10', None, 'instructor', '2026-10', None],
 'codyssey-learners': ['2026-06', None, 'facilitator', '2026-10', None],
 'coderland-online': ['2023-03', None, 'online', None, None],
 'lg-employees': ['2026-07', '2026-07', 'instructor', None, None],
 'tacademy-course': ['2025', '2025', 'instructor', None, None],
 'sds-course': ['2025', '2025', 'assistant', None, None],
 'jeohyeon': ['2025-04', '2025-07', 'instructor', None, None],
 'guryong': ['2025-04', '2025-07', 'instructor', None, None],
 'seowon': ['2025-05', '2025-07', 'instructor', None, None],
 'seoul-digitech': ['2025-04', '2025-06', 'instructor', None, None],
 'yeongjong': ['2025-05', '2025-06', 'instructor', None, None],
 'haseong': ['2024-09', '2024-11', 'lead', None, None],
 'jamsil-girls': ['2024-10', '2024-10', 'lead', None, None],
 'munhak': ['2024-09', '2024-09', 'lead', None, None],
 'handong-a': ['2024-10', '2024-10', 'instructor', None, None],
 'handong-b': ['2024-10', '2024-10', 'instructor', None, None],
 'sangincheon': ['2024-11', '2024-11', 'lead', None, None],
 'munchang': ['2024-12', '2024-12', 'lead', None, None],
 'cheongwon-girls': ['2024-09', '2024-12', 'lead', None, None],
 'hwagok': ['2024-07', '2024-07', 'assistant', None, None],
 'mirae': ['2024-05', '2024-06', 'lead', None, None],
 'sudo': ['2023-09', '2023-11', 'lead', None, None],
 'ansan-design': ['2023-05', '2023-05', 'instructor', None, None],
 'seoul-robot': ['2023-05', '2023-05', 'instructor', None, None],
 'gosaek-elective': ['2023-08', '2023-12', 'instructor', None, None],
 'hana-employees': ['2026-10', '2026-10', 'instructor', None, None],
 'paju-officials': ['2026-05', '2026-07', 'assistant', None, ['2026-05', '2026-07']],
 'elice-instructors': ['2024-12', '2025-01', 'instructor', None, None],
 'lgcns-school': ['2024-02', '2024-02', 'instructor', None, None]}


class RefinedEditorialContentTests(unittest.TestCase):
    def test_validated_content(self):
        validate()

    def test_source_roles_dates_and_detail_count_are_preserved(self):
        rows = DATA['teaching'] + [detail for row in DATA['teaching'] for detail in row['details']]
        actual = {row['id']: [row['start'], row['end'], row['role'], row.get('plannedEnd'),
                             row.get('activeMonths')] for row in rows}
        self.assertEqual(actual, SOURCE_SCOPE)
        self.assertEqual(len(DATA['teaching']), 14)
        self.assertEqual(sum(len(row['details']) for row in DATA['teaching']), 31)

    def test_source_publication_names_are_paper_specific(self):
        expected = {
            '2026': ['Soon Ho Choi', 'Soo Yong Kim'],
            '2025': ['Soon Ho Choi', 'Jae Young Im', 'Soo Yeon Yoon'],
            '2024': ['Choi Soon Ho', 'Soo-Yeon Yoon'],
        }
        for paper in DATA['papers']:
            self.assertEqual(authors(paper), expected[paper['id']])
            for lang in ['ko', 'en']:
                self.assertTrue(display_authors(paper, lang)[0].startswith(expected[paper['id']][0]))
            for output in [publications.summary(paper), publications.detail(paper)]:
                for name in expected[paper['id']]:
                    self.assertIn(escape(name), output)
        self.assertEqual(DATA['profile']['name']['en'], 'Choi Soon Ho')
        self.assertEqual(DATA['authors']['yoon']['name'], 'Soo-Yeon Yoon')

    def test_citations_use_paper_specific_initials_and_bibtex_names(self):
        papers = {row['id']: row for row in DATA['papers']}
        self.assertIn('S. Y. Yoon', reference(papers['2025'], 'en'))
        self.assertNotIn('S.-Y. Yoon', reference(papers['2025'], 'en'))
        self.assertIn('Yoon, Soo Yeon', bibtex(papers['2025']))
        self.assertNotIn('Yoon, Soo-Yeon', bibtex(papers['2025']))
        self.assertIn('S.-Y. Yoon', reference(papers['2024'], 'en'))
        self.assertIn('Yoon, Soo-Yeon', bibtex(papers['2024']))
        for paper in DATA['papers']:
            self.assertIn('Choi, Soon Ho', bibtex(paper))
            self.assertNotIn('First author', bibtex(paper))
            self.assertNotIn('제1저자', reference(paper, 'ko'))

    def test_author_overrides_support_each_format_without_changing_global_records(self):
        paper = copy.deepcopy(DATA['papers'][0])
        original = copy.deepcopy(DATA['authors'])
        paper['authorOverrides']['choi'] = {
            'name': 'Source Name', 'initials': 'S. Name', 'bibtex': 'Name, Source'}
        self.assertEqual(authors(paper)[0], 'Source Name')
        self.assertTrue(reference(paper, 'en').startswith('S. Name and S. Y. Kim,'))
        self.assertIn('Name, Source and', bibtex(paper))
        self.assertEqual(DATA['authors'], original)

    def test_unknown_or_malformed_author_overrides_stop_build(self):
        invalid = [
            ([], 'Unknown author override'),
            ({'unknown': {'name': 'Unknown'}}, 'Unknown author override'),
            ({'choi': {'unknown': 'value'}}, 'Invalid author override'),
            ({'choi': {'name': ''}}, 'Invalid author override'),
            ({'choi': {'name': None}}, 'Invalid author override'),
            ({'choi': {}}, 'Invalid author override'),
            ({'choi': 'Source Name'}, 'Invalid author override'),
        ]
        for override, message in invalid:
            with self.subTest(override=override):
                papers = copy.deepcopy(DATA['papers'])
                papers[0]['authorOverrides'] = override
                with patch.dict(DATA, papers=papers), self.assertRaisesRegex(ValueError, message):
                    validate()

    def test_bachelors_keeps_one_degree_and_both_majors(self):
        rows = [row for row in DATA['education'] if row['id'] == 'bachelors']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['field'], {
            'ko': '컴퓨터공학·전자공학', 'en': 'Computer Science and Electrical Engineering'})
        self.assertEqual(rows[0]['degree']['ko'], '공학사')
        self.assertEqual(rows[0]['year'], 2019)

    def test_ncs_is_ai_registration_without_a_score(self):
        ncs = next(row for row in DATA['qualifications'] if row['id'] == 'ncs-ai')
        self.assertEqual(ncs['title']['ko'], 'NCS 확인강사')
        self.assertEqual(ncs['field']['ko'], '인공지능')
        self.assertEqual(ncs['year'], 2026)
        self.assertNotIn('score', ncs)
        self.assertNotIn('점', json.dumps(ncs, ensure_ascii=False))

    def test_current_titles_keep_specific_work_and_freelance_status(self):
        rows = {row['id']: row for row in current_role_records()}
        self.assertEqual(rows['educore']['title']['ko'], '고양 스마트시티즌')
        self.assertEqual(rows['modulabs']['title']['ko'], 'PBL 퍼실리테이터')
        self.assertEqual(rows['coderland']['title']['ko'], '온라인 프로그래밍 교육(프리랜서)')
        self.assertEqual(rows['coderland']['start'], '2023-03')
        for key in ['educore', 'modulabs']:
            self.assertIsNone(rows[key]['end'])
            self.assertEqual(rows[key]['plannedEnd'], '2026-10')

    def test_taught_content_avoids_generic_preparation_claims(self):
        teaching = {row['id']: row for row in DATA['teaching']}
        for key in ['goyang-educore-2026-08', 'hanalife-2026-10', 'tacademy-mincoding-2025']:
            row = teaching[key]
            texts = [row['summary']] + [detail['curriculum'] for detail in row['details']]
            for value in texts:
                self.assertNotIn('교안', value['ko'])
                self.assertNotIn('준비', value['ko'])
                self.assertNotIn('prepar', value['en'].lower())
        self.assertIn('Codex 업무 비서 제작 교육', teaching['goyang-educore-2026-08']['summary']['ko'])
        self.assertIn('PRD', teaching['hanalife-2026-10']['summary']['ko'])

    def test_jeohyeon_only_claims_confirmed_teaching_scope(self):
        detail = next(detail for row in DATA['teaching'] for detail in row['details']
                      if detail['id'] == 'jeohyeon')
        self.assertEqual(detail['curriculum']['ko'],
                         '책임 있는 AI·SDGs 기반 앱 프로젝트 기획·발표 및 단계별 피드백 지도.')
        for value in [detail['curriculum']['ko'], detail['focus']['ko']]:
            for unsupported in ['로그인', 'UI/UX', '데이터 저장', '테스트', '프롬프트']:
                self.assertNotIn(unsupported, value)

    def test_workshop_omits_misattributed_material_authorship(self):
        row = next(row for row in DATA['teaching'] if row['id'] == 'ai-workshop-elice-2024-12')
        self.assertEqual(row['role'], 'instructor')
        self.assertEqual(row['details'][0]['role'], 'instructor')
        self.assertFalse(row['showRole'])
        self.assertNotIn('materials', DATA['roles'])
        self.assertIn('AI·ML·DL 기초', row['summary']['ko'])
        self.assertEqual(DATA['courses'][row['course']]['title']['ko'], '손쉽게 공부하는 인공지능 · 강사 워크숍')
        for value in [row['summary']['ko'], row['details'][0]['curriculum']['ko']]:
            for unsupported in ['교안', '초안', '수정본', '자료 제작']:
                self.assertNotIn(unsupported, value)
        self.assertEqual((row['start'], row['end']), ('2024-12', '2025-01'))

    def test_assistant_roles_remain_explicit(self):
        rows = DATA['teaching'] + [detail for row in DATA['teaching'] for detail in row['details']]
        actual = {row['id']: row['role'] for row in rows}
        for key in ['hwagok', 'paju-ablearn-2026-05', 'paju-officials',
                    'sds-mincoding-2025', 'sds-course']:
            self.assertEqual(actual[key], 'assistant')

    def test_public_data_contains_no_private_evidence_links(self):
        serialized = json.dumps(DATA)
        for domain in ['mail.google.com', 'drive.google.com', 'docs.google.com']:
            self.assertNotIn(domain, serialized)


if __name__ == '__main__':
    unittest.main()
