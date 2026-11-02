import pathlib
import tempfile
import unittest
from unittest.mock import patch
from scripts.freeze_audit_v1 import audit, get_static_pilot_seed_range, PROPOSED_SEEDS, STATUS, sha256

class FreezeAuditTests(unittest.TestCase):
    def test_digest(self): self.assertEqual(sha256(b'abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
    def test_seed_count(self): self.assertEqual(len(PROPOSED_SEEDS),100)
    def test_seed_unique(self): self.assertEqual(len(set(PROPOSED_SEEDS)),100)
    def test_known_seed_disjoint(self): self.assertTrue(set(PROPOSED_SEEDS).isdisjoint(range(30)))
    def test_ast_pilot_seed(self): self.assertEqual(get_static_pilot_seed_range('def build_pilot(seeds=range(30)): pass'),tuple(range(30)))
    def test_ast_unknown(self): self.assertIsNone(get_static_pilot_seed_range('def build_pilot(seeds=OTHER): pass'))
    def test_missing_source_fails(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(FileNotFoundError): audit(pathlib.Path(t))
    def test_repository_audit_fail_closed(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        result=audit(root)
        self.assertEqual(result['status'], STATUS)
        self.assertFalse(result['scored_validation_allowed'])
        self.assertFalse(result['all_historical_development_seeds_audited'])
        self.assertFalse(result['freeze_approved'])
        self.assertFalse(result['environment_locked'])
        self.assertEqual(len(result['source_sha256']),6)

if __name__=='__main__': unittest.main()
