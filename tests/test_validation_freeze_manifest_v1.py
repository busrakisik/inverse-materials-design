import json
import pathlib
import tempfile
import unittest
from scripts.validation_freeze_manifest_v1 import (
    SOURCE_FILES, SEEDS, assemble, canonical_json, seed_digest,
    validate_optional_evidence, sha256,
)


class ValidationFreezeManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        for p in SOURCE_FILES:
            t = self.root / p
            t.parent.mkdir(parents=True, exist_ok=True)
            t.write_text('controlled test fixture\n')
        self.commit = 'a' * 40

    def test_exact_seed_count_and_disjointness(self):
        self.assertEqual(len(SEEDS), 100)
        self.assertTrue(set(SEEDS).isdisjoint(range(30)))

    def test_seed_digest_stable(self):
        self.assertEqual(seed_digest(), seed_digest())
        self.assertEqual(len(seed_digest()), 64)

    def test_sha256_known_vector(self):
        self.assertEqual(sha256(b'abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')

    def test_missing_source_fails_closed(self):
        (self.root / SOURCE_FILES[0]).unlink()
        with self.assertRaises(FileNotFoundError):
            assemble(self.root, commit=self.commit)

    def test_invalid_commit_rejected(self):
        with self.assertRaises(ValueError):
            assemble(self.root, commit='not-a-commit')

    def test_no_evidence_never_approves(self):
        x = assemble(self.root, commit=self.commit)
        self.assertFalse(x['freeze_approved'])
        self.assertFalse(x['scored_validation_allowed'])
        self.assertFalse(x['external_independent_evidence_verified'])
        self.assertFalse(x['holdout_tasks_generated'])

    def test_all_self_attested_true_never_approves(self):
        blob = json.dumps({'status': 'APPROVED', 'freeze_approved': True,
                           'scored_validation_allowed': True,
                           'commit': self.commit}).encode()
        x = assemble(self.root, commit=self.commit, evidence={'fake.json': blob})
        self.assertFalse(x['scored_validation_allowed'])
        self.assertFalse(x['historical_artifacts_supplied'][0]['independently_verified'])

    def test_mismatched_evidence_commit_flag(self):
        x = assemble(self.root, commit=self.commit,
                     evidence={'old.json': json.dumps({'source_commit':'b'*40}).encode()})
        self.assertFalse(x['historical_artifacts_supplied'][0]['same_commit_as_current_tree'])

    def test_invalid_evidence_rejected(self):
        with self.assertRaises(ValueError):
            validate_optional_evidence('bad.json', b'{')
        with self.assertRaises(ValueError):
            validate_optional_evidence('list.json', b'[]')

    def test_evidence_path_traversal_rejected(self):
        with self.assertRaises(ValueError):
            assemble(self.root, commit=self.commit, evidence={'../bad.json':b'{}'})

    def test_canonical_deterministic_serialization(self):
        x = assemble(self.root, commit=self.commit)
        self.assertEqual(canonical_json(x), canonical_json(x))
        self.assertTrue(canonical_json(x).endswith(b'\n'))

    def test_source_digest_change_visible(self):
        before = assemble(self.root, commit=self.commit)
        (self.root / SOURCE_FILES[0]).write_text('changed\n')
        after = assemble(self.root, commit=self.commit)
        self.assertNotEqual(before['source_sha256'][SOURCE_FILES[0]],
                            after['source_sha256'][SOURCE_FILES[0]])


if __name__ == '__main__':
    unittest.main()
