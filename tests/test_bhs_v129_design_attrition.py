"""Falsification-oriented tests for the outcome-free V12.9 design audit."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.bhs_v128_design_estimability import audit_plan_bytes
from scripts.bhs_v129_design_attrition import (
    AttritionContractError, VARIANTS, audit_bundle, audit_bundle_bytes,
    main, model_summary, parse_bundle,
)

DESIGNS = Path('research/BHS_V129_DESIGN_VARIANTS.json')
ORIGINAL = Path('research/BHS_V128_MANUFACTURED_DESIGN_FIXTURE.json')


def fixture():
    return json.loads(DESIGNS.read_text(encoding='utf-8'))


class DesignAttritionContracts(unittest.TestCase):
    def test_both_fixture_structures_validate_but_never_authorize_laboratory_use(self):
        source = DESIGNS.read_bytes()
        result = audit_bundle_bytes(source)
        self.assertEqual(result['source_sha256'], hashlib.sha256(source).hexdigest())
        self.assertEqual(set(result['variants']), set(VARIANTS))
        for variant in result['variants'].values():
            full = variant['full_design']
            self.assertEqual(full['coupon_rows'], 16)
            self.assertEqual(full['named_batch_count'], 8)
            self.assertEqual(full['session_count'], 2)
            self.assertEqual(full['fully_paired_batch_count'], 8)
            self.assertEqual(full['both_arm_session_count'], 2)
            self.assertTrue(full['linear_treatment_estimable'])
            self.assertGreater(full['residual_row_degrees_of_freedom'], 0)
            self.assertEqual(full['technical_trace_count'], 48)
            self.assertFalse(variant['physical_recommendation_allowed'])
        self.assertFalse(result['physical_recommendation_allowed'])
        self.assertFalse(result['laboratory_action_allowed'])
        self.assertFalse(result['formal_power_or_precision_established'])
        self.assertFalse(result['statistical_risk_guarantee_supported'])
        self.assertFalse(result['independent_physical_validation_established'])
        self.assertEqual(result['status'], 'NO_GO_EXTERNAL_LAB_AND_PRECISION_REVIEW_REQUIRED')

    def test_declared_full_rank_and_row_degrees_of_freedom(self):
        r = audit_bundle(fixture())['variants']
        a = r['cross_session_pairs']['full_design']
        b = r['within_session_pairs']['full_design']
        self.assertEqual((a['nuisance_rank'], a['full_rank'],
                          a['residual_row_degrees_of_freedom']), (11, 12, 4))
        self.assertEqual((b['nuisance_rank'], b['full_rank'],
                          b['residual_row_degrees_of_freedom']), (10, 11, 5))

    def test_leave_one_batch_nominal_robustness_in_both_variants(self):
        report = audit_bundle(fixture())['variants']
        for name in VARIANTS:
            variants = report[name]
            self.assertEqual(variants['batch_loss_scenarios'], 8)
            self.assertEqual(variants['batch_loss_nominal_pass_count'], 8)
            self.assertEqual(len(variants['leave_one_batch']), 8)
            for row in variants['leave_one_batch'].values():
                self.assertEqual(row['coupon_rows'], 14)
                self.assertEqual(row['named_batch_count'], 7)
                self.assertEqual(row['fully_paired_batch_count'], 7)
                self.assertTrue(row['linear_treatment_estimable'])
                self.assertGreater(row['residual_row_degrees_of_freedom'], 0)

    def test_leave_one_session_detects_cross_session_fragility(self):
        result = audit_bundle(fixture())['variants']
        cross = result['cross_session_pairs']
        self.assertEqual(cross['session_loss_nominal_pass_count'], 0)
        for one in cross['leave_one_session'].values():
            self.assertEqual(one['coupon_rows'], 8)
            self.assertEqual(one['named_batch_count'], 8)
            self.assertEqual(one['session_count'], 1)
            self.assertFalse(one['linear_treatment_estimable'])
            self.assertEqual(one['fully_paired_batch_count'], 0)

    def test_leave_one_session_retains_within_session_pairs_but_halves_batches(self):
        result = audit_bundle(fixture())['variants']['within_session_pairs']
        self.assertEqual(result['session_loss_nominal_pass_count'], 2)
        for one in result['leave_one_session'].values():
            self.assertEqual(one['coupon_rows'], 8)
            self.assertEqual(one['named_batch_count'], 4)
            self.assertEqual(one['session_count'], 1)
            self.assertEqual(one['fully_paired_batch_count'], 4)
            self.assertTrue(one['linear_treatment_estimable'])
            self.assertGreater(one['residual_row_degrees_of_freedom'], 0)
            self.assertFalse(one['physical_adequacy_inferred'])
            self.assertFalse(one['cluster_uncertainty_calibrated'])

    def test_technical_repeats_do_not_fabricate_specimens_or_group_information(self):
        original = audit_bundle(fixture())['variants']
        changed = fixture()
        for plan in changed['variants'].values():
            for coupon in plan['specimens']:
                coupon['planned_moke_traces'] = 30
        newer = audit_bundle(changed)['variants']
        for name in VARIANTS:
            self.assertEqual(newer[name]['full_design']['technical_trace_count'], 480)
            for key in ('nuisance_rank', 'full_rank',
                        'residual_row_degrees_of_freedom',
                        'named_batch_count', 'coupon_rows'):
                self.assertEqual(newer[name]['full_design'][key],
                                 original[name]['full_design'][key])
            self.assertEqual(newer[name]['batch_loss_nominal_pass_count'],
                             original[name]['batch_loss_nominal_pass_count'])
            self.assertEqual(newer[name]['session_loss_nominal_pass_count'],
                             original[name]['session_loss_nominal_pass_count'])

    def test_inherited_v128_first_fixture_still_saturated(self):
        old = audit_plan_bytes(ORIGINAL.read_bytes())
        self.assertEqual(old['specimen_rows'], 8)
        self.assertEqual(old['synthesis_batch_count'], 4)
        self.assertEqual(old['residual_degrees_of_freedom'], 0)
        self.assertTrue(old['linear_contrast_estimable_under_declared_nuisance'])
        self.assertIn('NO_RESIDUAL_DEGREES_OF_FREEDOM',
                      old['blocking_conditions'])
        self.assertFalse(old['physical_recommendation_allowed'])

    def test_rejects_unexpected_observations_and_unregistered_metadata(self):
        for key, value in [('observed_coercivity_A_per_m', 30.0),
                           ('physical_effect_estimate', 200.0),
                           ('independent_validation', True)]:
            sample = fixture()
            sample[key] = value
            with self.subTest(key=key):
                with self.assertRaisesRegex(AttritionContractError, 'INVALID_BUNDLE'):
                    audit_bundle(sample)

    def test_rejects_claimed_external_feasibility_or_approval(self):
        for key in ('treatment_unit_feasibility_approved',
                    'independent_synthesis_batches_verified',
                    'physical_measurements_available', 'laboratory_action_allowed'):
            sample = fixture()
            sample[key] = True
            with self.subTest(key=key):
                with self.assertRaisesRegex(AttritionContractError,
                                            'UNSUPPORTED_EXTERNAL_APPROVAL'):
                    audit_bundle(sample)

    def test_rejects_modified_parent_source_identity(self):
        data = fixture()
        data['parent_v128_design_blob'] = '0' * 40
        with self.assertRaisesRegex(AttritionContractError, 'SOURCE_IDENTITY_CHANGED'):
            audit_bundle(data)
        data = fixture()
        data['status'] = 'approved'
        with self.assertRaisesRegex(AttritionContractError, 'SOURCE_IDENTITY_CHANGED'):
            audit_bundle(data)

    def test_rejects_missing_variant(self):
        data = fixture()
        del data['variants']['within_session_pairs']
        with self.assertRaisesRegex(AttritionContractError, 'REQUIRED_VARIANTS'):
            audit_bundle(data)

    def test_rejects_unpaired_batch_with_unbalanced_arm_labels(self):
        data = fixture()
        first = data['variants']['cross_session_pairs']['specimens'][0]
        first['processing_arm'] = 'modified'
        first['coupon_id'] = 'B01-M'
        with self.assertRaises(AttritionContractError):
            audit_bundle(data)

    def test_rejects_incompatible_within_and_cross_session_premises(self):
        data = fixture()
        data['variants']['within_session_pairs']['specimens'] = copy.deepcopy(
            data['variants']['cross_session_pairs']['specimens'])
        with self.assertRaisesRegex(AttritionContractError,
                                    'EXPECTED_WITHIN_SESSION'):
            audit_bundle(data)
        data = fixture()
        data['variants']['cross_session_pairs']['specimens'] = copy.deepcopy(
            data['variants']['within_session_pairs']['specimens'])
        with self.assertRaisesRegex(AttritionContractError,
                                    'EXPECTED_CROSS_SESSION'):
            audit_bundle(data)

    def test_missing_coupon_or_extra_batch_is_not_a_credible_full_design(self):
        data = fixture()
        data['variants']['cross_session_pairs']['specimens'].pop()
        with self.assertRaises(AttritionContractError):
            audit_bundle(data)
        data = fixture()
        data['variants']['cross_session_pairs']['specimens'][0]['synthesis_batch_id'] = 'NEW'
        with self.assertRaises(AttritionContractError):
            audit_bundle(data)

    def test_duplicate_coupon_or_session_slot_rejected(self):
        data = fixture()
        rows = data['variants']['cross_session_pairs']['specimens']
        rows[1]['coupon_id'] = rows[0]['coupon_id']
        with self.assertRaises(AttritionContractError):
            audit_bundle(data)
        data = fixture()
        rows = data['variants']['cross_session_pairs']['specimens']
        rows[2]['planned_position'] = rows[0]['planned_position']
        with self.assertRaises(AttritionContractError):
            audit_bundle(data)

    def test_wrong_measurement_terminology_and_release_flag_rejected(self):
        for key, val in [('response_unit','mT'),('raw_outcomes_present',True),
                         ('processing_conditions_physically_approved',True),
                         ('reviewed_minimum_effect_A_per_m',200.0)]:
            data=fixture()
            data['variants']['cross_session_pairs'][key]=val
            with self.subTest(key=key):
                with self.assertRaises(AttritionContractError):
                    audit_bundle(data)

    def test_missing_structural_readout_or_magnetic_trace_rejected(self):
        for key in ('xrd_planned','moke_raw_trace_retention'):
            data=fixture()
            data['variants']['within_session_pairs']['specimens'][0][key]=False
            with self.subTest(key=key):
                with self.assertRaises(AttritionContractError):
                    audit_bundle(data)

    def test_unbalanced_positions_are_rejected_even_with_model_rank(self):
        data=fixture()
        rows=data['variants']['cross_session_pairs']['specimens']
        # Swap occupied positions between different arms in S1: valid slots,
        # but the session's treatment means no longer match.
        i=next(i for i,r in enumerate(rows) if r['moke_session_id']=='S1'
               and r['processing_arm']=='reference' and r['planned_position']==1)
        j=next(j for j,r in enumerate(rows) if r['moke_session_id']=='S1'
               and r['processing_arm']=='modified' and r['planned_position']==2)
        rows[i]['planned_position'],rows[j]['planned_position']=2,1
        with self.assertRaisesRegex(AttritionContractError, 'SESSION_ARM_OR_POSITION'):
            audit_bundle(data)

    def test_missing_or_nonpositive_technical_repeats_rejected(self):
        for value in (0,-1,1.5,True):
            data=fixture()
            data['variants']['within_session_pairs']['specimens'][0]['planned_moke_traces']=value
            with self.subTest(value=value):
                with self.assertRaises(AttritionContractError):
                    audit_bundle(data)

    def test_invalid_and_duplicate_json_rejected_without_any_source_access(self):
        for raw in (b'{}', b'{"x":NaN}', b'{"x":1,"x":2}', b'', b'['):
            with self.subTest(raw=raw):
                with self.assertRaises(AttritionContractError):
                    audit_bundle_bytes(raw)
        with self.assertRaises(AttritionContractError):
            parse_bundle(b'[' + b'1' * 300000 + b']')

    def test_report_remains_deterministic_under_record_order_permutation(self):
        baseline=audit_bundle(fixture())
        changed=fixture()
        for plan in changed['variants'].values():
            plan['specimens'].reverse()
        other=audit_bundle(changed)
        self.assertEqual(baseline['variants'], other['variants'])
        self.assertFalse(other['laboratory_action_allowed'])

    def test_cli_default_no_execution_and_explicit_development_only(self):
        self.assertEqual(main([]),0)
        with TemporaryDirectory() as tmp:
            output=Path(tmp)/'report.json'
            self.assertEqual(main(['--designs',str(DESIGNS),'--out',str(output)]),0)
            result=json.loads(output.read_text())
            self.assertFalse(result['physical_measurements_performed'])
            self.assertFalse(result['hypothesis_evaluation_performed'])
            self.assertEqual(result['variants']['cross_session_pairs']['session_loss_nominal_pass_count'],0)
            self.assertEqual(result['variants']['within_session_pairs']['session_loss_nominal_pass_count'],2)


if __name__=='__main__':
    unittest.main()
