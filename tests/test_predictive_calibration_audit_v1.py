import unittest
from scripts.competing_hypotheses_v2 import Belief
from scripts.predictive_calibration_audit_v1 import (
    mixture_cdf, mixture_interval, prequential_audit, development_streams, run_fixed_demo,
)

class PredictiveAuditTests(unittest.TestCase):
    def setUp(self):
        self.b = Belief.initial()
        self.pub = {'a':(-1.,), 'b':(.5,), 'c':(1.,)}

    def test_cdf_bounded(self):
        for y in (-10., 0., 10.):
            self.assertTrue(0 <= mixture_cdf(self.b,.5,y,.12) <= 1)

    def test_cdf_monotonic(self):
        self.assertLess(mixture_cdf(self.b,.5,-1.,.12),mixture_cdf(self.b,.5,1.,.12))

    def test_interval_order(self):
        low, high=mixture_interval(self.b,.5,.12)
        self.assertLess(low,high)

    def test_interval_tails(self):
        lo,hi=mixture_interval(self.b,.5,.12,.9)
        self.assertAlmostEqual(mixture_cdf(self.b,.5,lo,.12),.05,places=7)
        self.assertAlmostEqual(mixture_cdf(self.b,.5,hi,.12),.95,places=7)

    def test_wider_level_gives_wider_interval(self):
        lo1,hi1=mixture_interval(self.b,.5,.12,.5)
        lo2,hi2=mixture_interval(self.b,.5,.12,.9)
        self.assertGreater(hi2-lo2,hi1-lo1)

    def test_prequential_first_record_prior(self):
        report=prequential_audit(self.pub,[('a',1.,.1)])
        self.assertAlmostEqual(report['records'][0]['max_model_probability_before'],1/3)

    def test_predictions_before_updates(self):
        # First forecast must not depend on the first observed value.
        r1=prequential_audit(self.pub,[('a',1.,.1)])['records'][0]
        r2=prequential_audit(self.pub,[('a',-5.,.1)])['records'][0]
        self.assertEqual((r1['lower'],r1['upper']), (r2['lower'],r2['upper']))

    def test_observation_changes_next_prediction(self):
        ra=prequential_audit(self.pub,[('a',2.,.1),('b',0.,.1)])['records'][1]
        rb=prequential_audit(self.pub,[('a',-2.,.1),('b',0.,.1)])['records'][1]
        self.assertNotEqual((ra['lower'],ra['upper']),(rb['lower'],rb['upper']))

    def test_reject_repeat(self):
        with self.assertRaises(ValueError):
            prequential_audit(self.pub,[('a',0.,.1),('a',0.,.1)])

    def test_reject_unknown(self):
        with self.assertRaises(ValueError):
            prequential_audit(self.pub,[('missing',0.,.1)])

    def test_reject_nonfinite(self):
        with self.assertRaises(ValueError):
            prequential_audit(self.pub,[('a',float('nan'),.1)])

    def test_reject_invalid_std(self):
        with self.assertRaises(ValueError):
            prequential_audit(self.pub,[('a',0.,0.)])

    def test_reject_empty(self):
        with self.assertRaises(ValueError):
            prequential_audit(self.pub,[])

    def test_reject_level(self):
        with self.assertRaises(ValueError):
            mixture_interval(self.b,.5,.1,1.)

    def test_fixed_streams(self):
        public,a,b=development_streams()
        self.assertEqual(len(public),20)
        self.assertEqual(len(a),len(b))

    def test_demo_reproducible(self):
        self.assertEqual(run_fixed_demo(),run_fixed_demo())

    def test_flags_fail_closed(self):
        r=run_fixed_demo()
        self.assertFalse(r['scored_validation_allowed'])
        self.assertFalse(r['in_family']['formal_calibration_established'])
        self.assertFalse(r['out_of_family']['out_of_family_detection_certified'])

if __name__ == '__main__':
    unittest.main()
