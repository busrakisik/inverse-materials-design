import pathlib, subprocess, tempfile, unittest
from scripts.seed_environment_inventory_v1 import scan_text, inventory, PROPOSED

class InventoryTests(unittest.TestCase):
    def test_range_overlap(self):
        self.assertTrue(scan_text('x.py','seeds=range(10000, 10100)')[0]['candidate_holdout_overlap'])
    def test_disjoint_range(self):
        self.assertFalse(scan_text('x.py','seeds=range(30)')[0]['candidate_holdout_overlap'])
    def test_literal_overlap(self):
        self.assertTrue(scan_text('x.py','seed = 10005')[0]['candidate_holdout_overlap'])
    def test_literal_outside(self):
        self.assertFalse(scan_text('x.py','seed = 42')[0]['candidate_holdout_overlap'])
    def test_empty(self):self.assertEqual(scan_text('x.py','foo=bar'),[])
    def test_never_approves(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        r=inventory(root)
        self.assertFalse(r['scored_validation_allowed']);self.assertFalse(r['development_seed_history_complete'])
        self.assertEqual(r['proposed_seed_count'],100)
    def test_git_metadata(self):
        r=inventory(pathlib.Path(__file__).resolve().parents[1])
        self.assertEqual(len(r['source_commit']),40)

if __name__=='__main__':unittest.main()
