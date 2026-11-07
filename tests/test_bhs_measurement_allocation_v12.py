"""Synthetic contract tests for the v12 one-response-per-action replay."""
import inspect
import unittest

import numpy as np

from scripts.bhs_measurement_allocation_v12 import (
    POLICIES, TOTAL_MEASUREMENTS, MeasurementContractError,
    acquisition_view, build_report, initial_geometry_ids, main,
    require_development_seed, run_campaign, run_development,
    select_measurement, HistoricalMeasurementOracle,
)


def synthetic_pool(n=50):
    rng = np.random.default_rng(204)
    X = rng.normal(size=(n, 4))
    signal = 25.0 + 4.0 * X[:, 0] - 2.0 * X[:, 1]
    triples = signal[:, None] + np.array([-1.2, 0.2, 1.0])[None, :]
    return X, triples


def init_observed(triples, seed=7):
    obs = {}
    for idx in initial_geometry_ids(len(triples), seed):
        obs[idx] = tuple(map(float, triples[idx]))
    return obs


class MeasurementLevelContracts(unittest.TestCase):
    def test_initial_designs_pair_across_policies(self):
        a = initial_geometry_ids(50, 7)
        self.assertEqual(a, initial_geometry_ids(50, 7))
        self.assertEqual(len(a), 6)
        self.assertEqual(len(set(a)), 6)
        for policy in POLICIES:
            X, triples = synthetic_pool()
            row = run_campaign(X, triples, policy, 7, budget=18)
            self.assertEqual(row['distinct_geometries_seen'], 6)
            self.assertEqual(row['completely_measured_geometries'], 6)
            self.assertEqual(row['historical_measurements_revealed'], 18)

    def test_shared_initial_designs_cannot_be_replaced_in_a_policy_view(self):
        X, triples = synthetic_pool()
        observed = init_observed(triples)
        missing = next(iter(observed))
        observed.pop(missing)
        replacement = next(i for i in range(len(X)) if i not in observed)
        observed[replacement] = tuple(map(float, triples[replacement]))
        with self.assertRaisesRegex(MeasurementContractError, "FROZEN_SHARED_INITIAL"):
            select_measurement("gp_ard_bundled", X, observed, seed=7, step=0)

    def test_no_full_oracle_or_hidden_labels_in_selector_signature(self):
        self.assertEqual(list(inspect.signature(select_measurement).parameters), [
            'policy', 'candidate_features', 'observed', 'seed', 'step'
        ])

    def test_one_action_reveals_one_observation(self):
        X, triples = synthetic_pool()
        obs = init_observed(triples)
        for policy in POLICIES:
            first_id, ordinal = select_measurement(policy, X, obs, seed=7, step=0)
            self.assertEqual(ordinal, 1)
            self.assertNotIn(first_id, obs)
            seen = dict(obs)
            seen[first_id] = (float(triples[first_id, 0]),)
            if policy.endswith('_bundled'):
                nxt_id, nxt_ordinal = select_measurement(policy, X, seen, seed=7, step=1)
                self.assertEqual((nxt_id, nxt_ordinal), (first_id, 2))

    def test_altering_unrevealed_values_cannot_change_first_decision(self):
        X, triples = synthetic_pool()
        init = init_observed(triples)
        unseen = sorted(set(range(len(X))) - set(init))
        altered = triples.copy()
        altered[unseen, :] += 1e8
        self.assertTrue(all(np.array_equal(triples[i], altered[i]) for i in init))
        for policy in POLICIES:
            a = select_measurement(policy, X, init, seed=7, step=0)
            b = select_measurement(policy, X.copy(), init_observed(altered), seed=7, step=0)
            self.assertEqual(a, b)

    def test_repeat_gate_uses_only_exposed_one_measurement(self):
        X, triples = synthetic_pool()
        obs = init_observed(triples)
        new = sorted(set(range(len(X))) - set(obs))[0]
        obs[new] = (1_000.0,)  # deliberately synthetic near-certain candidate trigger
        self.assertEqual(select_measurement(
            'evidence_gate_development', X, obs, seed=7, step=1
        ), (new, 2))
        obs[new] = (1_000.0, 1_001.0)
        self.assertEqual(select_measurement(
            'evidence_gate_development', X, obs, seed=7, step=2
        ), (new, 3))

    def test_exact_budget_and_recommendation_only_from_complete_designs(self):
        X, triples = synthetic_pool()
        for policy in POLICIES:
            with self.subTest(policy=policy):
                r = run_campaign(X, triples, policy, 7, budget=24)
                self.assertEqual(r['historical_measurements_revealed'], 24)
                self.assertGreaterEqual(r['completely_measured_geometries'], 6)
                self.assertGreaterEqual(r['regret_j'], 0.0)
                self.assertTrue(r['recommendation_complete_triplicates_only'])
                self.assertTrue(r['recommended_uses_all_three_observations'])
                self.assertTrue(r['all_unrevealed_measurements_hidden_from_policy'])
                self.assertEqual(r['historical_measurements_revealed'],
                                 3*r['completely_measured_geometries'] +
                                 r['partially_measured_response_count'])

    def test_original_triplicates_permuted_deterministically(self):
        _, triples = synthetic_pool()
        a, b = HistoricalMeasurementOracle(triples, 7), HistoricalMeasurementOracle(triples, 7)
        for idx in (0, 1, 3):
            observations_a = [a.reveal_one(idx, j) for j in range(1, 4)]
            observations_b = [b.reveal_one(idx, j) for j in range(1, 4)]
            self.assertEqual(observations_a, observations_b)
            self.assertAlmostEqual(sum(observations_a), float(np.sum(triples[idx])))

    def test_hard_seed_prohibition(self):
        for seed in (-1, 10000, 10099, True, 3.0):
            with self.assertRaises(MeasurementContractError):
                require_development_seed(seed)

    def test_no_actions_after_budget_exhaustion(self):
        X, triples = synthetic_pool()
        initial = list(initial_geometry_ids(len(X), 7))
        extras = [i for i in range(len(X)) if i not in initial][:10]
        obs = {i: tuple(map(float, triples[i])) for i in initial + extras}
        with self.assertRaisesRegex(MeasurementContractError, 'BUDGET_EXHAUSTED'):
            select_measurement('random_bundled', X, obs, seed=7,
                               step=TOTAL_MEASUREMENTS-18)

    def test_hidden_outcome_structure_not_in_public_view(self):
        X, triples = synthetic_pool()
        obs = init_observed(triples)
        with self.assertRaises(MeasurementContractError):
            acquisition_view(X, {i: tuple(triples[i]) for i in range(5)})
        obs[next(iter(obs))] = (1.0, 2.0, 3.0, 4.0)
        with self.assertRaisesRegex(MeasurementContractError, 'INVALID_OBSERVED_REPLICATE_COUNT'):
            acquisition_view(X, obs)

    def test_bundled_policy_refuses_multiple_partial_candidates(self):
        X, triples = synthetic_pool()
        obs = init_observed(triples)
        unseen = sorted(set(range(len(X))) - set(obs))[:2]
        obs[unseen[0]] = (25.0,)
        obs[unseen[1]] = (26.0,)
        with self.assertRaisesRegex(MeasurementContractError, 'MULTIPLE_PARTIALS'):
            select_measurement('gp_ard_bundled', X, obs, seed=7, step=2)

    def test_invalid_budget_fails_closed(self):
        X, triples = synthetic_pool()
        for budget in (17, 49, 10000, True):
            with self.assertRaises(MeasurementContractError):
                run_campaign(X, triples, 'random_bundled', 7, budget=budget)

    def test_compact_result_does_not_expose_rows_ids_or_raw_triplicates(self):
        X, triples = synthetic_pool()
        r = run_campaign(X, triples, 'random_bundled', 7, budget=21)
        forbidden = ('measurements', 'selected_ids', 'triplicates', 'coordinates', 'features')
        self.assertFalse(any(k in r for k in forbidden))
        self.assertEqual(r['historical_measurements_revealed'], 21)
        self.assertEqual(r['partially_measured_geometries'], 0)

    def test_no_replay_just_from_import_or_cli(self):
        self.assertEqual(main([]), 0)

    def test_immutable_source_hash_fails_before_loading_old_modules(self):
        with self.assertRaisesRegex(MeasurementContractError, 'PINNED_SOURCE_SHA256_MISMATCH'):
            build_report(b'not the pinned raw source')

    def test_source_protocol_cannot_be_relabelled_as_new_holdout(self):
        X, triples = synthetic_pool(600)
        with self.assertRaisesRegex(MeasurementContractError, 'UNAUTHORIZED_CHANGE'):
            run_development(X, triples, seeds=(7,13))
        with self.assertRaisesRegex(MeasurementContractError, 'UNAUTHORIZED_CHANGE'):
            run_development(X, triples, policies=('random_bundled',))

    def test_two_campaigns_reproduce_same_development_actions(self):
        X, triples = synthetic_pool()
        a = run_campaign(X, triples, 'evidence_gate_development', 7, budget=22)
        b = run_campaign(X, triples, 'evidence_gate_development', 7, budget=22)
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
