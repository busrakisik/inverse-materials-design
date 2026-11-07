"""V12.4 source-independent adversarial measurement and decision contracts."""
from __future__ import annotations

from dataclasses import replace
import inspect
import unittest
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning

from scripts.bhs_measurement_allocation_v12 import (
    INITIAL_MEASUREMENTS, TOTAL_MEASUREMENTS, REPEATS,
    MeasurementContractError, initial_geometry_ids,
)
from scripts.bhs_v123_synthetic_decision_audit import choose_action
from scripts.bhs_v124_completion_coverage_audit import (
    SOURCE_SEED, NOISE_SEED, POOL_SIZE, SEEDS, ORDER_VARIANTS,
    LANDSCAPES, REGIMES, POLICIES, MATCHED_POLICIES,
    ABSTENTION_Z, ABSTENTION_PENALTIES, PRIMARY_Z, PRIMARY_PENALTY,
    HARD_GATES, _observed_summary, completion_filter, propose_action,
    make_source, PrivateManufacturedOracle, run_campaign, main,
)


class CompletionAndAbstentionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings("ignore", category=ConvergenceWarning)

    def test_fixed_source_and_protocol_constants(self):
        self.assertEqual((SOURCE_SEED, NOISE_SEED, POOL_SIZE), (48121, 79331, 48))
        self.assertEqual(SEEDS, (19, 29))
        self.assertEqual(ORDER_VARIANTS, (0, 1))
        self.assertEqual(LANDSCAPES, ("ridge", "oscillatory"))
        self.assertEqual(REGIMES, ("constant", "varying"))
        self.assertEqual(len(POLICIES), 6)
        self.assertEqual(len(MATCHED_POLICIES), 5)
        self.assertEqual((ABSTENTION_Z, ABSTENTION_PENALTIES),
                         ((0.0, 1.0, 1.645), (0.25, 0.50, 1.0)))
        self.assertEqual((PRIMARY_Z, PRIMARY_PENALTY), (1.0, .5))
        self.assertTrue(HARD_GATES["development_only"])
        self.assertTrue(all(v is False for k, v in HARD_GATES.items()
                            if k != "development_only"))

    def test_source_deterministic_and_distinct_landscapes(self):
        a = make_source("ridge", "constant")
        b = make_source("ridge", "constant")
        c = make_source("oscillatory", "constant")
        self.assertEqual(a.digest, b.digest)
        np.testing.assert_array_equal(a.latent, b.latent)
        np.testing.assert_array_equal(a.outcomes, b.outcomes)
        np.testing.assert_array_equal(a.descriptors, c.descriptors)
        self.assertFalse(np.array_equal(a.latent, c.latent))
        self.assertTrue(np.isfinite(a.outcomes).all())
        with self.assertRaises(MeasurementContractError):
            make_source("not-a-landscape", "constant")
        with self.assertRaises(MeasurementContractError):
            make_source("ridge", "not-a-noise-model")

    def test_noise_regimes_share_underlying_standard_normal(self):
        a = make_source("ridge", "constant")
        b = make_source("ridge", "varying")
        np.testing.assert_array_equal(a.latent, b.latent)
        np.testing.assert_allclose(
            (a.outcomes-a.latent[:, None])/.35,
            (b.outcomes-b.latent[:, None]) / (
                .15+.55*(a.descriptors[:, 0]+1)/2)[:, None], atol=1e-12)

    def test_response_order_permutations_preserve_complete_multisets(self):
        src = make_source("ridge", "varying")
        a = PrivateManufacturedOracle(src, 19, 0)
        b = PrivateManufacturedOracle(src, 19, 1)
        changed = 0
        for i in range(POOL_SIZE):
            values_a = [a.reveal(i, j) for j in (1, 2, 3)]
            values_b = [b.reveal(i, j) for j in (1, 2, 3)]
            np.testing.assert_array_equal(sorted(values_a), sorted(values_b))
            changed += int(values_a != values_b)
        self.assertGreater(changed, 0)

    def test_private_oracle_use_once_and_order_enforced(self):
        oracle = PrivateManufacturedOracle(make_source("ridge", "constant"), 19, 0)
        with self.assertRaisesRegex(MeasurementContractError, "SKIPPED"):
            oracle.reveal(0, 2)
        first = oracle.reveal(0, 1)
        self.assertTrue(np.isfinite(first))
        with self.assertRaisesRegex(MeasurementContractError, "USED"):
            oracle.reveal(0, 1)
        for invalid in ((True, 1), (0, True), (-1, 1), (48, 1), (0, 4)):
            with self.subTest(req=invalid):
                with self.assertRaises(MeasurementContractError):
                    oracle.reveal(*invalid)
        with self.assertRaises(MeasurementContractError):
            PrivateManufacturedOracle(make_source("ridge", "constant"), 10000, 0)
        with self.assertRaises(MeasurementContractError):
            PrivateManufacturedOracle(make_source("ridge", "constant"), 19, 3)

    def test_evaluator_rejects_forged_and_partial_transcripts(self):
        oracle = PrivateManufacturedOracle(make_source("ridge", "constant"), 19, 0)
        v = oracle.reveal(0, 1)
        with self.assertRaisesRegex(MeasurementContractError, "ID_MISMATCH"):
            oracle.evaluate({})
        with self.assertRaisesRegex(MeasurementContractError, "VALUE_MISMATCH"):
            oracle.evaluate({0: (v+10,)})
        with self.assertRaisesRegex(MeasurementContractError, "VALUE_MISMATCH"):
            oracle.evaluate({0: (v, v)})
        with self.assertRaisesRegex(MeasurementContractError, "BUDGET_MISMATCH"):
            oracle.evaluate({0: (v,)})

    def test_oracle_copies_hidden_source_measurements(self):
        src = make_source("ridge", "constant")
        expected = np.sort(src.outcomes[0].copy())
        oracle = PrivateManufacturedOracle(src, 19, 0)
        src.outcomes[0] = 1e10
        np.testing.assert_array_equal(
            np.sort([oracle.reveal(0, j) for j in (1, 2, 3)]), expected)

    def test_common_evidence_filter_margin_and_noise(self):
        observed = {i: (float(i), float(i)+.2, float(i)-.2)
                    for i in range(6)}
        best, margin, se = _observed_summary(observed)
        self.assertEqual(best, 5)
        self.assertAlmostEqual(margin, 1.0)
        self.assertGreater(se, 0)
        observed[5] = (float("nan"), 5.2, 4.8)
        with self.assertRaises(MeasurementContractError):
            _observed_summary(observed)

    def test_common_evidence_filter_fails_closed_without_completed_designs(self):
        with self.assertRaisesRegex(MeasurementContractError, "NO_COMPLETED"):
            _observed_summary({0: (1.0,), 1: (2.0, 2.1)})

    def test_completion_guard_allows_new_design_when_budget_sufficient(self):
        source = make_source("ridge", "constant")
        ids = initial_geometry_ids(POOL_SIZE, 19)
        observed = {i: tuple(map(float, source.outcomes[i])) for i in ids}
        fresh = next(i for i in range(POOL_SIZE) if i not in observed)
        self.assertEqual(completion_filter((fresh, 1), observed,
                                           step=0, n=POOL_SIZE), (fresh, 1, False))

    def test_completion_guard_picks_pending_at_capacity(self):
        source = make_source("ridge", "constant")
        ids = initial_geometry_ids(POOL_SIZE, 19)
        observed = {i: tuple(map(float, source.outcomes[i])) for i in ids}
        extras = [i for i in range(POOL_SIZE) if i not in observed][:4]
        observed[extras[0]] = (0.0,)
        observed[extras[1]] = (3.0, 3.1)
        observed[extras[2]] = (2.0,)
        self.assertEqual(sum(map(len, observed.values())), 22)
        self.assertEqual(
            completion_filter((extras[3], 1), observed, step=4, n=POOL_SIZE),
            (extras[1], 3, True))

    def test_completion_guard_reserves_end_of_budget(self):
        # Valid state at one action left: 15 triplicates and one double.
        source = make_source("ridge", "constant")
        ids = initial_geometry_ids(POOL_SIZE, 19)
        observed = {i: tuple(map(float, source.outcomes[i])) for i in ids}
        others = [i for i in range(POOL_SIZE) if i not in observed][:10]
        for i in others[:9]:
            observed[i] = tuple(map(float, source.outcomes[i]))
        observed[others[9]] = tuple(map(float, source.outcomes[others[9]][:2]))
        self.assertEqual(sum(map(len, observed.values())), 47)
        new = next(i for i in range(POOL_SIZE) if i not in observed)
        self.assertEqual(
            completion_filter((new, 1), observed, step=29, n=POOL_SIZE),
            (others[9], 3, True))

    def test_completion_guard_rejects_inconsistent_step_or_bad_action(self):
        source = make_source("ridge", "constant")
        initial = initial_geometry_ids(POOL_SIZE, 19)
        observed = {i: tuple(map(float, source.outcomes[i])) for i in initial}
        with self.assertRaises(MeasurementContractError):
            completion_filter((0, 1), observed, step=1, n=POOL_SIZE)
        with self.assertRaises(MeasurementContractError):
            completion_filter((True, 1), observed, step=0, n=POOL_SIZE)
        first = initial[0]
        with self.assertRaises(MeasurementContractError):
            completion_filter((first, 4), observed, step=0, n=POOL_SIZE)

    def test_policy_uses_only_acquired_inputs(self):
        self.assertEqual(list(inspect.signature(propose_action).parameters),
                         ["policy", "descriptors", "observed", "seed", "step"])
        src = make_source("ridge", "constant")
        initial = initial_geometry_ids(POOL_SIZE, 19)
        view = {i: tuple(map(float, src.outcomes[i])) for i in initial}
        mutated = src.outcomes.copy()
        mutated[[i for i in range(POOL_SIZE) if i not in view]] += 1234.0
        other = replace(src, outcomes=mutated)
        view2 = {i: tuple(map(float, other.outcomes[i])) for i in initial}
        for policy in POLICIES:
            with self.subTest(policy=policy):
                a = propose_action(policy, src.descriptors, view, seed=19, step=0)
                b = propose_action(policy, other.descriptors, view2, seed=19, step=0)
                self.assertEqual(a, b)

    def test_native_gate_same_first_action_as_original_selector(self):
        src = make_source("ridge", "constant")
        initial = initial_geometry_ids(POOL_SIZE, 19)
        view = {i: tuple(map(float, src.outcomes[i])) for i in initial}
        baseline = choose_action("evidence_gate_development", src.descriptors,
                                 view, seed=19, step=0)
        self.assertEqual(
            propose_action("evidence_gate_native", src.descriptors,
                           view, seed=19, step=0),
            (baseline[0], baseline[1], False))

    def test_single_complete_budget_for_each_policy(self):
        # Synthetic full-budget smoke; full scores remain separate from CLI.
        src = make_source("ridge", "constant")
        for policy in POLICIES:
            with self.subTest(policy=policy):
                row = run_campaign(src, policy, 19, 0)
                self.assertEqual(row["total_measured_responses"], TOTAL_MEASUREMENTS)
                self.assertEqual(row["completed_designs"]*REPEATS+
                                 row["stranded_partial_responses"], TOTAL_MEASUREMENTS)
                self.assertEqual(len(row["decision_grid"]), 3)
                self.assertEqual(row["primary_loss"],
                                 next(q["loss_by_penalty"]["0.50"]
                                      for q in row["decision_grid"] if q["z"] == 1.0))
                if policy in MATCHED_POLICIES:
                    self.assertEqual(row["stranded_partial_responses"], 0)
                    self.assertEqual(row["completed_designs"], 16)
                    self.assertEqual(row["incomplete_designs"], 0)
                self.assertGreaterEqual(row["primary_loss"], 0)

    def test_main_requires_explicit_scored_execution(self):
        self.assertEqual(main([]), 0)


if __name__ == "__main__":
    unittest.main()
