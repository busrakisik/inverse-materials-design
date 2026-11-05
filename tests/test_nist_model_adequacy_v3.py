"""Synthetic-only prequential correctness tests; holdout seeds 10000–10099 forbidden."""
from __future__ import annotations

import inspect
import json
import math
import random
import unittest
from unittest.mock import patch

import numpy as np
from scipy.special import ndtr
from scripts.nist_model_adequacy_v3 import (
    STATUS, DEV_SEEDS, SELECTION_POLICIES, PREDICTORS,
    validate_protocol, gaussian_mixture, mixture_cdf, mixture_quantile,
    forecast_components, score_observation, trajectory,
    summarize_trajectories, evaluate_prequential, run_pinned_bytes,
)
from scripts.nist_anonymous_offline_pilot_v1 import gp_predict, campaign
from scripts.multivariate_hypotheses_v1 import MultivariateBelief


def pool(n=30):
    x = np.random.default_rng(2026).dirichlet([2.,2.,2.],size=n)
    y = .2 + .8*x[:,0] - .3*x[:,1] + 1.3*x[:,0]*x[:,1]
    return x,y


class ModelAdequacyTests(unittest.TestCase):
    def setUp(self):
        self.x,self.y=pool()
        self.initial=[0,2,5]
        self.z=np.array([.1,-.2,.4])
        self.probe=7

    def test_01_protocol_frozen(self):
        self.assertEqual(DEV_SEEDS,(7,13,23,31,41))
        self.assertEqual(len(PREDICTORS),5)
        self.assertEqual(len(SELECTION_POLICIES),3)
        self.assertTrue(validate_protocol())

    def test_02_forbid_independent_seed_start(self):
        with self.assertRaises(ValueError):validate_protocol([10000])

    def test_03_forbid_independent_seed_end(self):
        with self.assertRaises(ValueError):validate_protocol([10099])

    def test_04_forbid_negative_seed(self):
        with self.assertRaises(ValueError):validate_protocol([-1])

    def test_05_duplicate_seed(self):
        with self.assertRaises(ValueError):validate_protocol([7,7])

    def test_06_noninteger_seed(self):
        with self.assertRaises(ValueError):validate_protocol([7.0])

    def test_07_budget_is_frozen(self):
        with self.assertRaises(ValueError):validate_protocol([7],14)

    def test_08_single_gaussian_logpdf(self):
        v=score_observation(0.,*[np.array(q) for q in ([1.],[0.],[1.])])
        self.assertAlmostEqual(v['nlpd'],.5*math.log(2*math.pi),places=12)
        self.assertAlmostEqual(v['pit'],0.5,places=12)
        self.assertTrue(v['covered_90'])

    def test_09_single_gaussian_quantiles(self):
        w,m,v=gaussian_mixture([1.],[0.],[4.])
        self.assertAlmostEqual(mixture_quantile(.5,w,m,v),0.,places=10)
        self.assertAlmostEqual(mixture_quantile(.95,w,m,v),3.28970725390294,places=9)

    def test_10_mixture_cdf_monotone(self):
        w,m,v=gaussian_mixture([.3,.7],[-3.,4.],[.5,2.])
        cdfs=[mixture_cdf(p,w,m,v) for p in (-8,-2,1,4,10)]
        self.assertEqual(cdfs,sorted(cdfs))

    def test_11_mixture_interval_uses_true_mixture_not_gaussian_proxy(self):
        w,m,v=gaussian_mixture([.5,.5],[-5.,5.],[.01,.01])
        lo=mixture_quantile(.05,w,m,v)
        hi=mixture_quantile(.95,w,m,v)
        self.assertLess(lo,-5.)
        self.assertGreater(hi,5.)
        self.assertAlmostEqual(mixture_cdf(lo,w,m,v),.05,places=7)
        self.assertAlmostEqual(mixture_cdf(hi,w,m,v),.95,places=7)

    def test_12_mixture_nlpd_not_squared_weights(self):
        w,m,v=gaussian_mixture([.25,.75],[0.,2.],[1.,1.])
        expected=-math.log(.25/math.sqrt(2*math.pi)+.75/math.sqrt(2*math.pi)*math.exp(-2.))
        self.assertAlmostEqual(score_observation(0.,w,m,v)['nlpd'],expected,places=12)

    def test_13_zero_weight_component_does_not_change_score(self):
        w,m,v=gaussian_mixture([1.,0.],[1.,-40.],[.5,1.])
        s=score_observation(1.,w,m,v)
        t=score_observation(1.,*gaussian_mixture([1.],[1.],[.5]))
        self.assertAlmostEqual(s['nlpd'],t['nlpd'],places=12)

    def test_14_reject_invalid_mixture(self):
        for args in [([.2,.2],[1,2],[1,1]),([1.],[0.],[-1.]),([1.],[float('nan')],[1.]),([-.5,1.5],[0,1],[1,1])]:
            with self.subTest(args=args),self.assertRaises(ValueError):gaussian_mixture(*args)

    def test_15_reject_bad_quantile_level(self):
        w,m,v=gaussian_mixture([1.],[0.],[1.])
        with self.assertRaises(ValueError):mixture_quantile(1.0,w,m,v)

    def test_16_forecaster_observed_only_signature(self):
        params=list(inspect.signature(forecast_components).parameters)
        self.assertEqual(params,['predictor','candidates','selected','observed_z','candidate_index'])
        self.assertNotIn('hidden_labels',params)

    def test_17_gp_default_matches_existing_model(self):
        w,m,v=forecast_components('gp_length_0p22',self.x,self.initial,self.z,self.probe)
        mref,latent=gp_predict(self.x,self.initial,self.z)
        self.assertAlmostEqual(float(m[0]),float(mref[self.probe]),places=11)
        self.assertAlmostEqual(float(v[0]),float(latent[self.probe]**2+.15**2),places=10)

    def test_18_bhs_bma_weights_and_observation_variance_match(self):
        w,m,v=forecast_components('bhs_bma_sigma_0p15',self.x,self.initial,self.z,self.probe)
        b=MultivariateBelief(prior_variance=.5)
        for i,z in zip(self.initial,self.z):b.observe(self.x[i],float(z),.15)
        p=b.probabilities()
        np.testing.assert_allclose(w,[p[f] for f in b.models],atol=1e-12)
        np.testing.assert_allclose([b.predictive(f,self.x[self.probe],.15)[0] for f in b.models],m,atol=1e-12)
        np.testing.assert_allclose([b.predictive(f,self.x[self.probe],.15)[1] for f in b.models],v,atol=1e-12)

    def test_19_bhs_interaction_is_single_component(self):
        w,m,v=forecast_components('bhs_interaction_sigma_0p15',self.x,self.initial,self.z,self.probe)
        self.assertEqual(len(w),1)
        self.assertAlmostEqual(float(w[0]),1.)

    def test_20_posthoc_sigma_changes_prediction(self):
        a=forecast_components('bhs_bma_sigma_0p15',self.x,self.initial,self.z,self.probe)
        b=forecast_components('bhs_bma_sigma_0p05_posthoc',self.x,self.initial,self.z,self.probe)
        self.assertGreater(float(np.max(abs(a[2]-b[2]))),1e-4)

    def test_21_no_selected_or_bad_candidate_forecast(self):
        with self.assertRaises(ValueError):forecast_components('gp_length_0p22',self.x,self.initial,self.z,self.initial[0])
        with self.assertRaises(ValueError):forecast_components('gp_length_0p22',self.x,self.initial,self.z,99)

    def test_22_no_unobserved_response_in_forecast_api(self):
        with self.assertRaises(ValueError):forecast_components('gp_length_0p22',self.x,self.initial,self.z[:2],self.probe)

    def test_23_prequential_count_each_trajectory(self):
        for pol in SELECTION_POLICIES:
            rows=trajectory(self.x,self.y,pol,7)
            self.assertEqual(set(rows),set(PREDICTORS))
            self.assertTrue(all(len(v)==12 for v in rows.values()))
            self.assertTrue(all(math.isfinite(z['nlpd']) for s in rows.values() for z in s))

    def test_24_trajectory_matches_v1_selection_outcome(self):
        # Intercept selectors to capture anonymous indices in memory only, never an artifact.
        old=__import__('scripts.nist_model_adequacy_v3',fromlist=['choose_next']).choose_next
        for pol in SELECTION_POLICIES:
            selected=[]
            def wrapped(p,x,sel,z,rng):
                idx=old(p,x,sel,z,rng);selected.append(idx);return idx
            with patch('scripts.nist_model_adequacy_v3.choose_next',side_effect=wrapped):
                trajectory(self.x,self.y,pol,7)
            # Independently replay v1 public API, verify the final objective by step 15
            expected=campaign(self.x,self.y,pol,7)['final_normalized_simple_regret']
            rng=random.Random(7)
            initial=rng.sample(range(len(self.x)),3)
            actual=(self.y.max()-self.y[initial+selected].max())/np.ptp(self.y)
            self.assertAlmostEqual(expected,actual,places=11)

    def test_25_no_label_reveal_prior_to_predictive_forecast(self):
        observed_counts=[]
        original=forecast_components
        def capture(p,x,sel,z,idx):
            observed_counts.append(len(z))
            return original(p,x,sel,z,idx)
        with patch('scripts.nist_model_adequacy_v3.forecast_components',side_effect=capture):
            trajectory(self.x,self.y,'random',7)
        self.assertEqual(len(observed_counts),60)
        self.assertEqual(observed_counts[:5],[3]*5)
        self.assertEqual(observed_counts[-5:],[14]*5)

    def test_26_summary_has_count_and_no_rows(self):
        rows=[trajectory(self.x,self.y,'random',7)]
        summ=summarize_trajectories(rows)
        self.assertEqual(summ['gp_length_0p22']['prequential_forecast_count'],12)
        self.assertEqual(sum(summ['gp_length_0p22']['pit_bin_counts_5']),12)
        self.assertNotIn('selected_indices',json.dumps(summ))
        self.assertNotIn('raw_labels',json.dumps(summ))
        self.assertNotIn('observed_z',json.dumps(summ))

    def test_27_summary_paired_baseline_difference_zero(self):
        a=summarize_trajectories([trajectory(self.x,self.y,'random',7)])
        gp=a['gp_length_0p22']
        self.assertAlmostEqual(gp['mean_paired_nlpd_minus_gp_length_0p22'],0.,places=12)
        self.assertEqual(gp['paired_nlpd_better_tie_worse_vs_gp_length_0p22'],{'better':0,'tie':1,'worse':0})

    def test_28_report_integrity_synthetic(self):
        r=evaluate_prequential(self.x,self.y,seeds=(7,13))
        self.assertEqual(set(r),set(SELECTION_POLICIES))
        for traj in r.values():
            for predictor in traj.values():
                self.assertEqual(predictor['prequential_forecast_count'],24)
                self.assertEqual(predictor['development_seed_count'],2)
                self.assertGreaterEqual(predictor['mean_90pct_interval_coverage'],0)
                self.assertLessEqual(predictor['mean_90pct_interval_coverage'],1)

    def test_29_reject_reserved_seed_in_real_campaign(self):
        with self.assertRaises(ValueError):trajectory(self.x,self.y,'random',10000)

    def test_30_end_to_end_aggregate_serializes_without_raw_labels(self):
        fake={k:np.zeros((1,)) for k in ('C','Coer','Kerr','XRD','TTH')}
        summary={'eligible_samples':len(self.x),'element_order_verified':False}
        with patch('scripts.nist_model_adequacy_v3.validate_source',return_value='fixture_sha'),\
             patch('scripts.nist_model_adequacy_v3.loadmat',return_value=fake),\
             patch('scripts.nist_model_adequacy_v3.finite_pilot_pool',return_value=(self.x,self.y,summary)):
            report=run_pinned_bytes(b'synthetic-only-fixture')
        raw=json.dumps(report,allow_nan=False)
        self.assertEqual(report['status'],STATUS)
        self.assertFalse(report['scored_validation_allowed'])
        self.assertEqual(report['protocol']['development_seeds'],list(DEV_SEEDS))
        self.assertEqual(report['selection_trajectories']['random']['gp_length_0p22']['prequential_forecast_count'],60)
        self.assertNotIn('selected_indices',raw)
        self.assertNotIn('raw_labels',raw)
        self.assertNotIn('source_col_0',raw)  # only anonymous aggregate source metadata, no specific rows

    def test_31_no_independent_validation_status(self):
        self.assertIn('DEV_ONLY_NOT_VALIDATED', STATUS)
        self.assertEqual(len(PREDICTORS),5)

if __name__=='__main__':unittest.main()
