import unittest
from scripts.bayesian_only_policy_v1 import BayesianOnlyPolicyV1
from scripts.scientific_benchmark_contract_v1 import make_task, MeteredEvaluator

class BayesianOnlyPolicyTests(unittest.TestCase):
    def test_prior(self):
        m,v,_,seen = BayesianOnlyPolicyV1(0).posterior({'a':(1.0,)},())
        self.assertEqual((m,v,seen),(0.0,1.0,set()))
    def test_posterior_known_update(self):
        m,v,_,_ = BayesianOnlyPolicyV1(0,prior_variance=1,noise_variance=1).posterior({'a':(1.0,)},(('a',2.0),))
        self.assertAlmostEqual(m,1.0); self.assertAlmostEqual(v,0.5)
    def test_negative_observation(self):
        m,v,_,_ = BayesianOnlyPolicyV1(0).posterior({'a':(-1.,)},(('a',1.),))
        self.assertLess(m,0);self.assertLess(v,1)
    def test_reproducible(self):
        p={'a':(-1.,),'b':(0.,),'c':(1.,)}
        self.assertEqual(BayesianOnlyPolicyV1(4).choose(p,()),BayesianOnlyPolicyV1(4).choose(p,()))
    def test_no_repeat(self):
        x=MeteredEvaluator(make_task('smooth',3),10).run(BayesianOnlyPolicyV1(5))
        self.assertEqual(len(set(t['candidate_id'] for t in x['trace'])),10)
    def test_all_synthetic_scenarios(self):
        for scenario in ('smooth','multimodal','uninformative','mismatched','duplicates'):
            with self.subTest(scenario=scenario):
                r=MeteredEvaluator(make_task(scenario,3),5).run(BayesianOnlyPolicyV1(7))
                self.assertEqual(r['queries'],5)
                self.assertFalse(r['scored_benchmark'])
    def test_budget_reproducibility(self):
        t=make_task('smooth',13)
        self.assertEqual(MeteredEvaluator(t,5).run(BayesianOnlyPolicyV1(42)),MeteredEvaluator(t,5).run(BayesianOnlyPolicyV1(42)))
    def test_duplicate_observation_rejected(self):
        with self.assertRaises(ValueError):
            BayesianOnlyPolicyV1(0).choose({'a':(1.,),'b':(2.,)},(('a',1.),('a',2.)))
    def test_unknown_observation_rejected(self):
        with self.assertRaises(ValueError):BayesianOnlyPolicyV1(0).choose({'a':(1.,)},(('z',1.),))
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):BayesianOnlyPolicyV1(0).choose({'a':(float('nan'),)},())
    def test_invalid_hyperparameters(self):
        for kw in ({'seed':True},{'seed':0,'noise_variance':0},{'seed':0,'prior_variance':-1},{'seed':0,'exploration_scale':float('nan')}):
            with self.subTest(kw=kw),self.assertRaises(ValueError):BayesianOnlyPolicyV1(**kw)
    def test_deterministic_exploitation(self):
        p={'a':(-1.,),'b':(1.,)}
        self.assertEqual(BayesianOnlyPolicyV1(0,exploration_scale=0).choose(p,(('a',-2.),)),'b')
    def test_exhausted_pool(self):
        with self.assertRaises(ValueError):BayesianOnlyPolicyV1(0).choose({'a':(1.,)},(('a',1.),))

if __name__=='__main__':unittest.main()
