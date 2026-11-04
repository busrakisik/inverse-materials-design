import pathlib
import tempfile
import unittest
from scripts.label_boundary_audit_v1 import assess, audit_repository, sha256, CORE, PILOT

CORE_FIXTURE = '''
class SyntheticTask:
    _labels: dict
class MeteredEvaluator:
    def run(self, policy):
        public = self._task.public_view()
        selected = policy.choose(public, ())
        return self._task._labels[selected]
'''
PILOT_FIXTURE = '''
def evaluate():
    optimum = max(task._labels.values())
    return optimum
'''

class BoundaryTests(unittest.TestCase):
    def test_detect_inprocess_risk(self):
        r = assess(CORE_FIXTURE, PILOT_FIXTURE)
        self.assertFalse(r['adversarial_code_isolation_established'])
        self.assertFalse(r['independent_label_firewall_review_completed'])
    def test_never_approves_holdout(self):
        r = assess(CORE_FIXTURE, PILOT_FIXTURE)
        self.assertFalse(r['scored_validation_allowed'])
        self.assertFalse(r['holdout_tasks_generated'])
        self.assertFalse(r['holdout_labels_accessed'])
    def test_all_five_checks(self):
        self.assertEqual(len(assess(CORE_FIXTURE, PILOT_FIXTURE)['static_structure_checks']), 5)
    def test_missing_policy_call_rejected(self):
        with self.assertRaises(ValueError): assess(CORE_FIXTURE.replace('policy.choose(public, ())', "'candidate_000'"), PILOT_FIXTURE)
    def test_missing_label_rejected(self):
        with self.assertRaises(ValueError): assess(CORE_FIXTURE.replace('self._task._labels[selected]', '0.0'), PILOT_FIXTURE)
    def test_missing_regret_access_rejected(self):
        with self.assertRaises(ValueError): assess(CORE_FIXTURE, PILOT_FIXTURE.replace('task._labels.values()', '[0.0]'))
    def test_missing_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError): audit_repository(pathlib.Path(d))
    def test_repository_source_hashes(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            for path, value in [(CORE, CORE_FIXTURE), (PILOT, PILOT_FIXTURE)]:
                f = root / path; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(value)
            r = audit_repository(root)
            self.assertEqual(r['source_sha256'][CORE], sha256(CORE_FIXTURE.encode()))
            self.assertEqual(len(r['source_sha256']), 2)

if __name__ == '__main__': unittest.main()
