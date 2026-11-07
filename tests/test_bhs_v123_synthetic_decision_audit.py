"""Source-independent contracts for controlled synthetic decision evaluation."""
import inspect
import unittest
from dataclasses import replace

import numpy as np

from scripts.bhs_measurement_allocation_v12 import (
    MeasurementContractError, INITIAL_MEASUREMENTS, TOTAL_MEASUREMENTS,
    initial_geometry_ids,
)
from scripts.bhs_v123_synthetic_decision_audit import (
    BUNDLED_AND_GATE, DESCRIPTOR_SEED, HARD_GATES, NOISE_SEED,
    POOL_SIZE, POLICIES, REGIMES, SEEDS, ORDER_VARIANTS,
    ControlledSyntheticOracle, choose_action, main, make_scenario, run_campaign,
)


class ControlledSyntheticAuditTests(unittest.TestCase):
    def test_source_schema_determinism_and_fingerprints(self):
        for regime in REGIMES:
            first, second = make_scenario(regime), make_scenario(regime)
            self.assertEqual(first.descriptors.shape, (48, 4))
            self.assertEqual(first.outcomes.shape, (48, 3))
            self.assertEqual(first.latent.shape, (48,))
            self.assertEqual(first.digest, second.digest)
            np.testing.assert_array_equal(first.descriptors, second.descriptors)
            np.testing.assert_array_equal(first.outcomes, second.outcomes)
        self.assertEqual(DESCRIPTOR_SEED, 20261107)
        self.assertEqual(NOISE_SEED, 73123)

    def test_scenarios_share_latent_and_only_noise_changes(self):
        constant, varying = make_scenario('constant'), make_scenario('varying')
        np.testing.assert_array_equal(constant.descriptors, varying.descriptors)
        np.testing.assert_array_equal(constant.latent, varying.latent)
        self.assertFalse(np.array_equal(constant.outcomes, varying.outcomes))
        with self.assertRaises(MeasurementContractError):
            make_scenario('nonexistent')

    def test_order_variants_preserve_response_multiset(self):
        source = make_scenario('varying')
        a = ControlledSyntheticOracle(source, 7, 0)
        b = ControlledSyntheticOracle(source, 7, 1)
        divergent = False
        for i in range(POOL_SIZE):
            pa = [a.reveal_one(i, j) for j in (1, 2, 3)]
            pb = [b.reveal_one(i, j) for j in (1, 2, 3)]
            np.testing.assert_array_equal(sorted(pa), sorted(pb))
            divergent |= pa != pb
        self.assertTrue(divergent)

    def test_private_ledger_forbids_duplicate_skip_and_bool_index(self):
        oracle = ControlledSyntheticOracle(make_scenario('constant'), 7, 0)
        with self.assertRaisesRegex(MeasurementContractError, 'OUT_OF_ORDER'):
            oracle.reveal_one(0, 2)
        oracle.reveal_one(0, 1)
        with self.assertRaisesRegex(MeasurementContractError, 'ALREADY_SEEN'):
            oracle.reveal_one(0, 1)
        oracle.reveal_one(0, 2)
        oracle.reveal_one(0, 3)
        with self.assertRaises(MeasurementContractError):
            oracle.reveal_one(0, 3)
        with self.assertRaises(MeasurementContractError):
            oracle.reveal_one(True, 1)
        with self.assertRaises(MeasurementContractError):
            ControlledSyntheticOracle(make_scenario('constant'), 10000, 0)
        with self.assertRaises(MeasurementContractError):
            ControlledSyntheticOracle(make_scenario('constant'), 7, 2)

    def test_transcript_cannot_be_forged_or_shortened(self):
        oracle = ControlledSyntheticOracle(make_scenario('constant'), 7, 0)
        first = oracle.reveal_one(0, 1)
        with self.assertRaisesRegex(MeasurementContractError, 'IDS_DIFFER'):
            oracle.evaluate({})
        with self.assertRaisesRegex(MeasurementContractError, 'VALUES_DIFFER'):
            oracle.evaluate({0: (first + 1,)})
        with self.assertRaisesRegex(MeasurementContractError, 'BUDGET_NOT_EXACT'):
            oracle.evaluate({0: (first,)})

    def test_unseen_outcomes_do_not_affect_immediate_action(self):
        source = make_scenario('constant')
        ids = initial_geometry_ids(POOL_SIZE, 7)
        exposed = {i: tuple(map(float, source.outcomes[i])) for i in ids}
        hidden = source.outcomes.copy()
        hidden[[j for j in range(POOL_SIZE) if j not in ids]] += 2000
        altered = replace(source, outcomes=hidden)
        same_exposed = {i: tuple(map(float, altered.outcomes[i])) for i in ids}
        self.assertEqual(exposed, same_exposed)
        for policy in POLICIES:
            with self.subTest(policy=policy):
                left = choose_action(policy, source.descriptors, exposed, seed=7, step=0)
                right = choose_action(policy, altered.descriptors, same_exposed, seed=7, step=0)
                self.assertEqual(left, right)

    def test_acquisition_api_has_no_private_inputs(self):
        self.assertEqual(list(inspect.signature(choose_action).parameters),
                         ['policy', 'descriptors', 'observed', 'seed', 'step'])
        self.assertEqual(len(SEEDS), 2)
        self.assertEqual(ORDER_VARIANTS, (0, 1))
        self.assertEqual(BUNDLED_AND_GATE, POLICIES[:3])
        self.assertEqual(sum(v is True for v in HARD_GATES.values()), 1)
        self.assertFalse(HARD_GATES['claim_of_superiority'])
        self.assertFalse(HARD_GATES['independent_holdout_used'])

    def test_random_bundled_exact_budget_and_complete_recommendation(self):
        scenario = make_scenario('varying')
        result = run_campaign(scenario, 'random_bundled', 7, 0)
        self.assertEqual(result['measurement_count'], TOTAL_MEASUREMENTS)
        self.assertEqual(result['completed_geometries'], 16)
        self.assertEqual(result['partial_geometries'], 0)
        self.assertGreaterEqual(result['latent_simple_regret'], 0.0)
        self.assertLessEqual(result['best_completed_latent_regret'],
                             result['latent_simple_regret'] + 1e-9)
        self.assertFalse(result['selection_sees_latent_quality'])
        self.assertFalse(result['unobserved_responses_used_by_selector'])
        self.assertEqual(INITIAL_MEASUREMENTS, 18)

    def test_gp_one_complete_synthetic_budget(self):
        row = run_campaign(make_scenario('constant'), 'gp_pooled_noise_ivr', 7, 1)
        self.assertEqual(row['measurement_count'], 48)
        self.assertEqual(row['partial_geometries'], 0)
        self.assertEqual(row['completed_geometries'], 16)

    def test_evidence_gate_stays_development_only(self):
        row = run_campaign(make_scenario('varying'), 'evidence_gate_development', 13, 0)
        self.assertEqual(row['measurement_count'], 48)
        self.assertGreaterEqual(row['completed_geometries'], 6)
        self.assertGreaterEqual(row['partial_geometries'], 0)

    def test_inconsistent_policy_seed_order_rejected(self):
        source = make_scenario('constant')
        for policy, seed, variant in [('not-a-policy', 7, 0),
                                       ('random_bundled', 10000, 0),
                                       ('random_bundled', 7, 8)]:
            with self.subTest(policy=policy, seed=seed, variant=variant):
                with self.assertRaises(MeasurementContractError):
                    run_campaign(source, policy, seed, variant)
        with self.assertRaises(MeasurementContractError):
            choose_action('not-a-policy', source.descriptors, {}, seed=7, step=0)

    def test_cli_defaults_to_no_outcome_execution(self):
        self.assertEqual(main([]), 0)


if __name__ == '__main__':
    unittest.main()
