"""Development-only source and selection-isolation tests for UCI concrete v5."""
import unittest

import numpy as np

from scripts.uci_concrete_v5 import (
    ADDITIONAL_ACQUISITIONS,
    INITIAL_OBSERVATIONS,
    POLICIES,
    choose_next,
    evaluate_development,
    main,
    require_development_seeds,
    run_campaign,
    scale_candidates,
    select_28_day_pool,
)


class ConcreteDevelopmentTests(unittest.TestCase):
    def test_seed_restrictions(self):
        require_development_seeds([7, 13, 23, 9999, 10100])
        for bad in (10000, 10054, 10099, -1, True):
            with self.assertRaises(ValueError):
                require_development_seeds([bad])
        with self.assertRaises(ValueError):
            require_development_seeds([])

    def test_fixed_age_pool_deduplicates_without_target_selection(self):
        X = np.zeros((1030, 8), dtype=float)
        X[:, -1] = 7.0
        X[:90, -1] = 28.0
        X[:70, 0] = np.arange(70)
        X[70:90, 0] = np.arange(20)
        y = np.linspace(2.0, 70.0, 1030)
        names = ["cement", "slag", "fly_ash", "water", "admixture",
                 "coarse_aggregate", "fine_aggregate", "Age"]
        selected, labels, info = select_28_day_pool(X, y, names)
        self.assertEqual(selected.shape, (70, 8))
        self.assertEqual(info["rows_age_28"], 90)
        self.assertEqual(info["repeat_profile_rows_excluded_by_features_only"], 20)
        y2 = y.copy()
        y2[70:90] = -1e6  # unselected replicate targets cannot change candidate pool
        selected2, labels2, _ = select_28_day_pool(X, y2, names)
        np.testing.assert_array_equal(selected, selected2)
        np.testing.assert_array_equal(labels, labels2)

    def test_label_isolation_and_unobserved_candidate_selection(self):
        rng = np.random.default_rng(3)
        X = scale_candidates(rng.normal(size=(29, 8)))
        selected = list(range(INITIAL_OBSERVATIONS))
        acquired = np.array([3.0, 4.1, 2.0, 3.2, 5.0, 1.7])
        for policy in POLICIES:
            a = choose_next(X, selected, acquired, policy, np.random.default_rng(12))
            b = choose_next(X, selected, acquired.copy(), policy, np.random.default_rng(12))
            self.assertEqual(a, b)
            self.assertNotIn(a, selected)
        with self.assertRaises(ValueError):
            choose_next(X, [0, 0], [2., 3.], "gp_ei", rng)
        with self.assertRaises(ValueError):
            choose_next(X, selected, acquired[:-1], "gp_ei", rng)

    def test_paired_campaigns_and_regret_nonnegative(self):
        rng = np.random.default_rng(23)
        X = rng.normal(size=(38, 8))
        y = X[:, 0] + 0.35 * X[:, 1] ** 2 - 0.25 * X[:, 2]
        X_std = scale_candidates(X)
        reports, aggregates = evaluate_development(X, y, seeds=(7,))
        self.assertEqual(len(reports), len(POLICIES))
        self.assertEqual(set(aggregates), set(POLICIES))
        for report in reports:
            self.assertEqual(
                report["unique_observations"],
                INITIAL_OBSERVATIONS + ADDITIONAL_ACQUISITIONS,
            )
            self.assertGreaterEqual(report["normalized_final_simple_regret"], 0.0)
            self.assertLessEqual(report["normalized_final_simple_regret"], 1.0)
            self.assertEqual(report, run_campaign(X_std, y, 7, report["policy"]))

    def test_no_fetch_without_explicit_execute(self):
        self.assertEqual(main([]), 0)


if __name__ == "__main__":
    unittest.main()
