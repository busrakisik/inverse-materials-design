"""V12.20 source-stage timing and missing-counterfactual contract tests.

Only invented metadata and outcomes. No original campaign response labels loaded.
"""
from pathlib import Path
import ast
import json
import unittest

from scripts import bhs_v1220_campaign_decision_time_gate as m


def fake_design():
    return {
        "c4_base": 0.3, "c8_base": 0.1, "c4_top": 0.2, "c8_top": 0.0,
        "twist_linear": 1.0, "twist_amplitude": 0.05, "twist_cycles": 3.0,
        "perimeter_ratio": 1.2, "height": 20.0, "mass": 2.1, "thickness": 0.4,
    }


def fake_finished_event(*, valid=True):
    return {
        "experiment_id": "synthetic-test-101",
        "selected_at": "2023-01-01T10:00:00+00:00",
        "revealed_at": "2023-01-01T11:00:00+00:00",
        "quality_checked_at": "2023-01-01T11:05:00+00:00",
        "result": {"valid": valid} if not valid else
                  {"valid": True, "toughness_j": 10.5, "efficiency_ks": 0.25},
    }


class CampaignTimeGateTests(unittest.TestCase):
    def test_only_design_recipe_exists_before_choosing_action(self):
        p=fake_design()
        m.check_design(p)
        self.assertEqual(m.check_stage_view(
            p, stage="CANDIDATE_DESIGN"), sorted(p))
        self.assertFalse(m.scientific_admission_report()["scored_validation_allowed"])

    def test_exact_11_design_keys_no_outcome_or_hindsight(self):
        design=fake_design()
        self.assertEqual(len(design),11)
        design["valid"]=True
        with self.assertRaisesRegex(m.StageContractError,"PUBLIC_DESIGN_FIELDS_NOT_EXACT"):
            m.check_design(design)

    def test_design_recipe_dims_must_be_finite(self):
        for k,v in [("height",0),("thickness",-1),("mass",float("nan")),
                    ("twist_cycles",-0.1),("perimeter_ratio",0),
                    ("c4_base",float("inf")),("twist_linear",True)]:
            with self.subTest(field=k):
                d=fake_design();d[k]=v
                with self.assertRaises(m.StageContractError):
                    m.check_design(d)

    def test_earliest_conceptual_stage_is_not_source_authentication(self):
        s=m.scientific_admission_report()
        self.assertEqual(s["published_source_records_total"],25387)
        self.assertEqual(s["published_source_records_valid"],13250)
        self.assertEqual(s["published_source_invalid_or_other"],12137)
        self.assertTrue(s["counts_from_published_article_not_recomputed_csv"])
        self.assertFalse(s["original_campaign_csv_column_mapping_verified"])
        self.assertFalse(s["source_metadata_bytes_verified"])
        self.assertFalse(s["source_csv_header_verified"])

    def test_measured_mass_not_available_at_design_time(self):
        with self.assertRaisesRegex(m.StageContractError,"FUTURE_EXPERIMENT_INFORMATION"):
            m.check_stage_view({"actual_printed_mass_g":2.1},
                               stage="CANDIDATE_DESIGN")
        self.assertEqual(m.check_stage_view({"actual_printed_mass_g":2.1},
                                            stage="PRINTED_AND_WEIGHED"),
                         ["actual_printed_mass_g"])

    def test_measured_height_from_trace_cannot_be_used_pretest(self):
        with self.assertRaisesRegex(m.StageContractError,"FUTURE_EXPERIMENT_INFORMATION"):
            m.check_stage_view({"measured_height_from_trace_mm":19.8},
                               stage="PRINTED_AND_WEIGHED")

    def test_valid_is_posttest_qc_not_candidate_attribute(self):
        for st in m.STAGES[:3]:
            with self.subTest(stage=st):
                with self.assertRaisesRegex(m.StageContractError,
                                            "FUTURE_EXPERIMENT_INFORMATION"):
                    m.check_stage_view({"valid":True},stage=st)

    def test_test_results_require_finished_and_revealed(self):
        for field in ("toughness_j","efficiency_ks","force_displacement_trace",
                      "max_stress_mpa","measured_height_from_trace_mm"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(m.StageContractError,"UNREVEALED_TEST_RESULT"):
                    m.check_stage_view({field:1.0},stage="INSTRON_TESTED",
                                       finished_test=False)
                self.assertEqual(m.check_stage_view(
                    {field:1.0},stage="INSTRON_TESTED",finished_test=True),
                    [field])

    def test_quality_reason_requires_review_after_testing(self):
        with self.assertRaisesRegex(m.StageContractError,"UNREVIEWED_QUALITY_CONTROL"):
            m.check_stage_view({"quality_exclusion_reason":"fixture-failed"},
                               stage="QUALITY_REVIEWED",finished_test=True)
        self.assertEqual(m.check_stage_view(
            {"quality_exclusion_reason":"fixture-failed"},
            stage="QUALITY_REVIEWED",finished_test=True,quality_reviewed=True),
            ["quality_exclusion_reason"])

    def test_prior_calibration_not_free_global_metadata(self):
        with self.assertRaisesRegex(m.StageContractError,"PRIOR_CALIBRATION_NOT_VERIFIED"):
            m.check_stage_view({"material_modulus_from_prior_calibration":100.0},
                               stage="CANDIDATE_DESIGN")
        m.check_stage_view({"material_modulus_from_prior_calibration":100.0},
                           stage="CANDIDATE_DESIGN",
                           verified_prior_calibration=True)
        self.assertFalse(m.scientific_admission_report()["historic_policy_snapshot_verified"])

    def test_policy_identifiers_are_not_physical_predictors(self):
        with self.assertRaisesRegex(m.StageContractError,
                                    "POLICY_METADATA_IS_NOT_MATERIAL_PREDICTOR"):
            m.check_stage_view({"historical_policy_id_metadata":1},
                               stage="CANDIDATE_DESIGN")

    def test_future_global_campaign_rank_never_used_at_choice(self):
        with self.assertRaisesRegex(m.StageContractError,"FUTURE_EXPERIMENT_INFORMATION"):
            m.check_stage_view({"campaign_global_rank":1},
                               stage="CANDIDATE_DESIGN")

    def test_unknown_fields_not_silently_filtered(self):
        with self.assertRaisesRegex(m.StageContractError,"UNKNOWN_OR_UNAPPROVED_FIELD"):
            m.check_stage_view({"future_best_fitness":100},
                               stage="CANDIDATE_DESIGN")

    def test_real_source_cannot_be_score_approved_through_api(self):
        state=m.scientific_admission_report()
        for field in ("source_metadata_bytes_verified", "historic_policy_snapshot_verified",
                      "counterfactual_responses_available", "logging_propensities_verified",
                      "scored_validation_allowed", "full_bhs_fair_comparison_ready",
                      "commercial_rights_verified", "claim_of_superiority"):
            self.assertIs(state[field],False)
        self.assertEqual(state["decision"],
              "NO_GO_ADTS_2024_POLICY_TIME_AND_COUNTERFACTUALS_UNVERIFIED")

    def test_author_code_snapshot_not_live_signed_event_log(self):
        r=m.scientific_admission_report()
        self.assertTrue(r["external_author_code_snapshot_inspected"])
        self.assertTrue(r["experiment_integer_id_not_certified_as_decision_timestamp"])
        self.assertFalse(r["historic_policy_snapshot_verified"])
        self.assertEqual(r["source_references"]["source_code_repository_id"],676572978)

    def test_source_dataset_license_separate_from_permissive_code(self):
        r=m.scientific_admission_report()
        self.assertEqual(r["data_license"],"CC-BY-NC-SA-4.0")
        self.assertTrue(r["source_code_license_is_not_dataset_license"])
        self.assertFalse(r["commercial_rights_verified"])

    def test_revealed_prior_observation_is_valid_synthetic_contract(self):
        r=m.validate_revealed_history(
            [fake_finished_event()], "2023-01-01T11:10:00+00:00")
        self.assertEqual(r["revealed_count"],1)
        self.assertFalse(r["policy_score_allowed"])
        self.assertFalse(r["source_timeline_authenticity_verified"])

    def test_evaluation_cannot_reveal_future_test_before_decision(self):
        with self.assertRaisesRegex(m.StageContractError,
                                    "LATE_OR_OUT_OF_ORDER_OBSERVATION_LEAK"):
            m.validate_revealed_history(
                [fake_finished_event()],"2023-01-01T10:30:00+00:00")

    def test_qc_time_reordered_is_rejected(self):
        e=fake_finished_event()
        e["quality_checked_at"]="2023-01-01T10:10:00+00:00"
        with self.assertRaisesRegex(m.StageContractError,
                                    "LATE_OR_OUT_OF_ORDER_OBSERVATION_LEAK"):
            m.validate_revealed_history([e],"2023-01-01T12:00:00+00:00")

    def test_non_timezone_timestamp_cannot_establish_history(self):
        e=fake_finished_event()
        e["revealed_at"]="2023-01-01T11:00:00"
        with self.assertRaisesRegex(m.StageContractError,"NAIVE_REVEAL_TIME"):
            m.validate_revealed_history([e],"2023-01-01T12:00:00+00:00")

    def test_failed_not_measured_action_status_is_kept(self):
        e=fake_finished_event(valid=False)
        r=m.validate_revealed_history([e],"2023-01-01T12:00:00+00:00")
        self.assertEqual(r["revealed_count"],1)

    def test_failed_action_with_target_not_coded_as_success(self):
        e=fake_finished_event(valid=False)
        e["result"]["toughness_j"]=100.0
        with self.assertRaisesRegex(m.StageContractError,
                                    "UNQUALIFIED_FAILED_RESPONSE_AS_TARGET"):
            m.validate_revealed_history([e],"2023-01-01T12:00:00+00:00")

    def test_duplicate_action_id_not_counted_twice(self):
        e=fake_finished_event()
        with self.assertRaisesRegex(m.StageContractError,
                                    "MISSING_OR_DUPLICATE_OBSERVATION_ID"):
            m.validate_revealed_history([e,dict(e)],
                                          "2023-01-01T12:00:00+00:00")

    def test_qc_requires_boolean_valid(self):
        e=fake_finished_event()
        e["result"]["valid"]="TRUE"
        with self.assertRaisesRegex(m.StageContractError,"MISSING_BOOLEAN_QC_STATUS"):
            m.validate_revealed_history([e],"2023-01-01T12:00:00+00:00")

    def test_unknown_observation_metadata_not_accepted(self):
        e=fake_finished_event()
        e["global_best_after_campaign"]=1.0
        with self.assertRaisesRegex(m.StageContractError,
                                    "INVALID_OBSERVATION_LOG_SCHEMA"):
            m.validate_revealed_history([e],"2023-01-01T12:00:00+00:00")

    def test_source_module_never_downloads_or_reads_real_data(self):
        s=Path(m.__file__).read_text()
        ast.parse(s)
        self.assertNotIn("read_csv(",s)
        self.assertNotIn("requests.get(",s)
        self.assertNotIn("urlopen(",s)
        self.assertNotIn("np.load(",s)
        self.assertNotIn("torch.load(",s)
        self.assertNotIn("open_bu_file(",s)

    def test_observation_source_not_available_to_unselected_candidates(self):
        d=fake_design()
        m.check_design(d)
        with self.assertRaisesRegex(m.StageContractError,
                                    "FUTURE_EXPERIMENT_INFORMATION"):
            m.check_stage_view(dict(d,toughness_j=10),
                               stage="CANDIDATE_DESIGN")

    def test_catalog_determinism_no_outcomes(self):
        x=json.dumps(m.scientific_admission_report(),sort_keys=True)
        y=json.dumps(m.scientific_admission_report(),sort_keys=True)
        self.assertEqual(x,y)
        self.assertTrue(m.scientific_admission_report()[
            "counterfactual_unselected_actions_are_not_measured"])
        self.assertFalse(m.scientific_admission_report()[
            "new_policy_acquisition_score_computed"])


if __name__=="__main__":
    unittest.main()
