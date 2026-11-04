import math
import unittest
from scripts.competing_hypotheses_v2 import Belief, MODELS, information_gain, predictive_log_score
from scripts.independent_math_verification_v1 import (
    batch_reference, direct_eig_grid, direct_mixture_logpdf, audit_fixtures,
)

class IndependentMathVerificationTests(unittest.TestCase):
    def test_empty_prior_reference(self):
        r=batch_reference([])
        self.assertEqual(r['means'],(1.,)*len(MODELS))
        self.assertEqual(r['variances'],(.25,)*len(MODELS))
        for p in r['probabilities']:
            self.assertAlmostEqual(p,1/3)
        self.assertAlmostEqual(r['log_total_evidence'],0.)

    def test_batch_vs_sequential_means(self):
        for case in ([(.75,.4,.2)],[(.8,.4,.2),(-.6,.2,.15)],[(0.,.1,.2),(.7,1.2,.21)]):
            r=batch_reference(case)
            b=Belief.initial()
            for x,y,sd in case:b=b.update(x,y,sd)
            for a,c in zip(r['means'],b.means):self.assertAlmostEqual(a,c,places=11)

    def test_batch_vs_sequential_variances(self):
        case=[(-1.,.7,.16),(.3,.13,.23),(.9,.71,.17)]
        r=batch_reference(case);b=Belief.initial()
        for x,y,sd in case:b=b.update(x,y,sd)
        for a,c in zip(r['variances'],b.variances):self.assertAlmostEqual(a,c,places=11)

    def test_batch_vs_sequential_weights(self):
        case=[(-.8,-.5,.17),(.4,.3,.2),(.95,.8,.15)]
        r=batch_reference(case);b=Belief.initial()
        for x,y,sd in case:b=b.update(x,y,sd)
        for a,c in zip(r['probabilities'],b.probabilities()):self.assertAlmostEqual(a,c,places=11)

    def test_log_evidence_matches_sequential(self):
        case=[(-.9,-.5,.17),(.5,.2,.2)]
        r=batch_reference(case);b=Belief.initial()
        for x,y,sd in case:b=b.update(x,y,sd)
        # Belief stores log prior plus sequential conditional evidence.
        for a,c in zip(r['log_model_evidence'],b.log_weights):
            self.assertAlmostEqual(a,c-math.log(1/3),places=10)

    def test_unnormalized_prior(self):
        r=batch_reference([],model_priors=(2,3,5))
        self.assertEqual(tuple(round(x,9) for x in r['probabilities']),(.2,.3,.5))

    def test_direct_predictive_score(self):
        b=Belief.initial().update(.65,.45,.18)
        x,y,sd=-.75,.33,.21
        comps=[b.predictive(i,x,sd) for i in range(len(MODELS))]
        expected=-direct_mixture_logpdf(b.probabilities(),[m for m,v in comps],[v for m,v in comps],y)
        self.assertAlmostEqual(expected,predictive_log_score(b,x,y,sd),places=11)

    def test_eig_trivial_zero(self):
        b=Belief.initial()
        self.assertAlmostEqual(direct_eig_grid(b,0.,.15,grid_points=1001),0.,places=8)
        self.assertAlmostEqual(information_gain(b,0.,.15,128),0.,places=10)

    def test_eig_grid_positive(self):
        self.assertGreater(direct_eig_grid(Belief.initial(),-.9,.18,grid_points=2001),0.01)

    def test_eig_quantile_convergence(self):
        b=Belief.initial()
        ref=direct_eig_grid(b,-.8,.18,grid_points=4001)
        err16=abs(information_gain(b,-.8,.18,16)-ref)
        err128=abs(information_gain(b,-.8,.18,128)-ref)
        self.assertLess(err128,err16)
        self.assertLess(err128,.01)

    def test_eig_grid_resolution(self):
        b=Belief.initial()
        a=direct_eig_grid(b,-.8,.18,grid_points=2001)
        c=direct_eig_grid(b,-.8,.18,grid_points=4001)
        self.assertLess(abs(a-c),1e-5)

    def test_validation_bad_sigma(self):
        with self.assertRaises(ValueError):batch_reference([(.2,1.,0.)])
        with self.assertRaises(ValueError):direct_eig_grid(Belief.initial(),.5,0.)

    def test_validation_bad_grid(self):
        with self.assertRaises(ValueError):direct_eig_grid(Belief.initial(),.5,.2,grid_points=10)

    def test_no_holdout_or_superiority_claim(self):
        r=audit_fixtures()
        for name in ('independent_holdout_used','scored_validation_allowed','claim_of_superiority','physical_validation'):
            self.assertIs(r[name],False)
        self.assertEqual(len(r['batch_checks']),4)

    def test_report_finite(self):
        r=audit_fixtures()
        for item in r['batch_checks']:
            self.assertTrue(all(math.isfinite(v) for v in item.values()))
        self.assertTrue(all(math.isfinite(v) for v in r['eig_nats'].values()))

if __name__=='__main__':unittest.main()
