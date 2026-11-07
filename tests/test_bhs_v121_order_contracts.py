"""Source-independent v12.1 representation tests; no historical archive access."""
from __future__ import annotations

import inspect
import unittest

import numpy as np

from scripts.bhs_measurement_allocation_v12 import (
    INITIAL_MEASUREMENTS,
    POLICIES,
    TOTAL_MEASUREMENTS,
    MeasurementContractError,
    initial_geometry_ids,
)
from scripts.bhs_v121_order_contracts import (
    canonical_revealed_state,
    main,
    select_canonical_measurement,
)


def synthetic_pool(n=60):
    rng = np.random.default_rng(4021)
    descriptors = rng.normal(size=(n, 4))
    mean = 15 + descriptors[:, 0] * 3 - descriptors[:, 1] * 1.2
    repeated = mean[:, None] + np.array([-1.65, 0.27, 1.81])[None, :]
    return descriptors, repeated


def initial_observations(responses, seed):
    return {idx: tuple(map(float, responses[idx]))
            for idx in initial_geometry_ids(len(responses), seed)}


def permute_representation(observed, seed):
    rng = np.random.default_rng(seed)
    keys = list(observed)
    rng.shuffle(keys)
    return {
        idx: tuple(np.asarray(observed[idx])[rng.permutation(len(observed[idx]))].tolist())
        for idx in keys
    }


class RepresentationContracts(unittest.TestCase):
    def test_same_multisets_yield_exactly_same_first_action(self):
        features, responses = synthetic_pool()
        for seed in (7, 13):
            baseline = initial_observations(responses, seed)
            for policy in POLICIES:
                ref = select_canonical_measurement(
                    policy, features, baseline, seed=seed, step=0)
                for order_seed in (0, 1, 2, 3, 11, 19):
                    with self.subTest(seed=seed, policy=policy, order=order_seed):
                        alternative = permute_representation(baseline, order_seed)
                        self.assertEqual(
                            select_canonical_measurement(
                                policy, features, alternative, seed=seed, step=0),
                            ref,
                        )

    def test_partial_multisets_preserve_actions_not_temporal_histories(self):
        features, responses = synthetic_pool()
        for seed in (7, 13):
            initial = initial_observations(responses, seed)
            available = [i for i in range(len(features)) if i not in initial]
            # These values are synthetic already-revealed observations. Their
            # numerical identity remains constant while their order is changed.
            observed = dict(initial)
            observed[available[0]] = tuple(map(float, responses[available[0]][:2]))
            observed[available[1]] = (float(responses[available[1]][0]),)
            for policy in ("evidence_gate_development",):
                ref = select_canonical_measurement(
                    policy, features, observed, seed=seed, step=3)
                for order_seed in (0, 1, 2, 7, 23):
                    with self.subTest(seed=seed, policy=policy, order=order_seed):
                        other = permute_representation(observed, order_seed)
                        self.assertEqual(
                            select_canonical_measurement(
                                policy, features, other, seed=seed, step=3),
                            ref,
                        )

    def test_full_bundled_trajectories_preserve_design_choices(self):
        # The two scenarios differ only in how the same already revealed
        # complete observations are represented. They are not a simulation
        # of different physical acquisition time orders.
        features, responses = synthetic_pool()

        def trajectory(policy, seed, display_seed):
            rng = np.random.default_rng(display_seed)
            observed = initial_observations(responses, seed)
            picks = []
            for batch in range(10):
                displayed = permute_representation(observed, int(rng.integers(0, 1_000_000)))
                idx, ordinal = select_canonical_measurement(
                    policy, features, displayed, seed=seed, step=3 * batch)
                if idx in observed or ordinal != 1:
                    raise AssertionError("BUNDLED_REFERENCE_ACTION_CONTRACT_FAILED")
                picks.append(idx)
                observed[idx] = tuple(map(float, responses[idx]))
            self.assertEqual(sum(len(x) for x in observed.values()), TOTAL_MEASUREMENTS)
            return picks

        for policy in ("random_bundled", "gp_ard_bundled", "rf_ucb_bundled"):
            for seed in (7, 13):
                with self.subTest(policy=policy, seed=seed):
                    self.assertEqual(trajectory(policy, seed, 700),
                                     trajectory(policy, seed, 2801))

    def test_canonical_map_is_stable_and_does_not_mutate_input(self):
        features, responses = synthetic_pool()
        original = initial_observations(responses, 7)
        before = dict(original)
        cleaned = canonical_revealed_state(features, permute_representation(original, 9))
        self.assertEqual(original, before)
        self.assertEqual(list(cleaned), sorted(original))
        for key in original:
            self.assertEqual(cleaned[key], tuple(sorted(original[key])))

    def test_invalid_or_unseen_outcomes_are_refused(self):
        features, responses = synthetic_pool()
        observed = initial_observations(responses, 7)
        first = next(iter(observed))
        for invalid in ((1.0, 2.0, float("nan")), (1.0, 2.0, 3.0, 4.0)):
            forged = dict(observed)
            forged[first] = invalid
            with self.assertRaises(MeasurementContractError):
                canonical_revealed_state(features, forged)
        with self.assertRaises(MeasurementContractError):
            canonical_revealed_state(features, {True: (1.0, 2.0, 3.0), **observed})

    def test_budget_and_reserved_seed_restrictions_are_inherited(self):
        features, responses = synthetic_pool()
        observed = initial_observations(responses, 7)
        with self.assertRaises(MeasurementContractError):
            select_canonical_measurement("gp_ard_bundled", features, observed,
                                         seed=10000, step=0)
        with self.assertRaises(MeasurementContractError):
            select_canonical_measurement("gp_ard_bundled", features, observed,
                                         seed=7, step=TOTAL_MEASUREMENTS - INITIAL_MEASUREMENTS)

    def test_no_oracle_in_policy_signature(self):
        self.assertEqual(list(inspect.signature(select_canonical_measurement).parameters),
                         ["policy", "candidate_features", "observed", "seed", "step"])

    def test_import_does_not_run_real_source(self):
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
