import math
import unittest
from scripts.mcts_puct_policy_v1 import OpenLoopPUCTPolicyV1
from scripts.scientific_benchmark_contract_v1 import MeteredEvaluator, make_task

class PUCTTests(unittest.TestCase):
    def test_end_to_end_development_seed(self):
        task = make_task('smooth', 7)
        policy = OpenLoopPUCTPolicyV1(13, simulations=48)
        result = MeteredEvaluator(task, 5).run(policy)
        self.assertEqual(result['queries'], 5)
        self.assertEqual(len({r['candidate_id'] for r in result['trace']}), 5)
        self.assertFalse(result['scored_benchmark'])
    def test_reproducible(self):
        data = {'a': (0.3,), 'b': (-0.9,), 'c': (1.0,)}
        p = lambda: OpenLoopPUCTPolicyV1(42, simulations=64)
        x, y = p(), p()
        self.assertEqual(x.choose(data, ()), y.choose(data, ()))
        self.assertEqual(x.last_diagnostics, y.last_diagnostics)
    def test_prior_observations(self):
        p = OpenLoopPUCTPolicyV1(4, simulations=40)
        choice = p.choose({'a': (0.0,), 'b': (1.0,), 'c': (-1.0,)}, [('a', 0.3)])
        self.assertIn(choice, {'b', 'c'})
    def test_all_root_children_expanded(self):
        p = OpenLoopPUCTPolicyV1(1, simulations=12, horizon=2)
        p.choose({'a': (-1,), 'b': (0,), 'c': (1,)}, [])
        self.assertEqual(p.last_diagnostics['root_visits'], 12)
        self.assertEqual(p.last_diagnostics['expanded_root_actions'], 3)
        self.assertEqual(sum(x['visits'] for x in p.last_diagnostics['root_children'].values()), 12)
    def test_one_simulation_valid(self):
        p = OpenLoopPUCTPolicyV1(1, simulations=1)
        self.assertIn(p.choose({'a': (0.2,), 'b': (0.8,)}, []), ('a', 'b'))
    def test_exhausted(self):
        with self.assertRaises(ValueError):
            OpenLoopPUCTPolicyV1(1).choose({'a': (1,)}, [('a', 0.1)])
    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            OpenLoopPUCTPolicyV1(1).choose({'a': (float('nan'),)}, [])
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            OpenLoopPUCTPolicyV1(1).choose({'a': (1,), 'b': (2,)}, [('a', 0.2), ('a', 0.3)])
    def test_parameter_validation(self):
        for kw in ({'seed': True}, {'seed': 0, 'simulations': 0},
                   {'seed': 0, 'simulations': True}, {'seed': 0, 'horizon': 0},
                   {'seed': 0, 'horizon': 11}, {'seed': 0, 'c_puct': float('nan')},
                   {'seed': 0, 'c_puct': 0}, {'seed': 0, 'noise_variance': -1}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                OpenLoopPUCTPolicyV1(**kw)
    def test_no_holdout_flag(self):
        p = OpenLoopPUCTPolicyV1(2, simulations=12)
        p.choose({'a': (1,), 'b': (-1,)}, [])
        self.assertFalse(p.last_diagnostics['scored_validation_allowed'])
        self.assertFalse(p.last_diagnostics['adaptive_observation_tree'])
    def test_multiscenario_dev_only(self):
        for scenario in ('smooth', 'multimodal', 'uninformative', 'mismatched', 'duplicates'):
            with self.subTest(scenario=scenario):
                p=OpenLoopPUCTPolicyV1(13,simulations=12,horizon=2)
                output=MeteredEvaluator(make_task(scenario, 7), 2).run(p)
                self.assertEqual(output['queries'],2)
    def test_no_public_mutation(self):
        p=OpenLoopPUCTPolicyV1(5,simulations=8)
        public={'a': [1.0], 'b': [-1.0]}
        p.choose(public, [])
        self.assertEqual(public, {'a': [1.0], 'b': [-1.0]})

if __name__ == '__main__':unittest.main()
