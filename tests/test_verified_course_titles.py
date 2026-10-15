"""Verified course names remain associated with their own schools and tracks."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from content import DATA,teaching_records,detail_program_titles,school_program_groups
import site_sections

class VerifiedCourseTitlesTests(unittest.TestCase):
    def records(self,course):
        return [r for group in ['ai-data','programming'] for r in teaching_records(group) if r['course']==course]

    def test_actual_names_reach_home_history_and_cv(self):
        import build_cv
        for row in self.records('donghaeng-data')+self.records('saessak'):
            for lang in ['ko','en']:
                expected=[title for group in school_program_groups(row,lang) for title in group['titles']]
                for summary in [True,False]:
                    html=site_sections.teaching_entry(row,summary)
                    for title in expected:
                        self.assertIn(title,html)
                with patch.object(build_cv,'p',side_effect=lambda value,*a,**k:value):
                    rendered=str(build_cv.teaching_pdf_rows(row,lang))
                for title in expected:
                    self.assertIn(title,rendered)

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
