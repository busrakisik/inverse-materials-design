import pathlib
import tempfile
import unittest
from unittest.mock import patch
from scripts.freeze_readiness_v1 import assess, seed_digest, SEEDS, STATUS

class FreezeReadinessTests(unittest.TestCase):
    def test_seed_count(self): self.assertEqual(len(SEEDS),100)
    def test_seed_unique(self): self.assertEqual(len(set(SEEDS)),100)
    def test_seed_disjoint_known_pilot(self): self.assertFalse(set(SEEDS)&set(range(30)))
    def test_seed_hash_reproducible(self): self.assertEqual(seed_digest(SEEDS),seed_digest(SEEDS))
    def test_empty_approval_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            self._populate(d)
            with patch('scripts.freeze_readiness_v1.subprocess.check_output',return_value='a'*40):
                r=assess(d,{})
            self.assertEqual(r['status'],STATUS)
            self.assertFalse(r['scored_validation_allowed'])
            self.assertFalse(r['all_checks_reported'])
    def test_fake_approval_does_not_open_gate(self):
        with tempfile.TemporaryDirectory() as d:
            self._populate(d)
            with patch('scripts.freeze_readiness_v1.subprocess.check_output',return_value='b'*40):
                r=assess(d,{'reviewer_approval':True,'independent_label_boundary_audit':True})
            self.assertFalse(r['scored_validation_allowed'])
            self.assertFalse(r['independent_evidence_verified'])
    def test_missing_source_fails(self):
        with tempfile.TemporaryDirectory() as d:
            with patch('scripts.freeze_readiness_v1.subprocess.check_output',return_value='c'*40):
                with self.assertRaises(FileNotFoundError): assess(d,{})
    def test_malformed_approval_fails(self):
        with tempfile.TemporaryDirectory() as d:
            self._populate(d)
            with patch('scripts.freeze_readiness_v1.subprocess.check_output',return_value='d'*40):
                with self.assertRaises(ValueError): assess(d,[])
    def test_wrong_commit_fails_check(self):
        with tempfile.TemporaryDirectory() as d:
            self._populate(d)
            with patch('scripts.freeze_readiness_v1.subprocess.check_output',return_value='e'*40):
                r=assess(d,{'approved_source_commit':'f'*40})
            self.assertFalse(r['checks']['approved_source_commit_matches'])
    def _populate(self,d):
        from scripts.freeze_readiness_v1 import FILES
        for rel in FILES:
            f=pathlib.Path(d)/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('test')

if __name__=='__main__':unittest.main()
