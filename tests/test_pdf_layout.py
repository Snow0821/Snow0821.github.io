"""Geometry checks for PDF pills, independent of locally installed CJK fonts."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
try:
    from build_cv import PillTags,table
except ImportError:
    PillTags=None

@unittest.skipIf(PillTags is None,'ReportLab is optional for site-only validation')
class PDFLayoutTests(unittest.TestCase):
    def tags(self,labels,width):
        result=PillTags(labels)
        result.font_name='Helvetica'
        result.wrap(width,1000)
        return result

    def assert_bounds(self,result):
        for x,y,w,h,paragraph in result.placements:
            self.assertGreaterEqual(x,0)
            self.assertGreaterEqual(y,-.001)
            self.assertLessEqual(x+w,result.width+.001)
            self.assertLessEqual(y+h,result.height+.001)
            self.assertGreaterEqual(w-paragraph.width,result.pad_x*2-.001)
            self.assertGreaterEqual(h-paragraph.height,result.pad_y*2-.001)

    def test_tags_have_measured_internal_padding(self):
        result=self.tags(['Weight Quantization','Vision Transformers'],400)
        self.assert_bounds(result)
        self.assertEqual(len(result.placements),2)
        first,second=result.placements
        self.assertGreaterEqual(second[0]-first[0]-first[2],result.gap-.001)
        self.assertEqual(first[1],second[1])

    def test_tags_wrap_at_narrow_bounds_without_shrinking_type(self):
        result=self.tags(['Neural Architecture Learning','VeryLongUnbrokenResearchMethodLabel','Short'],100)
        self.assert_bounds(result)
        self.assertEqual(result.font_size,9)
        self.assertGreater(len({row[1] for row in result.placements}),1)
        self.assertTrue(all(row[4].style.fontSize==9 for row in result.placements))

    def test_empty_tag_set_is_safe(self):
        result=self.tags([],300)
        self.assertEqual(result.height,0)
        self.assertEqual(result.placements,[])

    def test_career_rows_cannot_split_internally(self):
        result=table([['date','course']],[100,300],header=False)
        self.assertEqual(result.splitByRow,1)
        self.assertEqual(result.splitInRow,0)
