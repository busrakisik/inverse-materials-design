"""Finite synthetic fixture only; NEVER independent BHS holdout seeds."""
import inspect
import math
import random
import unittest
from unittest.mock import patch
import numpy as np

from scripts.nist_anonymous_offline_pilot_v1 import (
    BUDGET, INITIAL, POLICIES, SEEDS, bhs_ei, campaign, choose_next,
    evaluate_development, expected_improvement, finite_pilot_pool,
    normalize_observed_initial, run_pinned_bytes,
)


def fixture():
    # Anonymous simplex coordinates; arbitrary synthetic scalar response.
    x=[]
    for i in range(7):
        for j in range(7-i):
            x.append((i/6,j/6,1-(i+j)/6))
    x=np.asarray(x,float)
    y=1.3 + x[:,0] - .3*x[:,1] + 2*x[:,0]*x[:,1]
    return x,y


def arrays():
    x,y=fixture()
    return {'C':x,'Kerr':y[:,None], 'Coer':np.zeros((len(y),1)),
            'XRD':np.zeros((len(y),2)), 'TTH':np.array([[10.,20.]])}


class NistAnonymousPilotTests(unittest.TestCase):
    def test_policies(self):
        self.assertEqual(len(POLICIES),4)
    def test_reserved_seeds_no_overlap(self):
        self.assertTrue(all(s < 10000 for s in SEEDS))
    def test_reject_reserved_seed(self):
        x,y=fixture()
        with self.assertRaises(ValueError): campaign(x,y,'random',10001)
    def test_evaluator_rejects_reserved_seed(self):
        x,y=fixture()
        with self.assertRaises(ValueError): evaluate_development(x,y,seeds=[10099])
    def test_pool_shapes(self):
        x,y,report=finite_pilot_pool(arrays())
        self.assertEqual(x.shape,(28,3));self.assertEqual(y.shape,(28,))
        self.assertFalse(report['element_order_verified'])
    def test_pool_percent_like(self):
        a=arrays();a['C']=a['C']*100
        x,y,r=finite_pilot_pool(a)
        self.assertTrue(np.allclose(x.sum(axis=1),1))
    def test_pool_transposed(self):
        a=arrays();a['C']=a['C'].T
        x,y,r=finite_pilot_pool(a)
        self.assertEqual(x.shape,(28,3))
    def test_pool_excludes_missing_labels_without_imputation(self):
        a=arrays();a['Kerr'][0,0]=float('nan')
        x,y,r=finite_pilot_pool(a)
        self.assertEqual(r['excluded_rows'],1)
        self.assertEqual(len(y),27)
    def test_pool_reject_wrong_fields(self):
        a=arrays();a.pop('Kerr')
        with self.assertRaises(ValueError):finite_pilot_pool(a)
    def test_pool_reject_unplausible_coords(self):
        a=arrays();a['C']*=7
        with self.assertRaises(ValueError):finite_pilot_pool(a)
    def test_ei_zero_uncertainty(self):
        self.assertTrue(np.allclose(expected_improvement([0,3],[0,0],1),[0,2]))
    def test_ei_positive(self):
        x=expected_improvement([0,1],[1,1],0)
        self.assertTrue(np.all(x>0))
    def test_ei_reject_negative_sigma(self):
        with self.assertRaises(ValueError):expected_improvement([0],[-1],0)
    def test_common_normalization_fixed(self):
        self.assertEqual(normalize_observed_initial([2,2,2]),(2,2))
    def test_choice_api_no_hidden_labels(self):
        self.assertNotIn('hidden_labels',inspect.signature(choose_next).parameters)
    def test_each_policy_no_repeat(self):
        x,y=fixture();sel=[0,1,2];z=np.array([1.,0.4,-.2])
        for policy in POLICIES:
            picked=choose_next(policy,x,sel,z,random.Random(7))
            self.assertNotIn(picked,sel)
    def test_every_campaign_budget(self):
        x,y=fixture()
        for policy in POLICIES:
            r=campaign(x,y,policy,7,budget=7)
            self.assertEqual(r['n_distinct_samples_acquired'],7)
            self.assertGreaterEqual(r['final_normalized_simple_regret'],0)
    def test_deterministic_seed(self):
        x,y=fixture()
        for policy in POLICIES:
            self.assertEqual(campaign(x,y,policy,7,budget=8),campaign(x,y,policy,7,budget=8))
    def test_hidden_labels_not_passed_to_selector(self):
        x,y=fixture();sel=[0,1,2];z=[0.,1.,-.5]
        first=choose_next('bhs_bma_ei',x,sel,z,random.Random(1))
        y[4:]+=1000000
        self.assertEqual(first,choose_next('bhs_bma_ei',x,sel,z,random.Random(1)))
    def test_comparison_has_four_policies(self):
        x,y=fixture()
        r=evaluate_development(x,y,seeds=(7,),budget=7)
        self.assertEqual(set(r),set(POLICIES))
        self.assertEqual(r['gp_ei']['replicate_count'],1)
    def test_no_source_data_export_in_code_contract(self):
        import scripts.nist_anonymous_offline_pilot_v1 as m
        code=inspect.getsource(m.run_pinned_bytes)
        self.assertNotIn('tolist()',code)
        self.assertIn('scored_validation_allowed',code)
    def test_invalid_budget(self):
        x,y=fixture()
        with self.assertRaises(ValueError):campaign(x,y,'random',7,budget=3)
    def test_invalid_policy(self):
        x,y=fixture()
        with self.assertRaises(ValueError):campaign(x,y,'unknown',7)
    def test_report_has_only_aggregate_diagnostics(self):
        # A synthetic MATLAB parse exercises the output boundary without raw source bytes.
        with patch('scripts.nist_anonymous_offline_pilot_v1.validate_source',return_value='a'*64), \
             patch('scripts.nist_anonymous_offline_pilot_v1.loadmat',return_value=arrays()):
            report=run_pinned_bytes(b'synthetic-only',seeds=(7,),budget=7)
        self.assertFalse(report['source_column_to_element_order_verified'])
        self.assertFalse(report['scored_validation_allowed'])
        self.assertFalse(report['independent_holdout_used'])
        self.assertEqual(set(report['policies']),set(POLICIES))
        self.assertNotIn('selected_indices',str(report))
        self.assertNotIn('raw_samples',str(report))

    def test_first_campaign_isolated_from_evaluation_labels_for_selector(self):
        # Label poisoning of an unobserved sample does not affect decision until query.
        x,y=fixture();selected=[1,2,3]
        revealed=np.array([y[i] for i in selected])
        center,scale=normalize_observed_initial(revealed)
        observed_z=(revealed-center)/scale
        i=choose_next('gp_ei',x,selected,observed_z,random.Random(7))
        poisoned=y.copy(); poisoned[[j for j in range(len(y)) if j not in selected]]=1e30
        revealed2=np.array([poisoned[j] for j in selected]); self.assertTrue(np.allclose(revealed,revealed2))
        j=choose_next('gp_ei',x,selected,(revealed2-center)/scale,random.Random(7))
        self.assertEqual(i,j)

    def test_no_physical_label_promotion(self):
        import scripts.nist_anonymous_offline_pilot_v1 as m
        self.assertIn('ANONYMOUS',m.STATUS)
        self.assertFalse(m.SEEDS[0] in range(10000,10100))
    def test_same_initialization_for_all_policies(self):
        # Initial indices are drawn before policy-specific selection occurs.
        code=inspect.getsource(campaign)
        self.assertLess(code.index('rng.sample'),code.index('choose_next'))


if __name__=='__main__':unittest.main()
