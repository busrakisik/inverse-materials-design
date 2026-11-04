import math
import unittest

from scripts.reliability_gated_design_v1 import (
    ALLOWED_PROVENANCE, STATUS, ReliabilityGatedCostPolicyV1, development_demo,
    retrospective_diagnostics, validate_history, validate_protocol,
)


class ReliabilityGatedDesignTests(unittest.TestCase):
    def setUp(self):
        self.public={'a':(-1.,),'b':(-.5,),'c':(0.,),'d':(.5,),'e':(1.,)}
        self.plan={cid:{'measurement_std':.15,'cost':1.,
                        'provenance':'instrument_calibrated_synthetic'}
                   for cid in self.public}

    def test_protocol_exact_coverage(self):
        xs, plan=validate_protocol(self.public,self.plan)
        self.assertEqual(len(xs),5)
        self.assertEqual(len(plan),5)

    def test_metadata_missing_rejected(self):
        p=dict(self.plan);p.pop('a')
        with self.assertRaises(ValueError):validate_protocol(self.public,p)

    def test_metadata_extra_rejected(self):
        p=dict(self.plan);p['extra']=self.plan['a']
        with self.assertRaises(ValueError):validate_protocol(self.public,p)

    def test_unapproved_provenance_rejected(self):
        p={k:dict(v) for k,v in self.plan.items()};p['a']['provenance']='trusted'
        with self.assertRaises(ValueError):validate_protocol(self.public,p)

    def test_invalid_uncertainty_rejected(self):
        for bad in (0.,-1.,float('nan'),True):
            p={k:dict(v) for k,v in self.plan.items()};p['a']['measurement_std']=bad
            with self.assertRaises(ValueError):validate_protocol(self.public,p)

    def test_invalid_cost_rejected(self):
        for bad in (0.,-1.,float('inf'),True):
            p={k:dict(v) for k,v in self.plan.items()};p['a']['cost']=bad
            with self.assertRaises(ValueError):validate_protocol(self.public,p)

    def test_duplicate_observation_rejected(self):
        with self.assertRaises(ValueError):
            validate_history(self.public,self.plan,[('a',1.,.15,ALLOWED_PROVENANCE[0])]*2)

    def test_unknown_observation_rejected(self):
        with self.assertRaises(ValueError):
            validate_history(self.public,self.plan,[('unknown',1.,.15,ALLOWED_PROVENANCE[0])])

    def test_mismatched_std_rejected(self):
        with self.assertRaises(ValueError):
            validate_history(self.public,self.plan,[('a',1.,.2,ALLOWED_PROVENANCE[0])])

    def test_unapproved_history_rejected(self):
        with self.assertRaises(ValueError):
            validate_history(self.public,self.plan,[('a',1.,.15,'unverified')])

    def test_nonfinite_value_rejected(self):
        with self.assertRaises(ValueError):
            validate_history(self.public,self.plan,[('a',float('nan'),.15,ALLOWED_PROVENANCE[0])])

    def test_determinism(self):
        a=ReliabilityGatedCostPolicyV1(quantiles=8)
        b=ReliabilityGatedCostPolicyV1(quantiles=8)
        self.assertEqual(a.choose(self.public,[],self.plan),b.choose(self.public,[],self.plan))
        self.assertEqual(a.last_diagnostics,b.last_diagnostics)

    def test_excludes_measured_candidates(self):
        p=ReliabilityGatedCostPolicyV1(quantiles=8)
        first=p.choose(self.public,[],self.plan)
        other=p.choose(self.public,[(first,.3,.15,ALLOWED_PROVENANCE[0])],self.plan)
        self.assertNotEqual(first,other)

    def test_cost_changes_decision_when_identical_candidates(self):
        public={'cheap':(1.,),'expensive':(1.,)}
        plan={k:{'measurement_std':.15,'cost':1. if k=='cheap' else 10.,
                 'provenance':ALLOWED_PROVENANCE[0]} for k in public}
        p=ReliabilityGatedCostPolicyV1(quantiles=8)
        self.assertEqual(p.choose(public,[],plan),'cheap')

    def test_uncertainty_changes_information_gain(self):
        public={'low_noise':(-1.,),'high_noise':(-1.,)}
        plan={k:{'measurement_std':.05 if k=='low_noise' else 5.,'cost':1.,
                 'provenance':ALLOWED_PROVENANCE[0]} for k in public}
        p=ReliabilityGatedCostPolicyV1(quantiles=16)
        self.assertEqual(p.choose(public,[],plan),'low_noise')

    def test_invalid_objective(self):
        with self.assertRaises(ValueError):ReliabilityGatedCostPolicyV1(objective='trust_penalty')

    def test_empty_history_no_audit(self):
        self.assertIsNone(retrospective_diagnostics(self.public,[],self.plan))

    def test_retro_audit_descriptive(self):
        r=retrospective_diagnostics(self.public,[('a',.6,.15,ALLOWED_PROVENANCE[0])],self.plan)
        self.assertEqual(r['count'],1)
        self.assertFalse(r['validated_detector'])

    def test_fail_closed_diagnostics(self):
        p=ReliabilityGatedCostPolicyV1(quantiles=8)
        p.choose(self.public,[],self.plan)
        d=p.last_diagnostics
        self.assertFalse(d['validated_reliability_detector'])
        self.assertFalse(d['scientific_optimality_established'])
        self.assertFalse(d['scored_validation_allowed'])

    def test_demo_reproducible(self):
        self.assertEqual(development_demo(),development_demo())

    def test_demo_holdout_excluded(self):
        r=development_demo()
        self.assertEqual(len(r['trace']),5)
        self.assertFalse(r['independent_holdout_used'])
        self.assertFalse(r['scored_validation_allowed'])

    def test_eig_comparator_reported(self):
        r=development_demo()
        self.assertTrue(all('eig_only_candidate_same_history' in row for row in r['trace']))

if __name__=='__main__':unittest.main()
