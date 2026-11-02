import pathlib
import tempfile
import unittest
from unittest.mock import patch
from scripts.validation_freeze_prepare_v1 import FILES, PILOT_SEEDS, SEEDS, STATUS, digest, prepare

class FreezePreparationTests(unittest.TestCase):
    def test_seeds_unique(self):
        self.assertEqual(len(SEEDS), len(set(SEEDS)))
    def test_seed_count(self):
        self.assertEqual(len(SEEDS), 100)
    def test_pilot_disjoint(self):
        self.assertTrue(PILOT_SEEDS.isdisjoint(SEEDS))
    def test_digest_stable(self):
        self.assertEqual(digest(b'abc'), digest(b'abc'))
    def test_all_sources_required(self):
        with tempfile.TemporaryDirectory() as t, patch('scripts.validation_freeze_prepare_v1.subprocess.check_output', return_value='a'*40):
            with self.assertRaises(FileNotFoundError): prepare(t)
    def test_invalid_sha_rejected(self):
        with tempfile.TemporaryDirectory() as t, patch('scripts.validation_freeze_prepare_v1.subprocess.check_output', return_value='not-a-sha'):
            with self.assertRaises(ValueError): prepare(t)
    def test_repo_proposal_fail_closed(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        r = prepare(root)
        self.assertEqual(r['status'], STATUS)
        self.assertFalse(r['scored_validation_allowed'])
        self.assertFalse(r['freeze_approved'])
        self.assertFalse(r['all_other_development_seeds_audited'])
        self.assertIsNone(r['primary_scenario'])
        self.assertEqual(set(r['source_sha256']), set(FILES))
        self.assertEqual(len(r['proposed_holdout_seeds']), 100)

if __name__ == '__main__': unittest.main()
