import math
import unittest
from unittest.mock import patch
from scripts.belief_state_search_v1 import (BeliefStateSearchV1, bayes_update, outcome_bin,
                                             run_fixed_development_demo, STATUS)


class BeliefStateSearchTests(unittest.TestCase):
    def test_conjugate_update(self):
        mean, variance = bayes_update(0.0, 1.0, 1.0, 2.0, 1.0)
        self.assertAlmostEqual(mean, 1.0)
        self.assertAlmostEqual(variance, 0.5)

    def test_zero_descriptor_no_information(self):
        mean, variance = bayes_update(0.2, 0.6, 0.0, -2.0, 0.1)
        self.assertAlmostEqual(mean, 0.2)
        self.assertAlmostEqual(variance, 0.6)

    def test_variance_never_increases(self):
        mean, variance = 0.0, 1.0
        for x, y in [(1.0, 0.1), (-0.5, 0.6), (0.0, 0.2)]:
            updated_mean, updated_variance = bayes_update(mean, variance, x, y, 0.1)
            self.assertLessEqual(updated_variance, variance + 1e-12)
            mean, variance = updated_mean, updated_variance

    def test_reject_bad_update(self):
        for args in ((0, 0, 1, 1, .1), (0, 1, 1, 1, 0),
                     (float('nan'), 1, 1, 1, .1)):
            with self.assertRaises(ValueError): bayes_update(*args)

    def test_outcome_bins(self):
        self.assertEqual(outcome_bin(-1, 0, 1), -1)
        self.assertEqual(outcome_bin(0, 0, 1), 0)
        self.assertEqual(outcome_bin(1, 0, 1), 1)

    def test_outcome_bin_invalid(self):
        with self.assertRaises(ValueError): outcome_bin(0, 0, 0)

    def test_reproducible(self):
        p = {'a':(-1.,), 'b':(-0.5,), 'c':(0.,), 'd':(0.5,), 'e':(1.,)}
        a, b = BeliefStateSearchV1(9, simulations=32), BeliefStateSearchV1(9, simulations=32)
        self.assertEqual(a.choose(p, ()), b.choose(p, ()))
        self.assertEqual(a.last_diagnostics, b.last_diagnostics)

    def test_posterior_input_used(self):
        p = {'a':(-1.,), 'b':(1.,), 'c':(.3,)}
        policy = BeliefStateSearchV1(2, simulations=16)
        action = policy.choose(p, [('a', -2.0)])
        self.assertIn(action, ('b', 'c'))

    def test_tree_has_observation_nodes(self):
        p = {'a':(-1.,), 'b':(-0.5,), 'c':(.5,), 'd':(1.,)}
        policy = BeliefStateSearchV1(3, simulations=96, horizon=3)
        policy.choose(p, ())
        diag = policy.last_diagnostics
        self.assertGreater(diag['observation_branches_created'], 0)
        self.assertTrue(diag['posterior_updates_during_simulation'])
        self.assertTrue(diag['observation_contingent_tree'])
        self.assertEqual(diag['root_visits'], 96)
        self.assertEqual(sum(v['visits'] for v in diag['root_children'].values()), 96)

    def test_no_duplicate_action(self):
        p = {'a':(-1.,), 'b':(.5,), 'c':(1.,)}
        policy = BeliefStateSearchV1(3)
        self.assertNotEqual(policy.choose(p, [('a', 0.7)]), 'a')

    def test_pool_exhausted(self):
        with self.assertRaises(ValueError):
            BeliefStateSearchV1(4).choose({'a':(1.,)}, [('a', 1.)])

    def test_reject_invalid_model(self):
        for kwargs in ({'seed':True}, {'seed':3,'simulations':0},
                       {'seed':3,'horizon':0}, {'seed':3,'c_uct':float('nan')},
                       {'seed':3,'noise_variance':0}):
            with self.assertRaises(ValueError): BeliefStateSearchV1(**kwargs)

    def test_fail_closed_flags(self):
        p = {'a':(-1.,), 'b':(1.,)}
        policy = BeliefStateSearchV1(2, simulations=12)
        policy.choose(p, ())
        d = policy.last_diagnostics
        self.assertFalse(d['scored_validation_allowed'])
        self.assertFalse(d['formal_bamcp_correctness_established'])
        self.assertFalse(d['physical_validation'])
        self.assertTrue(d['observation_nodes_are_approximate_bins'])

    def test_fixed_demo_no_holdout(self):
        with patch('scripts.belief_state_search_v1.run_fixed_development_demo', wraps=run_fixed_development_demo) as wrapped:
            report = wrapped()
            self.assertEqual(report['queries'], 5)
            self.assertFalse(report['independent_holdout_used'])
            self.assertFalse(report['scored_validation_allowed'])
            self.assertEqual(report['development_task'], 'smooth/7')

if __name__ == '__main__': unittest.main()
