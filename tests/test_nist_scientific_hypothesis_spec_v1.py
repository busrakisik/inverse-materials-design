import copy
import json
import unittest
from pathlib import Path
from scripts.nist_scientific_hypothesis_spec_v1 import validate_spec, FALSE_FLAGS, REQUIRED_GATES

DATA = json.loads(Path("research/NIST_SCIENTIFIC_HYPOTHESIS_SPEC_V1.json").read_text())


class HypothesisSpecTests(unittest.TestCase):
    def test_baseline(self):
        result = validate_spec(DATA)
        self.assertEqual(result["primary_target"], "Kerr")
        self.assertEqual(result["unresolved_gates"], 6)

    def test_deterministic(self):
        self.assertEqual(validate_spec(DATA), validate_spec(copy.deepcopy(DATA)))

    def test_all_flags_fail_closed(self):
        for flag in FALSE_FLAGS:
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                altered = copy.deepcopy(DATA)
                altered[flag] = True
                validate_spec(altered)

    def test_missing_flag_rejected(self):
        altered = copy.deepcopy(DATA)
        del altered["independent_holdout_used"]
        with self.assertRaises(ValueError): validate_spec(altered)

    def test_source_hash_locked(self):
        altered = copy.deepcopy(DATA)
        altered["source"]["git_blob_sha1"] = "0" * 40
        with self.assertRaises(ValueError): validate_spec(altered)

    def test_source_commit_locked(self):
        altered = copy.deepcopy(DATA)
        altered["source"]["commit"] = "a" * 40
        with self.assertRaises(ValueError): validate_spec(altered)

    def test_no_models_relabelled_as_physics(self):
        altered = copy.deepcopy(DATA)
        altered["model_families_are_phenomenological"] = False
        with self.assertRaises(ValueError): validate_spec(altered)

    def test_wrong_primary_target(self):
        altered = copy.deepcopy(DATA)
        altered["primary_target"] = "Coer"
        with self.assertRaises(ValueError): validate_spec(altered)

    def test_bad_units(self):
        altered = copy.deepcopy(DATA)
        altered["primary_target_units"] = "mT"
        with self.assertRaises(ValueError): validate_spec(altered)

    def test_model_family_changed(self):
        altered = copy.deepcopy(DATA)
        altered["model_families"].append("invented")
        with self.assertRaises(ValueError): validate_spec(altered)

    def test_missing_gate(self):
        altered = copy.deepcopy(DATA)
        altered["unresolved_gates"].pop()
        with self.assertRaises(ValueError): validate_spec(altered)

    def test_complete_gate_inventory(self):
        self.assertEqual(DATA["unresolved_gates"], list(REQUIRED_GATES))

    def test_no_sources(self):
        altered = copy.deepcopy(DATA)
        altered["literature"] = []
        with self.assertRaises(ValueError): validate_spec(altered)

    def test_no_live_data_or_benchmark_invocation(self):
        source = Path("scripts/nist_scientific_hypothesis_spec_v1.py").read_text()
        self.assertNotIn("urlopen(", source)
        self.assertNotIn("make_task(", source)
        self.assertNotIn("run_grid(", source)
        self.assertNotIn("loadmat(", source)

    def test_wrong_status(self):
        altered = copy.deepcopy(DATA)
        altered["status"] = "VALIDATED"
        with self.assertRaises(ValueError): validate_spec(altered)

    def test_no_domain_approval_in_spec(self):
        self.assertFalse(DATA["domain_expert_approved"])
        self.assertFalse(DATA["composition_column_order_authoritatively_verified"])


if __name__ == "__main__":
    unittest.main()
