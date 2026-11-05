import json
import math
import unittest
from copy import deepcopy

import numpy as np
from scripts.multivariate_hypotheses_v1 import (MODELS, MultivariateBelief, batch_reference,
                                                 composition, demo, features)


class MultivariateHypothesisTests(unittest.TestCase):
    def setUp(self):
        self.rows = [((.6,.2,.2),.7,.12), ((.2,.6,.2),-.1,.15),
                     ((.1,.2,.7),.2,.08), ((.4,.4,.2),.6,.2)]

    def test_families(self):
        self.assertEqual(len(MODELS),3)

    def test_valid_simplex(self):
        self.assertAlmostEqual(sum(composition([.1,.2,.7])),1.)

    def test_reject_sum(self):
        with self.assertRaises(ValueError):composition([.1,.2,.3])

    def test_reject_negative(self):
        with self.assertRaises(ValueError):composition([1.1,-.1,0])

    def test_reject_nan(self):
        with self.assertRaises(ValueError):composition([float('nan'),.2,.8])

    def test_reject_wrong_length(self):
        with self.assertRaises(ValueError):composition([.5,.5])

    def test_basis_sizes(self):
        self.assertEqual([len(features(m,(.5,.2,.3))) for m in MODELS],[3,4,4])

    def test_basis_not_collinear_trivially(self):
        self.assertAlmostEqual(features('linear',(0,0,1))[1],0)

    def test_unknown_model(self):
        with self.assertRaises(ValueError):features('unknown',(.5,.2,.3))

    def test_probabilities_normalize(self):
        b=MultivariateBelief()
        self.assertAlmostEqual(sum(b.probabilities().values()),1.)
        b.observe((.2,.4,.4),.3,.1)
        self.assertAlmostEqual(sum(b.probabilities().values()),1.)

    def test_initial_predictions(self):
        b=MultivariateBelief()
        for m in MODELS:
            mu,var=b.predictive(m,(.3,.4,.3),.2)
            self.assertAlmostEqual(mu,0.)
            self.assertGreaterEqual(var,.04)

    def test_posterior_match_batch(self):
        b=MultivariateBelief()
        for c,y,std in self.rows:b.observe(c,y,std)
        for m in MODELS:
            mean,cov=batch_reference(m,self.rows)
            np.testing.assert_allclose(b.models[m]['mean'],mean,rtol=0,atol=1e-10)
            np.testing.assert_allclose(b.models[m]['covariance'],cov,rtol=0,atol=1e-10)

    def test_variance_decreases(self):
        b=MultivariateBelief()
        old=np.trace(b.models['linear']['covariance'])
        b.observe((.3,.4,.3),.2,.1)
        self.assertLess(np.trace(b.models['linear']['covariance']),old)

    def test_bad_sigma(self):
        with self.assertRaises(ValueError):MultivariateBelief().observe((.3,.4,.3),.1,0)

    def test_bad_observation(self):
        with self.assertRaises(ValueError):MultivariateBelief().observe((.3,.4,.3),float('inf'),.1)

    def test_demonstration_reproducible(self):
        self.assertEqual(demo(),demo())

    def test_fail_closed(self):
        r=demo()
        for k in ('nist_data_used','real_data_experiment_executed','physical_validation',
                  'scored_validation_allowed','independent_holdout_used','scientific_mechanisms_validated'):
            self.assertIs(r[k],False)

    def test_report_discrepancy(self):
        r=demo()
        for x in r['batch_reference_discrepancies'].values():
            self.assertLess(x['mean_max_abs_error'],1e-9)
            self.assertLess(x['covariance_max_abs_error'],1e-9)

    def test_prior_invalid(self):
        with self.assertRaises(ValueError):MultivariateBelief(0)

    def test_batch_invalid(self):
        with self.assertRaises(ValueError):batch_reference('linear',[( (.3,.3,.4),.2,0)])


if __name__ == '__main__':unittest.main()
