"""Synthetic-only contract, arithmetic and pre-reveal timing tests for NIST v4."""
import inspect
import json
import math
import random
import unittest
from unittest.mock import patch

import numpy as np

from scripts.nist_miscalibration_rootcause_v4 import (
    STATUS, PREDICTORS, DISTANCE_BOUNDS, TIME_SPLIT,
    EXTRA_DISCREPANCY_SD, V3_PARITY, V3_RUN_ID, V3_ARTIFACT_ID,
    predictive_variance_components, candidate_novelty, distance_category,
    diagnose_after_reveal, run_trajectory, summarize_all, _aggregate,
    evaluate_development, verify_v3_reproduction,
)
from scripts.nist_model_adequacy_v3 import (
    DEV_SEEDS, SELECTION_POLICIES, forecast_components,
    score_observation, trajectory as v3_trajectory,
)
from scripts.nist_anonymous_offline_pilot_v1 import INITIAL, BUDGET


def make_sample(n=29):
    rng=np.random.default_rng(52026)
    x=rng.dirichlet((2.,2.,2.),size=n)
    y=1.0 + 0.7*x[:,0] - 0.4*x[:,1] + 1.5*x[:,0]*x[:,1] + 0.15*np.sin(8*x[:,0])
    return x,y


def one_components(predictor='gp_length_0p22'):
    return predictor, (np.array([1.]),np.array([.5]),np.array([.25]))


class MiscalibrationRootcauseTests(unittest.TestCase):
    def setUp(self):
        self.x,self.y=make_sample()

    def test_01_three_fixed_predictors(self):
        self.assertEqual(PREDICTORS,('gp_length_0p22','bhs_bma_sigma_0p15','bhs_interaction_sigma_0p15'))
    def test_02_same_development_seeds(self):
        self.assertEqual(DEV_SEEDS,(7,13,23,31,41))
        self.assertTrue(all(not (10000<=i<=10099) for i in DEV_SEEDS))
    def test_03_same_selection_trajectories(self):
        self.assertEqual(SELECTION_POLICIES,('random','gp_ei','bhs_bma_ei'))
    def test_04_budget_constant(self):
        self.assertEqual((INITIAL,BUDGET,TIME_SPLIT),(3,15,6))
    def test_05_fixed_posthoc_grid(self):
        self.assertEqual(EXTRA_DISCREPANCY_SD,(0.,.5,1.,2.))
    def test_06_distance_thresholds(self):
        self.assertEqual(DISTANCE_BOUNDS,(.08,.20))
        self.assertEqual(distance_category(.079),'near')
        self.assertEqual(distance_category(.08),'middle')
        self.assertEqual(distance_category(.2),'far')
    def test_07_distance_rejects_invalid(self):
        for x in (-.1,float('nan'),float('inf')):
            with self.assertRaises(ValueError): distance_category(x)
    def test_08_distance_exact_simplex(self):
        x=np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
        self.assertAlmostEqual(candidate_novelty(x,[0,1],2),math.sqrt(2))
    def test_09_distance_reject_duplicate_candidate(self):
        with self.assertRaises(ValueError): candidate_novelty(self.x,[0,1],1)
    def test_10_distance_reject_empty_history(self):
        with self.assertRaises(ValueError): candidate_novelty(self.x,[],2)
    def test_11_decomposition_single_gp(self):
        pred,components=one_components()
        v=predictive_variance_components(pred,*components)
        self.assertAlmostEqual(v['assumed_noise_variance'],.0225)
        self.assertAlmostEqual(v['within_family_variance'],.2275)
        self.assertAlmostEqual(v['between_family_variance'],0.)
        self.assertAlmostEqual(v['total_predictive_variance'],.25)
    def test_12_decomposition_mixture_between_family(self):
        w=np.array([.25,.75]); means=np.array([0.,2.]); var=np.array([.25,.65])
        s=predictive_variance_components('bhs_bma_sigma_0p15',w,means,var)
        self.assertAlmostEqual(s['predictive_mean'],1.5)
        self.assertAlmostEqual(s['between_family_variance'],.75)
        self.assertAlmostEqual(s['total_predictive_variance'],1.3)
        self.assertAlmostEqual(s['within_family_variance'],1.3-.75-.0225)
    def test_13_reject_variance_smaller_than_assumed_noise(self):
        with self.assertRaises(ValueError):
            predictive_variance_components('gp_length_0p22',[1.],[0.],[.01])
    def test_14_reject_bad_mixture_weights(self):
        with self.assertRaises(ValueError):
            predictive_variance_components('bhs_bma_sigma_0p15',[.5,.6],[0.,1.],[.2,.2])
    def test_15_reject_unknown_predictor(self):
        with self.assertRaises(ValueError):
            predictive_variance_components('physical_truth',[1.],[0.],[.25])
    def test_16_reject_nonfinite_mixture(self):
        with self.assertRaises(ValueError):
            predictive_variance_components('gp_length_0p22',[1.],[float('nan')],[.25])
    def test_17_post_reveal_matches_v3_base_score(self):
        pred,components=one_components()
        actual=diagnose_after_reveal(pred,.3,components,.03,1)
        reference=score_observation(.3,*components)
        self.assertAlmostEqual(actual['nlpd'],reference['nlpd'])
        self.assertEqual(actual['covered_90'],reference['covered_90'])
        self.assertAlmostEqual(actual['interval_width_90'],reference['interval_width_90'])
    def test_18_zero_extra_discrepancy_is_exact(self):
        pred,components=one_components('bhs_bma_sigma_0p15')
        actual=diagnose_after_reveal(pred,1.1,components,.15,8)
        self.assertAlmostEqual(actual['discrepancy_sensitivity']['0.0']['nlpd'],actual['nlpd'])
        self.assertEqual(actual['discrepancy_sensitivity']['0.0']['covered_90'],actual['covered_90'])
    def test_19_extra_variance_increases_interval_width(self):
        pred,components=one_components()
        actual=diagnose_after_reveal(pred,1.1,components,.03,1)
        self.assertLess(actual['discrepancy_sensitivity']['0.0']['width_90'],
                        actual['discrepancy_sensitivity']['2.0']['width_90'])
    def test_20_distance_and_phase_group_assignment(self):
        pred,components=one_components()
        early=diagnose_after_reveal(pred,.3,components,.01,6)
        late=diagnose_after_reveal(pred,.3,components,.25,7)
        self.assertEqual((early['time_category'],early['distance_category']),('early','near'))
        self.assertEqual((late['time_category'],late['distance_category']),('late','far'))
    def test_21_reject_ordinal(self):
        pred,components=one_components()
        with self.assertRaises(ValueError):diagnose_after_reveal(pred,.3,components,.02,0)
        with self.assertRaises(ValueError):diagnose_after_reveal(pred,.3,components,.02,13)
    def test_22_forecast_api_is_observed_only(self):
        params=inspect.signature(forecast_components).parameters
        self.assertEqual(list(params),['predictor','candidates','selected','observed_z','candidate_index'])
        self.assertNotIn('hidden_labels',params)
    def test_23_trajectory_has_twelve_forecasts_each(self):
        r=run_trajectory(self.x,self.y,'random',7)
        self.assertEqual(set(r),set(PREDICTORS))
        self.assertTrue(all(len(q)==12 for q in r.values()))
    def test_24_v3_prequential_parity_on_synthetic(self):
        for policy in SELECTION_POLICIES:
            old=v3_trajectory(self.x,self.y,policy,7)
            new=run_trajectory(self.x,self.y,policy,7)
            for pred in PREDICTORS:
                self.assertEqual(len(new[pred]),len(old[pred]))
                for a,b in zip(new[pred],old[pred]):
                    self.assertAlmostEqual(a['nlpd'],b['nlpd'],places=9)
                    self.assertEqual(a['covered_90'],b['covered_90'])
    def test_25_no_forecast_after_label_reveal(self):
        events=[]
        original=forecast_components
        original_diag=diagnose_after_reveal
        def f(*args):
            events.append('forecast')
            return original(*args)
        def d(*args):
            events.append('diagnose')
            return original_diag(*args)
        with patch('scripts.nist_miscalibration_rootcause_v4.forecast_components',side_effect=f), \
             patch('scripts.nist_miscalibration_rootcause_v4.diagnose_after_reveal',side_effect=d):
            run_trajectory(self.x,self.y,'random',7)
        self.assertEqual(events[:6],['forecast','forecast','forecast','diagnose','diagnose','diagnose'])
        self.assertEqual(len(events),12*6)
    def test_26_reject_invalid_seed(self):
        for seed in (10000,10099,-1):
            with self.assertRaises(ValueError):run_trajectory(self.x,self.y,'random',seed)
    def test_27_reject_unknown_selection_policy(self):
        with self.assertRaises(ValueError):run_trajectory(self.x,self.y,'future_label_oracle',7)
    def test_28_reject_invalid_candidate_pool(self):
        bad=self.x.copy();bad[0,0]=10.
        with self.assertRaises(ValueError):run_trajectory(bad,self.y,'random',7)
    def test_29_empty_bin_does_not_fake_a_metric(self):
        a=_aggregate([])
        self.assertEqual(a['count'],0)
        self.assertIsNone(a['mean_90pct_coverage'])
    def test_30_aggregate_count_and_no_per_row_output(self):
        traces={'random':[run_trajectory(self.x,self.y,'random',7)]}
        data=summarize_all(traces)
        gp=data['random']['gp_length_0p22']
        self.assertEqual(gp['count'],12)
        self.assertEqual(sum(q['count'] for q in gp['by_nearest_coordinate_distance'].values()),12)
        self.assertEqual(gp['by_acquisition_phase']['early']['count'],6)
        self.assertEqual(gp['by_acquisition_phase']['late']['count'],6)
        self.assertEqual(gp['development_seed_count'],1)
        payload=json.dumps(data,allow_nan=False)
        for forbidden in ('selected_indices','raw_labels','raw_measurements','per_step_forecasts','revealed_y'):
            self.assertNotIn(forbidden,payload)
    def test_31_aggregate_variance_identity(self):
        data=summarize_all({'random':[run_trajectory(self.x,self.y,'random',7)]})
        for p in PREDICTORS:
            v=data['random'][p]
            self.assertAlmostEqual(v['mean_total_variance'],
                v['mean_assumed_noise_variance']+v['mean_within_family_variance']+v['mean_between_family_variance'],places=9)
    def test_32_aggregate_is_deterministic(self):
        a=evaluate_development(self.x,self.y,seeds=(7,))
        b=evaluate_development(self.x,self.y,seeds=(7,))
        self.assertEqual(a,b)
    def test_33_regression_numbers_complete(self):
        self.assertEqual(set(V3_PARITY),set(SELECTION_POLICIES))
        self.assertTrue(all(set(v)==set(PREDICTORS) for v in V3_PARITY.values()))
        self.assertEqual((V3_RUN_ID,V3_ARTIFACT_ID),(41992614426,13397919991))
    def test_34_regression_parity_detection(self):
        report={'selection_trajectories':{p:{k:{'mean_nlpd':v[0],
              'mean_90pct_coverage':v[1]} for k,v in m.items()} for p,m in V3_PARITY.items()}}
        self.assertTrue(verify_v3_reproduction(report))
        report['selection_trajectories']['random']['gp_length_0p22']['mean_nlpd']+=.001
        with self.assertRaises(ValueError):verify_v3_reproduction(report)
    def test_35_fail_closed_status(self):
        self.assertIn('POSTHOC_NOT_VALIDATED',STATUS)
    def test_36_no_use_independent_holdout_seeds(self):
        self.assertNotIn(10000,DEV_SEEDS)
        self.assertNotIn(10099,DEV_SEEDS)


if __name__=='__main__':unittest.main()
