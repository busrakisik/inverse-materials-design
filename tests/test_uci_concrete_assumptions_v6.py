"""Contract tests for explicit assumption failure and observational label isolation."""
import unittest

import numpy as np

from scripts.uci_concrete_assumptions_v6 import (
    AssumptionViolation, analyze, audit_same_input_repeats,
    canonical_field_order, choose_disjoint_pairs_from_features,
    score_descriptive_contrasts, verify_source, EXPECTED_PARSED_SHA256
)

COLUMNS = [
    "Cement", "Blast Furnace Slag", "Fly Ash", "Water",
    "Superplasticizer", "Coarse Aggregate", "Fine Aggregate", "Age"
]


def make_synthetic():
    rng = np.random.default_rng(17)
    X = np.ones((1030, 8), dtype=float)
    X[:, 0] = 300 + rng.integers(0, 4, size=1030) * 20.0
    X[:, 1] = 35.0
    X[:, 2] = 45.0
    X[:, 3] = 120 + np.arange(1030) % 8 * 15.0
    X[:, 4] = 10.0
    X[:, 5] = 900.0
    X[:, 6] = 800.0
    X[:, 7] = 28.0
    y = np.linspace(30.0, 48.0, 1030)
    return X, y


class AssumptionAuditV6Tests(unittest.TestCase):
    def test_schema_and_units_guard(self):
        self.assertEqual(len(canonical_field_order(COLUMNS)), 8)
        with self.assertRaisesRegex(AssumptionViolation, "SCHEMA_MISMATCH"):
            canonical_field_order(COLUMNS[:3] + ["Fine Aggregate"] + COLUMNS[4:])
        with self.assertRaisesRegex(AssumptionViolation, "SCHEMA_MISMATCH"):
            canonical_field_order(COLUMNS[:-1] + ["Days not documented"])

    def test_missing_or_invalid_input_requires_abstention(self):
        X, y = make_synthetic()
        verify_source(X, y, COLUMNS)
        X_bad = X.copy()
        X_bad[0, 0] = -1
        with self.assertRaisesRegex(AssumptionViolation, "PHYSICALLY_INVALID_INPUT"):
            verify_source(X_bad, y, COLUMNS)
        X_bad = X.copy()
        X_bad[0, 7] = np.nan
        with self.assertRaisesRegex(AssumptionViolation, "INVALID_MEASUREMENT"):
            verify_source(X_bad, y, COLUMNS)
        X_bad = X.copy()
        X_bad[:, 7] = 7
        with self.assertRaisesRegex(AssumptionViolation, "AGE_SUPPORT_ABSENT"):
            verify_source(X_bad, y, COLUMNS)

    def test_pair_matching_is_label_blind_and_disjoint(self):
        X, y = make_synthetic()
        X_small = X[:32].copy()
        count1, pairs1 = choose_disjoint_pairs_from_features(X_small, 5.0)
        count2, pairs2 = choose_disjoint_pairs_from_features(X_small, 5.0)
        self.assertEqual((count1, pairs1), (count2, pairs2))
        self.assertEqual(len({i for pair in pairs1 for i in pair}), 2 * len(pairs1))
        a = score_descriptive_contrasts(X_small, y[:32], 5.0)
        b = score_descriptive_contrasts(X_small, -y[:32], 5.0)
        self.assertEqual(a["disjoint_paired_comparisons"], b["disjoint_paired_comparisons"])
        self.assertEqual(a["direction_matches_water_binder_expectation"],
                         b["direction_opposes_water_binder_expectation"])

    def test_identical_features_with_discordant_measurements(self):
        X, y = make_synthetic()
        X[1] = X[0]
        y[1] = y[0] + 4.0
        audit = audit_same_input_repeats(X, y)
        self.assertGreaterEqual(audit["groups_response_span_over_1_mpa"], 1)
        self.assertFalse(audit["measurement_noise_model_identified"])

    def test_decision_fails_closed_even_if_descriptive_pairs_exist(self):
        X, y = make_synthetic()
        report = analyze(X, y, COLUMNS, EXPECTED_PARSED_SHA256)
        self.assertEqual(report["decision"]["status"], "ABSTAIN_FROM_PHYSICAL_OR_LAB_RECOMMENDATION")
        self.assertFalse(report["evidence_boundaries"]["causal_identification"])
        self.assertFalse(report["evidence_boundaries"]["independent_holdout_used"])
        self.assertTrue(any(x["disjoint_paired_comparisons"] for x in report["matching_sensitivity"]))
        with self.assertRaisesRegex(AssumptionViolation, "SOURCE_VERSION_DRIFT"):
            analyze(X, y, COLUMNS, "wrong-fingerprint")

    def test_predeclared_matching_tolerances(self):
        X, _ = make_synthetic()
        with self.assertRaisesRegex(AssumptionViolation, "TOLERANCE_NOT_PREDECLARED"):
            choose_disjoint_pairs_from_features(X[:30], 12.3)

    def test_no_external_data_without_explicit_execute(self):
        from scripts.uci_concrete_assumptions_v6 import main
        self.assertEqual(main([]), 0)


if __name__ == "__main__":
    unittest.main()
