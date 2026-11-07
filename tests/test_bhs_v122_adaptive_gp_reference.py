"""Source-independent noise-aware GP reference contracts, no source data."""
import inspect
import unittest

import numpy as np

from scripts.bhs_measurement_allocation_v12 import (
    INITIAL_MEASUREMENTS, REPEATS, TOTAL_MEASUREMENTS,
    MeasurementContractError, initial_geometry_ids,
)
from scripts.bhs_v122_adaptive_gp_reference import (
    REFERENCES, NOISE_CEILING, NOISE_FLOOR,
    _feasible_actions, fit_revealed_gp, pooled_noise_statistics,
    score_candidate_actions, select_gp_measurement, main,
)


def synthetic_data(n=32):
    rng = np.random.default_rng(331)
    X = rng.uniform(-0.9, 1.0, size=(n, 4))
    f = 2.3 * X[:, 0] + 1.1 * X[:, 1] * X[:, 1] - .4 * X[:, 2]
    Y = f[:, None] + rng.normal(0, .4, size=(n, REPEATS))
    return X, Y


def revealed(Y, seed):
    return {i: tuple(map(float, Y[i])) for i in initial_geometry_ids(len(Y), seed)}


def scramble_map(view, seed):
    rng = np.random.default_rng(seed)
    ids = list(view)
    rng.shuffle(ids)
    return {int(i): tuple(np.asarray(view[i])[rng.permutation(len(view[i]))].tolist()) for i in ids}


class AdaptiveReferenceTests(unittest.TestCase):
    def test_first_action_deterministic_under_identical_observed_evidence(self):
        X, Y = synthetic_data()
        for seed in (7, 13):
            view = revealed(Y, seed)
            for reference in REFERENCES:
                expected = select_gp_measurement(reference, X, view, seed=seed, step=0)
                for display_order in (0, 1, 3):
                    with self.subTest(seed=seed, method=reference, order=display_order):
                        self.assertEqual(expected, select_gp_measurement(
                            reference, X, scramble_map(view, display_order), seed=seed, step=0))
                self.assertEqual(expected[1], 1)
                self.assertNotIn(expected[0], view)

    def test_only_revealed_responses_affect_first_selection(self):
        X, Y = synthetic_data()
        view = revealed(Y, 7)
        changed_unseen = Y.copy()
        changed_unseen[[i for i in range(len(Y)) if i not in view]] += 10000
        # The selector receives no oracle argument; both views are identical.
        for reference in REFERENCES:
            a = select_gp_measurement(reference, X, view, seed=7, step=0)
            b = select_gp_measurement(reference, X, revealed(changed_unseen, 7), seed=7, step=0)
            self.assertEqual(a, b)

    def test_pending_designs_and_representational_order_are_valid(self):
        X, Y = synthetic_data()
        view = revealed(Y, 7)
        chosen, _ = select_gp_measurement(REFERENCES[0], X, view, seed=7, step=0)
        view[chosen] = (float(Y[chosen][0]),)
        for reference in REFERENCES:
            a = select_gp_measurement(reference, X, view, seed=7, step=1)
            b = select_gp_measurement(reference, X, scramble_map(view, 11), seed=7, step=1)
            self.assertEqual(a, b)
            self.assertIn(a[1], (1, 2))
            self.assertLessEqual(a[1], 3)

    def test_fixed_budget_and_no_partial_endpoints(self):
        X, Y = synthetic_data()
        for reference in REFERENCES:
            view = revealed(Y, 7)
            trace = []
            for step in range(TOTAL_MEASUREMENTS - INITIAL_MEASUREMENTS):
                idx, ordinal = select_gp_measurement(reference, X, view, seed=7, step=step)
                self.assertEqual(ordinal, len(view.get(idx, ())) + 1)
                self.assertLessEqual(ordinal, 3)
                view[idx] = view.get(idx, ()) + (float(Y[idx][ordinal - 1]),)
                trace.append((idx, ordinal))
                self.assertLessEqual(sum(len(v) < 3 for v in view.values()), 3)
                self.assertEqual(sum(map(len, view.values())), INITIAL_MEASUREMENTS + step + 1)
            with self.subTest(method=reference):
                self.assertEqual(sum(map(len, view.values())), 48)
                self.assertEqual(len(view), 16)
                self.assertTrue(all(len(vals) == 3 for vals in view.values()))
                self.assertTrue(any(j >= 2 for _, j in trace))

    def test_noise_variance_uses_only_acquired_replicates(self):
        X, Y = synthetic_data()
        view = revealed(Y, 7)
        _, _, variance = pooled_noise_statistics(view)
        model, diag, _ = fit_revealed_gp(X, view)
        self.assertGreaterEqual(variance, NOISE_FLOOR)
        self.assertLessEqual(variance, NOISE_CEILING)
        self.assertEqual(diag.observed_measurements, INITIAL_MEASUREMENTS)
        self.assertAlmostEqual(diag.alpha_min, variance / 3)
        new_idx = next(i for i in range(len(X)) if i not in view)
        view[new_idx] = (float(Y[new_idx][0]),)
        _, diag2, _ = fit_revealed_gp(X, view)
        self.assertAlmostEqual(diag2.alpha_max, diag2.pooled_noise_variance_standardized)
        self.assertTrue(hasattr(model, "predict"))

    def test_exact_variance_reduction_formula_and_cost_discount(self):
        X, Y = synthetic_data(16)
        view = revealed(Y, 7)
        model, diag, incumbent = fit_revealed_gp(X, view)
        n = len(X)
        available = np.asarray([i for i in range(n) if i not in view], dtype=int)
        scores = score_candidate_actions(model, X, available, view,
                                         diag.pooled_noise_variance_standardized,
                                         incumbent, REFERENCES[0])
        _, cov = model.predict(X, return_cov=True)
        var = np.maximum(0, np.diag(cov)[available])
        manual = ((cov[:, available] ** 2).sum(axis=0) /
                  (var + diag.pooled_noise_variance_standardized) / 3)
        np.testing.assert_allclose(scores, manual, atol=1e-10, rtol=1e-9)
        self.assertTrue(np.all(scores >= 0.0))

    def test_rejects_forbidden_seeds_invalid_steps_and_fake_observations(self):
        X, Y = synthetic_data()
        view = revealed(Y, 7)
        invalid_cases = [
            (REFERENCES[0], view, 10000, 0),
            (REFERENCES[0], view, 7, 1),
            (REFERENCES[0], view, 7, 30),
            ("unknown", view, 7, 0),
            (REFERENCES[0], dict(view, **{}), 7, 0),
        ]
        for policy, obs, seed, step in invalid_cases[:-1]:
            with self.subTest(seed=seed, step=step, method=policy):
                with self.assertRaises(MeasurementContractError):
                    select_gp_measurement(policy, X, obs, seed=seed, step=step)
        bad = dict(view)
        i = next(iter(bad))
        bad[i] = (float('nan'), 0.0, 1.0)
        with self.assertRaises(MeasurementContractError):
            select_gp_measurement(REFERENCES[0], X, bad, seed=7, step=0)

    def test_infeasible_pending_capacity_rejected(self):
        X, Y = synthetic_data()
        view = revealed(Y, 7)
        pending = [i for i in range(len(X)) if i not in view][:3]
        for i in pending:
            view[i] = (float(Y[i, 0]),)
        with self.assertRaises(MeasurementContractError):
            _feasible_actions(len(X), view, pending, TOTAL_MEASUREMENTS - 5)
        eligible = _feasible_actions(len(X), view, pending, INITIAL_MEASUREMENTS + 3)
        self.assertEqual(list(eligible), pending)

    def test_all_complete_reference_rejects_budget_exhaustion(self):
        X, Y = synthetic_data()
        view = revealed(Y, 7)
        with self.assertRaises(MeasurementContractError):
            select_gp_measurement(REFERENCES[0], X, view, seed=7, step=True)
        # The selector explicitly does not accept arrays of hidden raw outcomes.
        self.assertEqual(list(inspect.signature(select_gp_measurement).parameters),
                         ["reference", "candidate_features", "observed", "seed", "step"])
        self.assertEqual(main(), 0)

    def test_canonical_values_do_not_mutate_caller_map(self):
        X, Y = synthetic_data()
        view = revealed(Y, 7)
        snapshot = {k: tuple(v) for k, v in view.items()}
        select_gp_measurement(REFERENCES[0], X, view, seed=7, step=0)
        self.assertEqual(view, snapshot)


if __name__ == '__main__':
    unittest.main()
