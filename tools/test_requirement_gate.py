#!/usr/bin/env python3
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from requirement_gate import check
DATA=json.loads((ROOT/'requirements/manifest.json').read_text())
IDS=(ROOT/'requirements/required_ids.txt').read_text()
class TestGate(unittest.TestCase):
 def test_original_plan_valid(self): self.assertEqual(check(DATA,IDS,'plan'),[])
 def test_dropped_requirement_fails(self):
  x=copy.deepcopy(DATA);x['requirements'].pop();self.assertTrue(check(x,IDS,'plan'))
 def test_false_completed_without_evidence_fails(self):
  x=copy.deepcopy(DATA);x['requirements'][0]['status']='software_completed';self.assertTrue(check(x,IDS,'plan'))
 def test_unbuilt_release_fails(self): self.assertTrue(check(DATA,IDS,'release'))
 def test_unreviewed_new_owner_comment_fails(self):
  x=copy.deepcopy(DATA)
  for v in x['requirements']:
   v.update(status='software_completed',source_commit='verified-commit',implementation_files=['x.c'],test_refs=['test-x'],artifact_refs=['release.zip'])
  x['review'].update(source_comments_reviewed=True,issue_snapshot_date='2026-11-05',review_evidence='review.md',unmapped_owner_requests=['untracked comment'])
  self.assertTrue(check(x,IDS,'release'))
 def test_completed_and_reconciled_can_pass(self):
  x=copy.deepcopy(DATA)
  for v in x['requirements']:
   v.update(status='software_completed',source_commit='verified-commit',implementation_files=['x.c'],test_refs=['test-x'],artifact_refs=['release.zip'])
  x['review'].update(source_comments_reviewed=True,issue_snapshot_date='2026-11-05',review_evidence='review.md',unmapped_owner_requests=[])
  self.assertEqual(check(x,IDS,'release'),[])
if __name__=='__main__': unittest.main()
