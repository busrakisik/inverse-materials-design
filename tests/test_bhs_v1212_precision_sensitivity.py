"""Independent exact-coefficient checks for conditional, outcome-free V12.12."""
import copy
import unittest
from fractions import Fraction
from pathlib import Path

from scripts.bhs_v1212_precision_sensitivity import (
    conditional_variance, evaluate, load_frozen, paired_coefficients,
)

ROOT = Path(__file__).resolve().parents[1]


class PrecisionSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenarios = load_frozen(ROOT)
        cls.report = evaluate(ROOT)

    def coefficient(self, name, key):
        return Fraction(self.report["findings"][name]["full"]["coefficients"][key])

    def test_four_schedules_have_eight_pairs(self):
        self.assertEqual(len(self.scenarios), 4)
        self.assertTrue(all(paired_coefficients(v)["complete_pairs"] == 8 for v in self.scenarios.values()))

    def test_shared_source_run_cancels_only_for_coupon_treatment(self):
        self.assertEqual(self.coefficient("v1210/postdeposition_coupon", "run"), 0)
        self.assertEqual(self.coefficient("v1210/deposition_run", "run"), Fraction(1, 4))

    def test_coupon_and_trace_components_use_coupons_not_scans(self):
        for name in self.scenarios:
            self.assertEqual(self.coefficient(name, "coupon"), Fraction(1, 4))
            self.assertEqual(self.coefficient(name, "trace"), Fraction(1, 12))

    def test_complete_schedules_have_balanced_session_offsets(self):
        for name in self.scenarios:
            self.assertEqual(self.coefficient(name, "session"), 0)

    def test_one_session_loss_cross_session_has_no_complete_pairs(self):
        x = self.report["findings"]["v129/cross_session_pairs"]["loss_one_session"]["results"]
        self.assertEqual([r["complete_pairs"] for r in x], [0, 0])
        self.assertTrue(all(r["status"] == "NOT_ESTIMABLE" for r in x))

    def test_one_session_loss_within_session_keeps_four_pairs(self):
        x = self.report["findings"]["v129/within_session_pairs"]["loss_one_session"]["results"]
        self.assertEqual([r["complete_pairs"] for r in x], [4, 4])
        self.assertTrue(all(Fraction(r["coefficients"]["session"]) == 0 for r in x))

    def test_all_single_block_losses_reduce_to_seven_pairs(self):
        for scenario in self.report["findings"].values():
            vals = scenario["loss_one_matched_block"]["results"]
            self.assertEqual(len(vals), 8)
            self.assertTrue(all(v["complete_pairs"] == 7 for v in vals))

    def test_cross_session_single_pair_loss_reintroduces_session_noise(self):
        rows = self.report["findings"]["v129/cross_session_pairs"]["loss_one_matched_block"]["results"]
        self.assertTrue(all(Fraction(r["coefficients"]["session"]) == Fraction(2, 49) for r in rows))
        rows = self.report["findings"]["v129/within_session_pairs"]["loss_one_matched_block"]["results"]
        self.assertTrue(all(Fraction(r["coefficients"]["session"]) == 0 for r in rows))

    def test_run_variance_changes_conditional_sd_not_data(self):
        post = self.report["findings"]["v1210/postdeposition_coupon"]["full"]["coefficients"]
        dep = self.report["findings"]["v1210/deposition_run"]["full"]["coefficients"]
        self.assertEqual(conditional_variance(post, 2, 0) * 3, 1)
        self.assertAlmostEqual(conditional_variance(dep, 2, 0), 4/3, places=14)

    def test_invariance_row_order_and_renaming(self):
        rows = copy.deepcopy(self.scenarios["v1210/deposition_run"])
        expected = paired_coefficients(rows)
        for row in rows:
            row["coupon_id"] = "renamed-" + row["coupon_id"]
            row["source_deposition_run_id"] = "other-" + row["source_deposition_run_id"]
        self.assertEqual(paired_coefficients(list(reversed(rows))), expected)

    def test_duplicate_coupon_fails_closed(self):
        rows = copy.deepcopy(self.scenarios["v1210/deposition_run"])
        rows[1]["coupon_id"] = rows[0]["coupon_id"]
        with self.assertRaisesRegex(ValueError, "BAD_COUPON_ID"):
            paired_coefficients(rows)

    def test_invalid_trace_count_fails_closed(self):
        rows = copy.deepcopy(self.scenarios["v1210/deposition_run"])
        rows[0]["planned_moke_traces"] = 0
        with self.assertRaisesRegex(ValueError, "INVALID_TRACE_COUNT"):
            paired_coefficients(rows)

    def test_bad_noise_scale_rejected(self):
        x = self.report["findings"]["v1210/deposition_run"]["full"]["coefficients"]
        with self.assertRaises(ValueError):
            conditional_variance(x, -1, 0)


if __name__ == "__main__":
    unittest.main()
