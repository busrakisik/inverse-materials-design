import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.competing_hypotheses_v2 import (
    MODELS, STATUS, Belief, ParametricHypothesisPolicyV2, basis,
    development_demo, fit_belief, information_gain, predictive_log_score,
)

PUBLIC = {
    "neg": (-1.0,), "mid": (-0.5,), "zero": (0.0,),
    "half": (0.5,), "pos": (1.0,)
}


class ParametricHypothesisTests(unittest.TestCase):
    def test_model_families(self):
        self.assertEqual(MODELS, ("linear", "quadratic", "oscillatory"))
        self.assertEqual(basis("quadratic", -.5), .25)
        self.assertAlmostEqual(basis("oscillatory", 0), 0)

    def test_prior_is_normalized(self):
        b = Belief.initial()
        self.assertAlmostEqual(sum(b.probabilities()), 1.0)
        self.assertEqual(b.means, (1.0, 1.0, 1.0))

    def test_known_noise_conjugate_posterior(self):
        # phi_linear(1)=1, a ~ N(1,1), y=2, noise variance 1
        b = Belief.initial(prior_parameter_variance=1)
        newer = b.update(1.0, 2.0, 1.0)
        self.assertAlmostEqual(newer.means[0], 1.5)
        self.assertAlmostEqual(newer.variances[0], .5)

    def test_posterior_variance_shrinks(self):
        b = Belief.initial()
        for _ in range(3):
            c = b.update(.8, .3, .15)
            self.assertTrue(all(x <= y for x,y in zip(c.variances,b.variances)))
            b = c

    def test_zero_feature_does_not_change_parameter_belief(self):
        b = Belief.initial()
        new = b.update(0., .2, .15)
        self.assertEqual(new.means, b.means)
        self.assertEqual(new.variances, b.variances)
        self.assertAlmostEqual(new.entropy(), b.entropy())

    def test_high_noise_weak_evidence(self):
        b = Belief.initial()
        low = b.update(-1., 1., .05)
        high = b.update(-1., 1., 10.)
        self.assertGreater(max(low.probabilities()), max(high.probabilities()))

    def test_posterior_probability_normalized(self):
        b = Belief.initial()
        for x,y,std in ((-1, .9,.1), (1,.8,.2),(-.3,.05,.15)):
            b = b.update(x,y,std)
        self.assertAlmostEqual(sum(b.probabilities()), 1.0)
        self.assertTrue(all(math.isfinite(x) for x in b.log_weights))

    def test_predictive_includes_parameter_variance(self):
        b = Belief.initial(prior_parameter_variance=1.)
        mu, var = b.predictive(0, 1., .2)
        self.assertEqual(mu,1.)
        self.assertAlmostEqual(var,1.04)

    def test_sequential_fit_matches_update(self):
        b,seen,xs = fit_belief(PUBLIC,[("neg",1.,.2),("pos",.8,.1)])
        expected = Belief.initial().update(-1.,1.,.2).update(1.,.8,.1)
        for a,c in zip(b.probabilities(),expected.probabilities()):
            self.assertAlmostEqual(a,c)
        self.assertEqual(seen,{"neg","pos"})

    def test_eig_zero_for_feature_zero(self):
        self.assertAlmostEqual(information_gain(Belief.initial(),0.,.15,16),0.,places=12)

    def test_eig_informative(self):
        self.assertGreater(information_gain(Belief.initial(),-1.,.15,16),.001)

    def test_nonfinite_rejected(self):
        for vals in ((float("nan"),1.,.1),(0.,float("inf"),.1),(0.,1.,0.)):
            with self.subTest(vals=vals),self.assertRaises(ValueError):
                Belief.initial().update(*vals)

    def test_unknown_duplicate_invalid_std(self):
        for obs in ([("neg",1.,.2),("neg",.5,.2)],
                    [("unknown",1.,.2)], [("neg",.3,-.1)], [("neg",.3)]):
            with self.subTest(obs=obs),self.assertRaises(ValueError):
                fit_belief(PUBLIC,obs)

    def test_policy_deterministic(self):
        a=ParametricHypothesisPolicyV2(quantiles=16)
        b=ParametricHypothesisPolicyV2(quantiles=16)
        self.assertEqual(a.choose(PUBLIC,[]),b.choose(PUBLIC,[]))
        self.assertEqual(a.last_diagnostics,b.last_diagnostics)

    def test_policy_excludes_previous(self):
        p=ParametricHypothesisPolicyV2(quantiles=16)
        a=p.choose(PUBLIC,[])
        self.assertNotEqual(p.choose(PUBLIC,[(a,.4,.1)]),a)

    def test_noise_map_validation(self):
        p=ParametricHypothesisPolicyV2(quantiles=16)
        with self.assertRaises(ValueError):
            p.choose(PUBLIC,[],planned_stds={"neg":.1})
        with self.assertRaises(ValueError):
            p.choose(PUBLIC,[],planned_stds={k:0 for k in PUBLIC})

    def test_predictive_surprisal_sensitivity(self):
        b=Belief.initial()
        near=predictive_log_score(b,.5,.3,.1)
        far=predictive_log_score(b,.5,20.,.1)
        self.assertGreater(far,near)

    def test_no_holdout_and_flags(self):
        r=development_demo()
        self.assertEqual(len(r["trace"]),5)
        self.assertFalse(r["independent_holdout_used"])
        self.assertFalse(r["scored_validation_allowed"])
        p=ParametricHypothesisPolicyV2(quantiles=16)
        p.choose(PUBLIC,[])
        self.assertFalse(p.last_diagnostics["calibration_established"])
        self.assertFalse(p.last_diagnostics["physical_validation"])

    def test_demo_deterministic(self):
        self.assertEqual(development_demo(),development_demo())

    def test_invalid_prior_and_quadrature(self):
        for v in (0.,float("nan"),True):
            with self.assertRaises(ValueError): Belief.initial(prior_parameter_variance=v)
        with self.assertRaises(ValueError): ParametricHypothesisPolicyV2(quantiles=0)
        with self.assertRaises(ValueError): Belief.initial(priors=(.2,.8))

    def test_exhaustion(self):
        with self.assertRaises(ValueError):
            ParametricHypothesisPolicyV2(quantiles=16).choose({"one":(1.,)},[("one",1.,.1)])


if __name__ == "__main__":
    unittest.main()
