"""Synthetic grader validation only; these are NOT human listening results."""
import importlib.util,pathlib,unittest
spec=importlib.util.spec_from_file_location('grade',pathlib.Path(__file__).parents[1]/'tools/english6_grade.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class GradeTest(unittest.TestCase):
 def setUp(self):self.key={'s00':{'engine':'baseline','note':60,'group':'vowels','word':'heed'},'s01':{'engine':'prototype','note':60,'group':'consonants','word':'she'}}
 def doc(self,rs):return {'protocol':'english6-blind-v1','responses':rs}
 def test_partial_confusion(self):
  r=m.grade(self.doc([{'id':'s00','response':'hid'}]),self.key);self.assertEqual(r['status'],'partial');self.assertEqual(r['missing_ids'],['s01']);self.assertEqual(r['by_engine_register_group']['baseline-60-vowels']['confusions'],{'heed':{'hid':1}})
 def test_complete_unclear(self):
  r=m.grade(self.doc([{'id':'s00','response':'heed'},{'id':'s01','response':'Unclear'}]),self.key);self.assertEqual(r['status'],'complete');self.assertEqual(r['by_engine_register_group']['prototype-60-consonants']['correct'],0)
 def test_reject_invalid(self):
  for rs in [[],[{'id':'bad','response':'heed'}],[{'id':'s00','response':'she'}],[{'id':'s00','response':'heed'}]*2]:
   with self.subTest(rs=rs),self.assertRaises(ValueError):m.grade(self.doc(rs),self.key)
if __name__=='__main__':unittest.main()
