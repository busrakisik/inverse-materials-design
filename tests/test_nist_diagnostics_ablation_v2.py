"""Synthetic development unit/contract checks; never run BHS independent holdout."""
import inspect
import json
import math
import random
import unittest
from unittest.mock import patch

import numpy as np

from scripts.nist_diagnostics_ablation_v2 import (
    STATUS, POLICIES, DEV_SEEDS, REPORT_BUDGETS,
    anonymous_features, bhs_ablation_scores, gp_scores_at_lengthscale,
    select_ablation, campaign_diagnostic, evaluate_ablation,
    summarize_paired, validate_dev_protocol,
    V1_PRIOR_REPORTED_MEAN_REGRET,
)
from scripts.multivariate_hypotheses_v1 import features, MODELS
from scripts.nist_anonymous_offline_pilot_v1 import (
    bhs_ei, gp_predict, campaign, POLICIES as OLD_POLICIES,
)


def sample(n=34):
    rng = np.random.default_rng(2026)
    x = rng.dirichlet([2, 2, 2], size=n)
    y = 0.2 + .6*x[:,0] - .3*x[:,1] + 1.2*x[:,0]*x[:,1] + .12*np.sin(6*x[:,0])
    return x, y


class NistDiagnosticsAblationTests(unittest.TestCase):
    def setUp(self):
        self.x, self.y = sample()

    def test_01_policies_complete(self):
        self.assertEqual(len(POLICIES),11)
        self.assertEqual(len(set(POLICIES)),len(POLICIES))
        self.assertEqual(tuple(POLICIES[:4]),OLD_POLICIES)

    def test_02_development_seeds_never_reserved(self):
        self.assertEqual(DEV_SEEDS,(7,13,23,31,41))
        self.assertTrue(validate_dev_protocol())
        self.assertTrue(all(s not in range(10000,10100) for s in DEV_SEEDS))

    def test_03_reject_reserved_seed(self):
        with self.assertRaises(ValueError): validate_dev_protocol((10000,))
        with self.assertRaises(ValueError): validate_dev_protocol((10099,))

    def test_04_reject_duplicated_seeds(self):
        with self.assertRaises(ValueError): validate_dev_protocol((7,7))

    def test_05_reject_invalid_budget(self):
        with self.assertRaises(ValueError): validate_dev_protocol((7,),14)

    def test_06_basis_matches_v1(self):
        for mode in MODELS:
            got=anonymous_features(mode,self.x)
            expected=np.stack([features(mode,row) for row in self.x])
            np.testing.assert_allclose(got,expected,rtol=0,atol=5e-15)

    def test_07_basis_opaque_coordinates_reject_bad(self):
        with self.assertRaises(ValueError):anonymous_features('linear',np.array([[.5,.5,.5]]))
        with self.assertRaises(ValueError):anonymous_features('linear',np.array([[.5,.5,float('nan')]]))

    def test_08_basis_reject_unknown_family(self):
        with self.assertRaises(ValueError):anonymous_features('invented',self.x)

    def test_09_vectorized_bma_ei_matches_v1(self):
        inds=[0,2,7]
        observed=np.array([.3,.1,.2])
        ref=bhs_ei(self.x,inds,observed)
        got=bhs_ablation_scores(self.x,inds,observed)
        np.testing.assert_allclose(got,ref,rtol=1e-9,atol=1e-9)

    def test_10_single_family_scores_finite(self):
        for m in MODELS:
            got=bhs_ablation_scores(self.x,[0,1,2],[.1,.2,.3],m)
            self.assertEqual(got.shape,(len(self.x),))
            self.assertTrue(np.isfinite(got).all())
            self.assertTrue(np.all(got>=0))

    def test_11_nominal_noise_sensitivity_is_distinct(self):
        a=bhs_ablation_scores(self.x,[0,2,7],[.3,.1,.2],sigma=.05)
        b=bhs_ablation_scores(self.x,[0,2,7],[.3,.1,.2],sigma=.30)
        self.assertGreater(np.max(abs(a-b)),1e-5)

    def test_12_reject_invalid_sigma(self):
        with self.assertRaises(ValueError):bhs_ablation_scores(self.x,[0],[.1],sigma=0.)
        with self.assertRaises(ValueError):bhs_ablation_scores(self.x,[0],[.1],sigma=float('nan'))

    def test_13_reject_unobserved_or_inconsistent(self):
        with self.assertRaises(ValueError):bhs_ablation_scores(self.x,[0,1],[.1])
        with self.assertRaises(ValueError):bhs_ablation_scores(self.x,[0,0],[.1,.2])

    def test_14_default_gp_matches_v1(self):
        inds=[1,2,3]
        obs=np.array([.4,.2,.3])
        a=gp_scores_at_lengthscale(self.x,inds,obs,.22)
        b=gp_predict(self.x,inds,obs)
        for aa,bb in zip(a,b):np.testing.assert_allclose(aa,bb,atol=0,rtol=0)

    def test_15_gp_scale_sensitivity(self):
        inds=[0,1,2]
        z=np.array([.1,.2,.3])
        a,_=gp_scores_at_lengthscale(self.x,inds,z,.12)
        b,_=gp_scores_at_lengthscale(self.x,inds,z,.40)
        self.assertGreater(np.max(abs(a-b)),1e-5)

    def test_16_gp_reject_invalid_lengthscale(self):
        with self.assertRaises(ValueError):gp_scores_at_lengthscale(self.x,[0],[.1],-1.)

    def test_17_policy_api_cannot_access_oracle(self):
        params=list(inspect.signature(select_ablation).parameters)
        self.assertEqual(params,['policy','candidates','selected','observed_z','rng'])
        self.assertNotIn('hidden_labels',params)

    def test_18_selection_no_repeats(self):
        for p in POLICIES:
            i=select_ablation(p,self.x,[0,1,2],[.1,.2,.3],random.Random(7))
            self.assertTrue(3 <= i < len(self.x),p)

    def test_19_previously_reported_four_policy_regret_reproduction(self):
        for p in OLD_POLICIES:
            current=campaign_diagnostic(self.x,self.y,p,7)
            old=campaign(self.x,self.y,p,7)
            self.assertAlmostEqual(current['regret_by_budget']['15'],old['final_normalized_simple_regret'],places=13)

    def test_20_budget_checkpoints_monotone(self):
        for p in POLICIES:
            vals=campaign_diagnostic(self.x,self.y,p,7)['regret_by_budget']
            self.assertEqual(set(map(int,vals)),set(REPORT_BUDGETS))
            self.assertGreaterEqual(vals['5']+1e-12,vals['10'])
            self.assertGreaterEqual(vals['10']+1e-12,vals['15'])

    def test_21_invalid_policy_rejected(self):
        with self.assertRaises(ValueError):campaign_diagnostic(self.x,self.y,'oracle',7)

    def test_22_hidden_label_not_given_at_decision_time(self):
        seen=[]
        original=select_ablation
        def interceptor(policy,x,selected,z,rng):
            seen.append((list(selected),list(z)))
            return original(policy,x,selected,z,rng)
        with patch('scripts.nist_diagnostics_ablation_v2.select_ablation',side_effect=interceptor):
            campaign_diagnostic(self.x,self.y,'gp_ei',7)
        self.assertEqual(len(seen),12)
        self.assertEqual(len(seen[0][0]),3)
        self.assertEqual(len(seen[-1][0]),14)
        self.assertTrue(all(len(s)==len(z) for s,z in seen))

    def test_23_paired_stats_correct(self):
        def a(r):return {'regret_by_budget':{'5':r,'10':r/2,'15':r/3}}
        arr={p:[a(.3),a(.9)] for p in POLICIES}
        arr['bhs_bma_ei']=[a(.6),a(.3)]
        # Need family posteriors for all BHS variants, and weights for bma.
        for p in POLICIES:
            for row in arr[p]:
                if p.startswith('bhs_'):
                    row['final_posterior_effective_family_count']=2.
                    if p in ('bhs_bma_ei','bhs_bma_sigma_0p05','bhs_bma_sigma_0p30'):
                        row['final_model_weights']={m:1./3 for m in MODELS}
        report=summarize_paired(arr)
        self.assertEqual(report['gp_ei']['paired_final_win_tie_loss_vs_gp_ei'],{'better':0,'tie':2,'worse':0})
        self.assertEqual(report['bhs_bma_ei']['paired_final_win_tie_loss_vs_gp_ei'],{'better':1,'tie':0,'worse':1})
        self.assertAlmostEqual(report['bhs_bma_ei']['mean_paired_final_regret_minus_gp_ei'],-.05)

    def test_24_full_synthetic_aggregate_no_raw_indices(self):
        report=evaluate_ablation(self.x,self.y,seeds=(7,13))
        self.assertEqual(len(report),len(POLICIES))
        self.assertEqual(report['gp_ei']['replicate_count'],2)
        self.assertTrue(all(v['normalized_regret_by_budget']['15']['mean']>=0 for v in report.values()))
        self.assertNotIn('selected_indices',json.dumps(report))
        self.assertNotIn('raw_measurements',json.dumps(report))

    def test_25_deterministic_campaign(self):
        a=campaign_diagnostic(self.x,self.y,'bhs_bma_sigma_0p30',7)
        b=campaign_diagnostic(self.x,self.y,'bhs_bma_sigma_0p30',7)
        self.assertEqual(a,b)

    def test_26_model_entropy_in_range(self):
        r=campaign_diagnostic(self.x,self.y,'bhs_bma_ei',7)
        self.assertGreaterEqual(r['final_posterior_effective_family_count'],1.)
        self.assertLessEqual(r['final_posterior_effective_family_count'],3.00001)
        self.assertAlmostEqual(sum(r['final_model_weights'].values()),1.)

    def test_27_provenance_of_locked_prior_v1_numbers(self):
        self.assertEqual(set(V1_PRIOR_REPORTED_MEAN_REGRET),set(OLD_POLICIES))
        self.assertAlmostEqual(V1_PRIOR_REPORTED_MEAN_REGRET['gp_ei'],0.025001283117256388)
        self.assertAlmostEqual(V1_PRIOR_REPORTED_MEAN_REGRET['bhs_bma_ei'],0.13924593765076626)

    def test_28_no_independent_validation_claim(self):
        self.assertIn('EXPLORATORY_NOT_VALIDATED',STATUS)
        self.assertNotIn(10000,DEV_SEEDS)
        self.assertNotIn(10099,DEV_SEEDS)

if __name__ == '__main__':unittest.main()
