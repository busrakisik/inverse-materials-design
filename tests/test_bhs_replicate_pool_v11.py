"""Replicate/group budget isolation contracts for BHS v11 research development."""
import inspect
import unittest
from unittest.mock import patch

import numpy as np

from scripts.bhs_replicate_pool_v11 import (
    ADDITIONAL, INITIAL, POLICIES, REPLICATES, SEEDS,
    SelectionContractError, check_acquisition_view, group_source,
    initial_geometries, main, run_campaign, run_development, select_next,
)
from scripts.bhs_replicate_leakage_v10 import validate_measurements


def simple_pool(n=40):
    rng = np.random.default_rng(42)
    X = rng.normal(size=(n, 4))
    # These are explicitly synthetic, not physical measurements or validated noise.
    truth = 10.0 + 3.0 * X[:, 0] - 1.5 * X[:, 1] ** 2
    samples = truth[:, None] + np.array([-0.5, 0.0, 0.5])[None, :]
    return X, samples


class PoolAcquisitionV11Contracts(unittest.TestCase):
    def test_source_has_600_distinct_geometries_and_complete_triplicates(self):
        X = []
        y = []
        for i in range(600):
            for noise in (-1.0, 0.0, 1.0):
                X.append([6 + i % 4, i // 4, 2.0, 0.8])
                y.append(12.0 + (i % 23) / 2 + noise)
        X, y, group = validate_measurements(np.asarray(X), np.asarray(y))
        standardized, triplicates = group_source(X, y, group)
        self.assertEqual(standardized.shape, (600, 4))
        self.assertEqual(triplicates.shape, (600, 3))
        self.assertEqual(len(np.unique(group)), 600)

    def test_frozen_paired_initial_design_ids(self):
        a = initial_geometries(600, 7)
        b = initial_geometries(600, 7)
        self.assertEqual(a, b)
        self.assertEqual(len(set(a)), INITIAL)
        for policy in POLICIES:
            _, hidden = simple_pool()
            row = run_campaign(*simple_pool(), policy, 7, acquisitions=0)
            self.assertEqual(row["total_distinct_designs_acquired"], INITIAL)

    def test_selections_never_repeat_and_count_3_replicates_each(self):
        X, oracle = simple_pool()
        for policy in POLICIES:
            with self.subTest(policy=policy):
                result = run_campaign(X, oracle, policy, 7, acquisitions=2)
                self.assertEqual(result["total_distinct_designs_acquired"], INITIAL+2)
                self.assertEqual(result["historical_measured_rows_revealed"], (INITIAL+2)*3)
                self.assertTrue(result["triplicate_group_integrity"])
                self.assertFalse(result["unobserved_replicates_used_by_policy"])
                self.assertFalse(result["global_optimum_used_by_policy"])
                self.assertGreaterEqual(result["final_simple_regret_against_noisy_pool_best_j"], 0.0)

    def test_selector_api_does_not_accept_oracle_or_full_labels(self):
        params = inspect.signature(select_next).parameters
        self.assertEqual(list(params), [
            "policy", "candidate_features", "acquired_ids",
            "acquired_triplicates", "seed", "step"
        ])
        X, oracle = simple_pool()
        selected = initial_geometries(len(X), 7)
        revealed = oracle[list(selected)].copy()
        for policy in POLICIES:
            a = select_next(policy, X, selected, revealed, seed=7, step=0)
            changed_hidden = oracle.copy()
            remaining = sorted(set(range(len(X))) - set(selected))
            changed_hidden[remaining] += 1000000.0
            b = select_next(policy, X, selected, changed_hidden[list(selected)],
                            seed=7, step=0)
            self.assertEqual(a, b)
            self.assertNotIn(a, selected)

    def test_existing_bhs_selector_used_unchanged(self):
        X, oracle = simple_pool()
        selected = initial_geometries(len(X), 7)
        triplicates = oracle[list(selected)]
        expected_means = triplicates.mean(axis=1)
        def spy(features, acquired_ids, observed, policy, rng):
            self.assertEqual(policy, "kernel_portfolio_ei")
            np.testing.assert_array_equal(observed, expected_means)
            self.assertEqual(list(acquired_ids), list(selected))
            return 0 if 0 not in selected else 1
        with patch("scripts.bhs_replicate_pool_v11.existing_bhs_v5_selector", side_effect=spy) as p:
            next_id = select_next("bhs_v5_kernel_portfolio_ei", X, selected,
                                  triplicates, seed=7, step=0)
            self.assertEqual(p.call_count, 1)
            self.assertNotIn(next_id, selected)

    def test_triplicate_is_indivisible(self):
        X, hidden = simple_pool()
        initial = initial_geometries(len(X), 7)
        with self.assertRaisesRegex(SelectionContractError, "THREE_PER_ACQUIRED"):
            select_next("random", X, initial, hidden[list(initial), :2], seed=7, step=0)

    def test_invalid_and_duplicate_design_ids_refused(self):
        X, hidden = simple_pool()
        initial = list(initial_geometries(len(X), 7))
        initial[-1] = initial[0]
        with self.assertRaisesRegex(SelectionContractError, "INVALID_ACQUIRED_DESIGN"):
            check_acquisition_view(X, initial, hidden[initial])

    def test_selection_with_no_unseen_candidates_fails(self):
        X, hidden = simple_pool(16)
        with self.assertRaisesRegex(SelectionContractError, "NO_UNOBSERVED_DESIGNS"):
            select_next("random", X, list(range(len(X))), hidden, seed=7, step=0)

    def test_strict_budget_never_exceeds_protocol(self):
        X, hidden = simple_pool()
        with self.assertRaisesRegex(SelectionContractError, "UNEXPECTED_POLICY_OR_BUDGET"):
            run_campaign(X, hidden, "random", 7, acquisitions=ADDITIONAL + 1)

    def test_holdout_seed_guard(self):
        X, hidden = simple_pool()
        for seed in (-1, 10000, 10043, 10099):
            with self.assertRaises(ValueError):
                run_campaign(X, hidden, "random", seed, acquisitions=0)

    def test_acquisition_replay_deterministic(self):
        X, hidden = simple_pool()
        for policy in POLICIES:
            a = run_campaign(X, hidden, policy, 7, acquisitions=2)
            b = run_campaign(X, hidden, policy, 7, acquisitions=2)
            self.assertEqual(a, b)

    def test_benchmark_result_cannot_claim_superiority_from_altered_seed_list(self):
        X, hidden = simple_pool(600)
        with self.assertRaisesRegex(SelectionContractError, "ONLY_FROZEN"):
            run_development(X, hidden, seeds=(7,13,23))

    def test_no_real_source_download_without_execute(self):
        self.assertEqual(main([]), 0)


if __name__ == "__main__":
    unittest.main()
