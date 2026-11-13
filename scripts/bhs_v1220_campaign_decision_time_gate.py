"""V12.20: source-only stage provenance and counterfactual no-go contract.

All examples are manufactured. Never open historical campaign response rows.
No empirical scoring, mechanism labels, action policy, or material discovery.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
from pathlib import Path

STAGES = ("CANDIDATE_DESIGN", "PRINTED_AND_WEIGHED",
          "INSTRON_TESTED", "QUALITY_REVIEWED", "AFTER_CAMPAIGN_PUBLICATION")
DESIGN_FIELDS = (
    "c4_base", "c8_base", "c4_top", "c8_top",
    "twist_linear", "twist_amplitude", "twist_cycles",
    "perimeter_ratio", "height", "mass", "thickness",
)
CANONICAL_SOURCE_REFERENCES = {
    "article_doi": "10.1038/s41467-024-48534-4",
    "archive_handle": "2144/46687",
    "archive_metadata_file_label": "CampaignData.csv",
    "archive_filament_file_label": "FilamentData.csv",
    "source_code_repository_id": 676572978,
    "source_code_pinned_commit": "621d294e2df6b7c7156f0f72dab4ec39c168fd0f",
    "shape_code_pinned_commit": "a5b784f0fe2d93d72bd67f7390df0ca44b1279c2",
    "source_code_repo_readme_blob": "3914437b87d1d93fabf3b9f9245596965722a067",
    "source_code_select_experiment_blob": "4ca861776a81321ddbcd4b80775b46f831d252c8",
    "source_code_save_design_blob": "3b6fa2b3e40a2ed582b9107a02321027711ecdc8",
    "source_code_process_results_blob": "755f885f1577d36cd4257f924c92601d080f3330",
    "source_code_previous_data_backfill_blob": "49ab113c7eef233062abcd4a9058bb61a851f047",
    "design_library_readme_blob": "cfff28992112224610b4b9ef49c7e876e5e8f054",
    "original_2024_archive_bytes_downloaded": False,
}
PUBLISHED_TOTAL_EXPERIMENTS = 25387
PUBLISHED_VALID_EXPERIMENTS = 13250
# Earliest stage is a conceptual process-time classification, NOT a certificate
# that every historical source CSV row or policy could access the named field.
FIELD_STAGE = {
    **{f: 0 for f in DESIGN_FIELDS},
    "material_id_loaded_before_choice": 0,
    "printer_id_eligible_before_choice": 0,
    "material_modulus_from_prior_calibration": 0,
    "historical_policy_id_metadata": 0,
    "actual_printed_mass_g": 1,
    "force_displacement_trace": 2,
    "toughness_j": 2,
    "efficiency_ks": 2,
    "max_stress_mpa": 2,
    "measured_height_from_trace_mm": 2,
    "valid": 3,
    "quality_exclusion_reason": 3,
    "campaign_global_rank": 4,
}
REQUIRES_PRIOR_EVENT = frozenset({"material_modulus_from_prior_calibration"})
NOT_PHYSICAL_PREDICTORS = frozenset({"historical_policy_id_metadata"})
POST_COMMIT_MEASUREMENTS = frozenset(f for f, t in FIELD_STAGE.items() if t > 0)
NEVER_BEFORE_SELECTION = POST_COMMIT_MEASUREMENTS | NOT_PHYSICAL_PREDICTORS
CLOSED = {
    "development_only": True,
    "source_metadata_bytes_verified": False,
    "source_csv_header_verified": False,
    "historic_policy_snapshot_verified": False,
    "original_raw_curve_identity_verified": False,
    "logging_propensities_verified": False,
    "counterfactual_responses_available": False,
    "scored_validation_allowed": False,
    "full_bhs_fair_comparison_ready": False,
    "physical_mechanism_hypotheses_validated": False,
    "independent_holdout_used": False,
    "commercial_rights_verified": False,
    "claim_of_superiority": False,
    "physical_action_allowed": False,
}


class StageContractError(ValueError):
    pass


def _timestamp(x: str, name: str) -> datetime:
    if type(x) is not str or len(x) > 64:
        raise StageContractError("MISSING_" + name)
    try:
        dt = datetime.fromisoformat(x.replace("Z", "+00:00"))
    except ValueError as exc:
        raise StageContractError("INVALID_" + name) from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise StageContractError("NAIVE_" + name)
    return dt


def check_design(design: dict) -> None:
    """Only verify public input shape; physical feasibility needs lab source."""
    if type(design) is not dict or set(design) != set(DESIGN_FIELDS):
        raise StageContractError("PUBLIC_DESIGN_FIELDS_NOT_EXACT")
    for field, value in design.items():
        if type(value) not in (int, float) or not math.isfinite(float(value)):
            raise StageContractError("NONFINITE_OR_INVALID_PUBLIC_DESIGN")
    for field in ("perimeter_ratio", "height", "mass", "thickness"):
        if design[field] <= 0:
            raise StageContractError("NONPOSITIVE_PUBLIC_DESIGN_DIMENSION")
    if design["twist_cycles"] < 0:
        raise StageContractError("NEGATIVE_TWIST_CYCLES")


def check_stage_view(
    values: dict, *, stage: str, finished_test: bool = False,
    quality_reviewed: bool = False, verified_prior_calibration: bool = False,
) -> list[str]:
    """Reject a value that would be unavailable at the declared decision stage.

    The optional booleans are caller-provided *synthetic contract metadata*;
    they are not independent authentication and never open scoring gates.
    """
    if stage not in STAGES:
        raise StageContractError("UNKNOWN_EXPERIMENT_STAGE")
    if type(values) is not dict:
        raise StageContractError("INVALID_VIEW_FIELDS")
    idx = STAGES.index(stage)
    for field in values:
        if field not in FIELD_STAGE:
            raise StageContractError("UNKNOWN_OR_UNAPPROVED_FIELD")
        if FIELD_STAGE[field] > idx:
            raise StageContractError("FUTURE_EXPERIMENT_INFORMATION")
        if field in REQUIRES_PRIOR_EVENT and not verified_prior_calibration:
            raise StageContractError("PRIOR_CALIBRATION_NOT_VERIFIED")
        if field in NOT_PHYSICAL_PREDICTORS:
            raise StageContractError("POLICY_METADATA_IS_NOT_MATERIAL_PREDICTOR")
        if FIELD_STAGE[field] >= 2 and not finished_test:
            raise StageContractError("UNREVEALED_TEST_RESULT")
        if FIELD_STAGE[field] >= 3 and not quality_reviewed:
            raise StageContractError("UNREVIEWED_QUALITY_CONTROL")
    return sorted(values)


def validate_revealed_history(observations: list, decision_time: str) -> dict:
    """Strict *already revealed* history, never a source outcome table.

    Caller is an evaluation owner; any future record is a fatal leak.
    A row ID is never substituted for a timestamp.
    """
    at = _timestamp(decision_time, "DECISION_TIME")
    if type(observations) is not list or len(observations) > 50000:
        raise StageContractError("INVALID_REVEALED_HISTORY")
    seen = set()
    for entry in observations:
        if type(entry) is not dict or set(entry) != {
                "experiment_id", "selected_at", "revealed_at",
                "quality_checked_at", "result"}:
            raise StageContractError("INVALID_OBSERVATION_LOG_SCHEMA")
        ident = entry["experiment_id"]
        if type(ident) is not str or not ident.strip() or ident in seen:
            raise StageContractError("MISSING_OR_DUPLICATE_OBSERVATION_ID")
        seen.add(ident)
        selected_at = _timestamp(entry["selected_at"], "SELECTION_TIME")
        revealed_at = _timestamp(entry["revealed_at"], "REVEAL_TIME")
        quality_at = _timestamp(entry["quality_checked_at"], "QUALITY_TIME")
        if not (selected_at <= revealed_at <= quality_at <= at):
            raise StageContractError("LATE_OR_OUT_OF_ORDER_OBSERVATION_LEAK")
        values = entry["result"]
        check_stage_view(values,stage="QUALITY_REVIEWED",
                         finished_test=True,quality_reviewed=True)
        if "valid" not in values or type(values["valid"]) is not bool:
            raise StageContractError("MISSING_BOOLEAN_QC_STATUS")
        if values["valid"] is False and any(k in values for k in
                 ("toughness_j", "efficiency_ks", "force_displacement_trace")):
            # Outcome bytes might exist for a failed specimen but cannot be
            # uncritically treated as a successful target.
            raise StageContractError("UNQUALIFIED_FAILED_RESPONSE_AS_TARGET")
    return {
        "revealed_count": len(seen),
        "all_past_measurements_before_decision_time": True,
        "source_timeline_authenticity_verified": False,
        "policy_score_allowed": False,
    }


def scientific_admission_report() -> dict:
    """Only a machine-readable distinction between source and actual proof."""
    return {
        "schema": "BHS-V12.20-CAMPAIGN-DECISION-TIME-GATE",
        "published_source_records_total": PUBLISHED_TOTAL_EXPERIMENTS,
        "published_source_records_valid": PUBLISHED_VALID_EXPERIMENTS,
        "published_source_invalid_or_other": (
            PUBLISHED_TOTAL_EXPERIMENTS - PUBLISHED_VALID_EXPERIMENTS),
        "counts_from_published_article_not_recomputed_csv": True,
        "original_2020_crossed_barrel_source_separate": True,
        "external_author_code_snapshot_inspected": True,
        "source_references": CANONICAL_SOURCE_REFERENCES,
        "proposed_gcs_design_recipe_keys": list(DESIGN_FIELDS),
        "original_campaign_csv_column_mapping_verified": False,
        "field_earliest_conceptual_stage": dict(sorted(
            (name, STAGES[stage]) for name, stage in FIELD_STAGE.items())),
        "calibration_information_not_automatically_approved": sorted(REQUIRES_PRIOR_EVENT),
        "postdecision_information_never_prequery": sorted(NEVER_BEFORE_SELECTION),
        "quality_status_is_an_observed_postselection_outcome": True,
        "published_campaign_policy_and_feasible_space_changed": True,
        "experiment_integer_id_not_certified_as_decision_timestamp": True,
        "published_source_test_outcomes_read": False,
        "new_policy_acquisition_score_computed": False,
        "counterfactual_unselected_actions_are_not_measured": True,
        "possible_future_prediction_test_not_equivalent_to_policy_acquisition_test": True,
        "data_license": "CC-BY-NC-SA-4.0",
        "source_code_license_is_not_dataset_license": True,
        "decision": "NO_GO_ADTS_2024_POLICY_TIME_AND_COUNTERFACTUALS_UNVERIFIED",
        **CLOSED,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    r = scientific_admission_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print("Design-stage keys documented:", len(DESIGN_FIELDS))
    print("Archived CSV field mapping:", "NOT VERIFIED")
    print("Counterfactual acquisition:", "NOT IDENTIFIABLE FROM LOGGED OUTCOMES")
    print("Scored physical BHS comparison:", "BLOCKED")


if __name__ == "__main__":
    main()
