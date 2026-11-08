"""Adversarial processing-scope, experimental-unit and provenance contracts."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.bhs_v1210_assignment_unit import (
    AssignmentContractError, FIXTURE, audit_all, audit_bytes, main,
    parse_fixtures, _matrix_rank,
)


def fixture():
    return json.loads(FIXTURE.read_text(encoding='utf-8'))


def records(mode):
    return fixture()['scenarios'][mode]['specimens']


class AssignmentUnitTests(unittest.TestCase):
    def test_source_is_outcome_free_and_physical_release_is_closed(self):
        raw=FIXTURE.read_bytes()
        report=audit_bytes(raw)
        self.assertEqual(report['source_sha256'],hashlib.sha256(raw).hexdigest())
        self.assertFalse(report['physical_measurements_performed'])
        self.assertFalse(report['independent_physical_validation_established'])
        self.assertFalse(report['physical_recommendation_allowed'])
        self.assertFalse(report['laboratory_action_allowed'])
        self.assertFalse(report['formal_sample_size_established'])
        self.assertEqual(report['status'],'NO_GO_EXTERNAL_PROCESSING_SCOPE_AND_LAB_REVIEW_REQUIRED')

    def test_full_plans_keep_distinct_processing_units_and_experiment_counts(self):
        result=audit_all(fixture())['scenarios']
        self.assertEqual(set(result),{'postdeposition_coupon','deposition_run'})
        for mode,design in result.items():
            with self.subTest(mode=mode):
                x=design['full_design']
                self.assertEqual(x['coupon_rows'],16)
                self.assertEqual(x['named_matched_blocks'],8)
                self.assertEqual(x['complete_paired_blocks'],8)
                self.assertEqual(x['technical_traces'],48)
                self.assertEqual(x['moke_sessions'],2)
                self.assertEqual(x['named_processing_events'],16)
                self.assertTrue(x['treatment_estimable_in_declared_additive_matrix'])
                self.assertTrue(x['nominal_rank_and_df_pass'])
                self.assertFalse(x['physical_independence_established'])
                self.assertFalse(design['actual_treatment_assignability_verified'] if 'actual_treatment_assignability_verified' in design else design['actual_processing_scope_verified'])
        self.assertEqual(result['postdeposition_coupon']['full_design']['named_deposition_runs'],8)
        self.assertEqual(result['deposition_run']['full_design']['named_deposition_runs'],16)

    def test_treatment_scope_must_match_declared_assignment_unit(self):
        for mode in ('postdeposition_coupon','deposition_run'):
            x=fixture()
            x['scenarios'][mode]['declared_assignment_unit']='deposition_run' if mode=='postdeposition_coupon' else 'coupon'
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(AssignmentContractError,'SCOPE_UNIT_MISMATCH'):
                    audit_all(x)

    def test_deposition_setting_must_not_mix_arms_in_same_synthesis_run(self):
        x=fixture()
        rows=x['scenarios']['deposition_run']['specimens']
        rows[1]['source_deposition_run_id']=rows[0]['source_deposition_run_id']
        with self.assertRaisesRegex(AssignmentContractError,'WHOLE_DEPOSITION_RUN'):
            audit_all(x)

    def test_deposition_route_cannot_relabel_processing_event_as_new_run(self):
        x=fixture()
        rows=x['scenarios']['deposition_run']['specimens']
        rows[0]['processing_event_id']='independently-labelled-event'
        with self.assertRaisesRegex(AssignmentContractError,'DEPOSITION_PROCESSING_RUN_ID'):
            audit_all(x)

    def test_postdeposition_coupon_requires_shared_source_run(self):
        x=fixture()
        rows=x['scenarios']['postdeposition_coupon']['specimens']
        rows[0]['source_deposition_run_id']='new-deposition-run'
        with self.assertRaises(AssignmentContractError):
            audit_all(x)

    def test_shared_postprocessing_event_is_not_two_independent_units(self):
        x=fixture()
        rows=x['scenarios']['postdeposition_coupon']['specimens']
        rows[1]['processing_event_id']=rows[0]['processing_event_id']
        with self.assertRaisesRegex(AssignmentContractError,'SHARED_PROCESSING_EVENT'):
            audit_all(x)

    def test_coupon_pair_must_contain_opposite_arms(self):
        x=fixture()
        x['scenarios']['postdeposition_coupon']['specimens'][1]['processing_arm']='reference'
        with self.assertRaisesRegex(AssignmentContractError,'INCOMPLETE_REFERENCE_MODIFIED_BLOCK'):
            audit_all(x)

    def test_session_confounded_with_processing_arm_fails(self):
        x=fixture()
        rows=x['scenarios']['postdeposition_coupon']['specimens']
        # Re-label session affiliations, retaining unique session positions.
        for row in rows:
            row['moke_session_id']='S1' if row['processing_arm']=='reference' else 'S2'
        for session in ('S1','S2'):
            subset=[r for r in rows if r['moke_session_id']==session]
            for pos,row in enumerate(subset,1):row['planned_position']=pos
        with self.assertRaisesRegex(AssignmentContractError,'SESSION_TREATMENT_CONFUNDING'):
            audit_all(x)

    def test_substrate_position_stratum_must_not_determine_treatment(self):
        x=fixture()
        for mode in x['scenarios']:
            for row in x['scenarios'][mode]['specimens']:
                row['substrate_location_stratum']='near' if row['processing_arm']=='reference' else 'far'
        with self.assertRaisesRegex(AssignmentContractError,'SPATIAL_COMPOSITION_POSITION_TREATMENT_CONFOUNDING'):
            audit_all(x)

    def test_duplicate_coupon_and_session_slot_rejected(self):
        for field in ('coupon_id','planned_position'):
            x=fixture()
            rows=x['scenarios']['deposition_run']['specimens']
            rows[1][field]=rows[0][field]
            with self.subTest(field=field):
                with self.assertRaises(AssignmentContractError):
                    audit_all(x)

    def test_unapproved_result_fields_and_flag_tampering_rejected(self):
        for field in ('treatment_unit_physical_feasibility_verified',
                      'instrument_calibration_verified','new_physical_measurements_present',
                      'physical_action_allowed'):
            x=fixture()
            x['scenarios']['deposition_run'][field]=True
            with self.subTest(field=field):
                with self.assertRaisesRegex(AssignmentContractError,'UNSUPPORTED_APPROVAL'):
                    audit_all(x)
        x=fixture()
        x['scenarios']['postdeposition_coupon']['specimens'][0]['measured_coercivity']=250.0
        with self.assertRaisesRegex(AssignmentContractError,'PLAN_ROW_FIELDS'):
            audit_all(x)

    def test_duplicate_json_keys_and_invalid_nonfinite_data_rejected(self):
        for raw in (b'{}',b'{"a":1,"a":2}',b'{"x":NaN}',b'not json',b'',b'{'*300_000):
            with self.subTest(raw=raw[:20]):
                with self.assertRaises(AssignmentContractError):
                    audit_bytes(raw)

    def test_changed_fixture_schema_and_parent_rejected(self):
        for key,value in (('schema_version','BHS-V99'),
                          ('source_v129_fixture_blob','0'*40),
                          ('target_unit','mT'),('status','approved')):
            x=fixture()
            x[key]=value
            with self.subTest(key=key):
                with self.assertRaisesRegex(AssignmentContractError,'UNAUTHORIZED_SCIENTIFIC'):
                    audit_all(x)

    def test_full_event_and_measurement_session_loss_are_enumerated(self):
        result=audit_all(fixture())['scenarios']
        for mode,summary in result.items():
            with self.subTest(mode=mode):
                self.assertEqual(summary['event_count'],16)
                self.assertEqual(len(summary['all_event_losses']),16)
                self.assertEqual(summary['event_loss_nominal_pass_count'],16)
                self.assertEqual(summary['session_count'],2)
                self.assertEqual(len(summary['all_session_losses']),2)
                self.assertEqual(summary['session_loss_nominal_pass_count'],2)
                self.assertTrue(all(v['coupon_rows']==15 for v in summary['all_event_losses'].values()))
                self.assertTrue(all(v['complete_paired_blocks']==7 for v in summary['all_event_losses'].values()))
                self.assertTrue(all(v['coupon_rows']==8 for v in summary['all_session_losses'].values()))
                self.assertTrue(all(v['complete_paired_blocks']==4 for v in summary['all_session_losses'].values()))

    def test_technical_trace_multipliers_do_not_increase_independent_units(self):
        rows=records('postdeposition_coupon')
        a=_matrix_rank(rows)
        b=copy.deepcopy(rows)
        for row in b:row['planned_moke_traces']*=12
        c=_matrix_rank(b)
        self.assertEqual(c['technical_traces'],a['technical_traces']*12)
        for key in ('coupon_rows','named_matched_blocks','named_processing_events',
                    'full_rank','nuisance_rank','residual_coupon_row_df',
                    'treatment_estimable_in_declared_additive_matrix'):
            self.assertEqual(a[key],c[key])

    def test_both_routes_refuse_to_certify_physical_assignability(self):
        report=audit_all(fixture())
        for x in report['scenarios'].values():
            self.assertFalse(x['actual_processing_scope_verified'])
            self.assertFalse(x['actual_independent_replicates_verified'])
            self.assertFalse(x['causal_identification_established'])
            self.assertFalse(x['physical_recommendation_allowed'])
            self.assertFalse(x['laboratory_action_allowed'])

    def test_measurement_plan_requires_original_traces_and_diffraction(self):
        for field in ('xrd_planned','moke_raw_trace_retention'):
            x=fixture()
            x['scenarios']['deposition_run']['specimens'][0][field]=False
            with self.subTest(field=field):
                with self.assertRaisesRegex(AssignmentContractError,'MISSING_ORIGINAL'):
                    audit_all(x)

    def test_cli_no_scoring_without_explicit_paths(self):
        self.assertEqual(main([]),0)
        with TemporaryDirectory() as d:
            out=Path(d)/'audit.json'
            self.assertEqual(main(['--fixtures',str(FIXTURE),'--out',str(out)]),0)
            report=json.loads(out.read_text())
            self.assertFalse(report['physical_measurements_performed'])
            self.assertFalse(report['physical_recommendation_allowed'])


if __name__=='__main__':
    unittest.main()
