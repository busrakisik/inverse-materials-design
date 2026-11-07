"""Adversarial manufactured-design contracts; no physical outcome data."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.bhs_v128_design_estimability import (
    FIXTURE_PATH, DesignContractError, audit_plan, audit_plan_bytes,
    main, parse_plan, _exact_rank,
)


def fixture():
    return json.loads(FIXTURE_PATH.read_text())


def dump(obj):
    return (json.dumps(obj, sort_keys=True, allow_nan=False) + '\n').encode()


class PhysicalDesignContracts(unittest.TestCase):
    def test_frozen_manufactured_fixture_is_estimable_but_no_go(self):
        raw = FIXTURE_PATH.read_bytes()
        report = audit_plan_bytes(raw)
        self.assertEqual(report['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertTrue(report['linear_contrast_estimable_under_declared_nuisance'])
        self.assertEqual(report['specimen_rows'], 8)
        self.assertEqual(report['synthesis_batch_count'], 4)
        self.assertEqual(report['measurement_session_count'], 2)
        self.assertEqual(report['planned_technical_traces'], 24)
        self.assertEqual(report['nuisance_rank'], 7)
        self.assertEqual(report['full_rank'], 8)
        self.assertEqual(report['residual_degrees_of_freedom'], 0)
        self.assertIn('NO_RESIDUAL_DEGREES_OF_FREEDOM', report['blocking_conditions'])
        self.assertNotIn('ARM_POSITION_IMBALANCE:S1', report['blocking_conditions'])
        self.assertFalse(report['physical_recommendation_allowed'])
        self.assertFalse(report['independent_physical_validation_established'])

    def test_repeated_traces_are_not_new_independent_coupons(self):
        obj = fixture()
        for row in obj['specimens']:
            row['planned_moke_traces'] = 30
        report = audit_plan(obj)
        self.assertEqual(report['specimen_rows'], 8)
        self.assertEqual(report['synthesis_batch_count'], 4)
        self.assertEqual(report['planned_technical_traces'], 240)
        self.assertEqual(report['residual_degrees_of_freedom'], 0)

    def test_processing_confounded_with_synthesis_batches(self):
        obj = fixture()
        for row in obj['specimens']:
            row['processing_arm'] = ('reference' if row['synthesis_batch_id']
                                     in ('B01', 'B02') else 'modified')
        result = audit_plan(obj)
        self.assertFalse(result['linear_contrast_estimable_under_declared_nuisance'])
        self.assertTrue(any(x.startswith('UNPAIRED_SYNTHESIS_BATCH:')
                            for x in result['blocking_conditions']))
        self.assertIn('PROCESSING_CONTRAST_CONFOUNDED_WITH_NUISANCE',
                      result['blocking_conditions'])

    def test_processing_confounded_with_measurement_session(self):
        obj = fixture()
        position = {'S1': 0, 'S2': 0}
        for row in obj['specimens']:
            row['moke_session_id'] = 'S1' if row['processing_arm']=='reference' else 'S2'
            session = row['moke_session_id']
            position[session] += 1
            row['planned_position'] = position[session]
        result = audit_plan(obj)
        self.assertFalse(result['linear_contrast_estimable_under_declared_nuisance'])
        self.assertIn('SINGLE_ARM_MEASUREMENT_SESSION:S1', result['blocking_conditions'])
        self.assertIn('SINGLE_ARM_MEASUREMENT_SESSION:S2', result['blocking_conditions'])

    def test_arm_order_imbalance_flagged_even_if_rank_sufficient(self):
        obj = fixture()
        for session in ('S1','S2'):
            rows = [r for r in obj['specimens'] if r['moke_session_id']==session]
            rows.sort(key=lambda x: x['processing_arm'], reverse=True)
            for idx, row in enumerate(rows, 1):
                row['planned_position'] = idx
        report = audit_plan(obj)
        self.assertIn('ARM_POSITION_IMBALANCE:S1', report['blocking_conditions'])
        self.assertIn('ARM_POSITION_IMBALANCE:S2', report['blocking_conditions'])

    def test_duplicate_coupon_and_session_slot_rejected(self):
        obj = fixture()
        obj['specimens'][1]['coupon_id'] = obj['specimens'][0]['coupon_id']
        with self.assertRaisesRegex(DesignContractError,'DUPLICATED_SPECIMEN'):
            audit_plan(obj)
        obj = fixture()
        obj['specimens'][3]['planned_position'] = 1
        with self.assertRaisesRegex(DesignContractError,'SESSION_SLOT'):
            audit_plan(obj)

    def test_unrecorded_source_outcomes_and_extra_keys_rejected(self):
        obj = fixture()
        obj['specimens'][0]['measured_coercive_field'] = 23.4
        with self.assertRaisesRegex(DesignContractError,'INVALID_SPECIMEN_SCHEMA'):
            audit_plan(obj)
        obj = fixture()
        obj['evaluation_regret'] = 0
        with self.assertRaisesRegex(DesignContractError,'INVALID_PLAN_SCHEMA'):
            audit_plan(obj)

    def test_tampered_schema_or_claims_rejected(self):
        for key, val in [('status','laboratory_approved'),
                         ('response_unit','Oe'),('independent_unit','moke_trace')]:
            obj = fixture()
            obj[key] = val
            with self.subTest(key=key),self.assertRaises(DesignContractError):
                audit_plan(obj)
        for flag in ('raw_outcomes_present','physical_action_allowed',
                     'external_investigator_approval_verified',
                     'measurement_calibration_independently_verified',
                     'randomization_independently_verified',
                     'processing_conditions_physically_approved'):
            obj = fixture()
            obj[flag] = True
            with self.subTest(flag=flag),self.assertRaises(DesignContractError):
                audit_plan(obj)

    def test_no_structural_or_magnetic_raw_record_flag_rejected(self):
        for field in ('xrd_planned','moke_raw_trace_retention'):
            obj = fixture()
            obj['specimens'][0][field]=False
            with self.subTest(field=field),self.assertRaises(DesignContractError):
                audit_plan(obj)

    def test_invalid_sequence_and_nonpositive_trace_count(self):
        for field,value in [('planned_position',0),('planned_position',True),
                            ('planned_moke_traces',0),('planned_moke_traces',1.1)]:
            obj = fixture()
            obj['specimens'][0][field] = value
            with self.subTest(field=field,value=value),self.assertRaises(DesignContractError):
                audit_plan(obj)

    def test_nonfinite_threshold_and_bool_are_not_real_measurements(self):
        for value in (0, -5.0, float('nan'), float('inf'), True):
            obj = fixture()
            obj['reviewed_minimum_effect_A_per_m']=value
            with self.subTest(value=value),self.assertRaises(DesignContractError):
                audit_plan(obj)
        obj=fixture()
        obj['reviewed_minimum_effect_A_per_m']=125.0
        report=audit_plan(obj)
        self.assertNotIn('PHYSICAL_MINIMUM_MEANINGFUL_EFFECT_UNSET', report['blocking_conditions'])
        self.assertFalse(report['laboratory_action_allowed'])

    def test_missing_group_labels_and_unknown_arm_rejected(self):
        for key,value in [('synthesis_batch_id',''),('moke_session_id',''),
                          ('processing_arm','other')]:
            obj=fixture()
            obj['specimens'][0][key]=value
            with self.subTest(key=key),self.assertRaises(DesignContractError):
                audit_plan(obj)

    def test_too_few_independent_synthesis_batches_fails(self):
        obj=fixture()
        for row in obj['specimens']:
            row['synthesis_batch_id']='B01'
        with self.assertRaisesRegex(DesignContractError,'INSUFFICIENT_BATCH'):
            audit_plan(obj)

    def test_exact_rational_rank_invariance_and_known_values(self):
        self.assertEqual(_exact_rank([[1,0],[0,1],[1,1]]),2)
        self.assertEqual(_exact_rank([[1,2],[2,4],[3,6]]),1)
        self.assertEqual(_exact_rank([[1,1,1],[1,2,4]]),2)
        self.assertEqual(_exact_rank([[1,1,1],[1,2,4]][::-1]),2)
        self.assertEqual(_exact_rank([[1,1,1],[1,2,4],[1,3,9]]),3)

    def test_duplicate_json_key_nonfinite_json_and_invalid_bytes(self):
        with self.assertRaisesRegex(DesignContractError, 'DUPLICATE_JSON_KEY'):
            parse_plan(b'{"x":1,"x":2}')
        with self.assertRaises(DesignContractError):
            parse_plan(b'{"x":NaN}')
        with self.assertRaises(DesignContractError):
            parse_plan(b'')
        with self.assertRaises(DesignContractError):
            parse_plan(b'x'*210_000)

    def test_fixture_permutation_does_not_change_rank(self):
        obj=fixture()
        rank=audit_plan(obj)
        obj['specimens'].reverse()
        other=audit_plan(obj)
        self.assertEqual(rank['nuisance_rank'],other['nuisance_rank'])
        self.assertEqual(rank['full_rank'],other['full_rank'])
        self.assertEqual(rank['blocking_conditions'],other['blocking_conditions'])

    def test_source_digest_changes_when_plan_modified(self):
        obj=fixture()
        original=audit_plan_bytes(dump(obj))
        obj['specimens'][0]['planned_moke_traces']+=1
        altered=audit_plan_bytes(dump(obj))
        self.assertNotEqual(original['source_sha256'],altered['source_sha256'])
        self.assertFalse(altered['physical_recommendation_allowed'])

    def test_cli_explicit_output_and_default_no_source_access(self):
        self.assertEqual(main([]), 0)
        with TemporaryDirectory() as td:
            target=Path(td)/'report.json'
            self.assertEqual(main(['--plan',str(FIXTURE_PATH),'--out',str(target)]),0)
            x=json.loads(target.read_text())
            self.assertEqual(x['status'],'NO_GO_PHYSICAL_DESIGN_NOT_EXTERNALLY_VALIDATED')
            self.assertFalse(x['independent_physical_validation_established'])
            self.assertEqual(x['specimen_rows'],8)

if __name__=='__main__':
    unittest.main()
