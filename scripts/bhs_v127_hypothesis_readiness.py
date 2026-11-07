"""BHS v12.7: falsifiable physical-hypothesis passport readiness.

This is a structural, fail-closed review of a *proposed* Fe-Co-Ni research pilot.
It performs no synthesis, measurement, acquisition, source download or scoring.
It cannot authenticate claimed human approvals or authorize laboratory action.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "BHS-V12.7"
EXPECTED_SYSTEM = "Fe-Co-Ni magnetic thin films"
PASSPORT_PATH = Path("research/BHS_V127_FECONI_PILOT_PASSPORT.json")
MAX_PASSPORT_BYTES = 128_000
PLACEHOLDERS = frozenset({"unknown", "pending", "tbd", "none", "n/a", "to be determined"})
FIELD_KEYS = {
    "root": frozenset((
        "schema_version", "study_id", "status", "material_system",
        "hypotheses", "readout", "design", "resources", "governance",
        "evidence", "release", "references"
    )),
    "hypothesis": frozenset(("id", "primary_observable", "unit", "prediction", "falsifier")),
    "readout": frozenset((
        "primary_observable", "primary_unit", "method", "structural_method",
        "raw_trace_retention", "instrument_field_calibration_verified",
        "structural_instrument_calibration_verified"
    )),
    "design": frozenset((
        "independence_unit", "calibration_group_ids", "evaluation_group_ids",
        "randomization_plan", "processing_conditions", "composition_verified",
        "substrate_control", "thickness_control", "structural_contrast_definition",
        "minimum_meaningful_effect_A_per_m", "measurement_uncertainty_A_per_m",
        "sample_size_and_precision_plan", "measurement_chronology_plan",
        "missing_data_plan"
    )),
    "resources": frozenset((
        "response_budget", "per_measurement_cost", "cost_unit",
        "abstention_cost", "measurement_seconds"
    )),
    "governance": frozenset((
        "lab_partner_confirmed", "responsible_investigator_review_verified",
        "material_and_instrument_safety_verified", "source_rights_verified",
        "protocol_externally_registered"
    )),
    "evidence": frozenset((
        "new_prospective_measurements_available", "independent_validation_available",
        "authentic_measurement_log_verified", "source_sha256", "source_license",
        "historical_nist_used_as_holdout"
    )),
    "release": frozenset((
        "requested", "physical_action_allowed", "generalization_claim_allowed"
    )),
}


class PilotContractError(ValueError):
    """Invalid research passport; no downstream scientific conclusion is authorized."""


def _check_keys(value, group):
    if type(value) is not dict or set(value) != FIELD_KEYS[group]:
        raise PilotContractError("INVALID_" + group.upper() + "_FIELDS")


def _nonplaceholder(value):
    return (type(value) is str and bool(value.strip())
            and value.strip().lower() not in PLACEHOLDERS)


def _real(value, *, strictly_positive=False):
    return (type(value) in (int, float) and math.isfinite(float(value))
            and (not strictly_positive or value > 0))


def _ids(values, name):
    if type(values) is not list:
        raise PilotContractError("INVALID_" + name.upper() + "_GROUP_LIST")
    if any(not _nonplaceholder(x) for x in values):
        raise PilotContractError("INVALID_" + name.upper() + "_GROUP_ID")
    if len(values) != len(set(values)):
        raise PilotContractError("DUPLICATE_" + name.upper() + "_GROUP_ID")
    return set(values)


def _pair_hook(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise PilotContractError("DUPLICATE_JSON_KEY")
        obj[key] = value
    return obj


def parse_passport(raw: bytes):
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_PASSPORT_BYTES:
        raise PilotContractError("PASSPORT_BYTES_INVALID")
    try:
        obj = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_pair_hook,
            parse_constant=lambda s: (_ for _ in ()).throw(PilotContractError("NONFINITE_JSON"))
        )
    except (UnicodeError, ValueError, TypeError) as exc:
        if isinstance(exc, PilotContractError):
            raise
        raise PilotContractError("PASSPORT_JSON_INVALID") from exc
    return obj


def validate_passport(passport: dict, *, raw_sha256: str | None = None):
    """Validate falsifiability structure; ALWAYS prohibit automated physical action.

    The review of authenticity is out of scope. Even a completely filled
    passport cannot be elevated to verified physical evidence by this code.
    """
    _check_keys(passport, "root")
    if (passport["schema_version"] != SCHEMA or
            passport["material_system"] != EXPECTED_SYSTEM or
            passport["status"] != "candidate_unapproved" or
            not _nonplaceholder(passport["study_id"])):
        raise PilotContractError("UNSUPPORTED_PILOT_IDENTITY")
    hypotheses = passport["hypotheses"]
    if type(hypotheses) is not list or len(hypotheses) != 2:
        raise PilotContractError("REQUIRE_TWO_COMPETING_HYPOTHESES")
    for h in hypotheses:
        _check_keys(h, "hypothesis")
        if (h["primary_observable"] != "coercive_field" or h["unit"] != "A/m"
                or not all(_nonplaceholder(h[k]) and len(h[k].strip()) >= 35
                           for k in ("prediction", "falsifier"))):
            raise PilotContractError("HYPOTHESIS_NOT_MEASURABLE_OR_FALSIFIABLE")
    if ({h["id"] for h in hypotheses} != {"H0", "H1"}
            or len({h["prediction"].strip().casefold() for h in hypotheses}) != 2
            or len({h["falsifier"].strip().casefold() for h in hypotheses}) != 2):
        raise PilotContractError("HYPOTHESIS_DUPLICATE_OR_NOT_DISTINGUISHABLE")

    readout = passport["readout"]
    _check_keys(readout, "readout")
    if (readout["primary_observable"] != "coercive_field" or
            readout["primary_unit"] != "A/m" or
            readout["method"] != "MOKE hysteresis" or
            readout["structural_method"] != "X-ray diffraction" or
            readout["raw_trace_retention"] is not True):
        raise PilotContractError("INVALID_TARGET_OR_PRIMARY_MEASUREMENT")
    missing = []
    for field in ("instrument_field_calibration_verified",
                  "structural_instrument_calibration_verified"):
        if type(readout[field]) is not bool:
            raise PilotContractError("INVALID_READOUT_VERIFICATION_FLAG")
        if readout[field] is False:
            missing.append("readout." + field)

    design = passport["design"]
    _check_keys(design, "design")
    if design["independence_unit"] != "synthesis_batch":
        raise PilotContractError("INDEPENDENCE_UNIT_NOT_REGISTERED")
    cal_ids = _ids(design["calibration_group_ids"], "calibration")
    ev_ids = _ids(design["evaluation_group_ids"], "evaluation")
    if cal_ids & ev_ids:
        raise PilotContractError("CALIBRATION_EVALUATION_GROUP_OVERLAP")
    if not cal_ids:
        missing.append("design.calibration_group_ids")
    if not ev_ids:
        missing.append("design.evaluation_group_ids")
    if type(design["composition_verified"]) is not bool:
        raise PilotContractError("INVALID_COMPOSITION_VERIFICATION_FLAG")
    if design["composition_verified"] is False:
        missing.append("design.composition_verified")
    text_fields = (
        "randomization_plan", "processing_conditions", "substrate_control",
        "thickness_control", "structural_contrast_definition",
        "sample_size_and_precision_plan", "measurement_chronology_plan", "missing_data_plan"
    )
    for key in text_fields:
        value = design[key]
        if value is None or not _nonplaceholder(value):
            missing.append("design." + key)
    for key in ("minimum_meaningful_effect_A_per_m",
                "measurement_uncertainty_A_per_m"):
        value = design[key]
        if value is None:
            missing.append("design." + key)
        elif not _real(value, strictly_positive=True):
            raise PilotContractError("NONPHYSICAL_" + key.upper())
    resources = passport["resources"]
    _check_keys(resources, "resources")
    budget = resources["response_budget"]
    if budget is None:
        missing.append("resources.response_budget")
    elif type(budget) is not int or budget <= 0:
        raise PilotContractError("INVALID_EXPERIMENT_BUDGET")
    for key in ("per_measurement_cost", "abstention_cost", "measurement_seconds"):
        value = resources[key]
        if value is None:
            missing.append("resources." + key)
        elif not _real(value, strictly_positive=(key != "abstention_cost")):
            raise PilotContractError("INVALID_EXPERIMENT_RESOURCE")
        elif key == "abstention_cost" and value < 0:
            raise PilotContractError("INVALID_ABSTENTION_COST")
    if not _nonplaceholder(resources["cost_unit"]):
        missing.append("resources.cost_unit")
    governance = passport["governance"]
    _check_keys(governance, "governance")
    for field in FIELD_KEYS["governance"]:
        if type(governance[field]) is not bool:
            raise PilotContractError("INVALID_GOVERNANCE_FLAG")
        if governance[field] is False:
            missing.append("governance." + field)
    evidence = passport["evidence"]
    _check_keys(evidence, "evidence")
    for field in ("new_prospective_measurements_available",
                  "independent_validation_available",
                  "authentic_measurement_log_verified",
                  "historical_nist_used_as_holdout"):
        if evidence[field] is not False:
            raise PilotContractError("UNSUPPORTED_PHYSICAL_EVIDENCE_OR_OLD_HOLDOUT")
    source_hash = evidence["source_sha256"]
    if source_hash is None:
        missing.append("evidence.source_sha256")
    elif (type(source_hash) is not str or len(source_hash) != 64 or
          any(c not in "0123456789abcdef" for c in source_hash)):
        raise PilotContractError("INVALID_EVIDENCE_SHA256")
    if not _nonplaceholder(evidence["source_license"]):
        missing.append("evidence.source_license")
    release = passport["release"]
    _check_keys(release, "release")
    if any(value is not False for value in release.values()):
        raise PilotContractError("PROHIBITED_RELEASE_OR_PHYSICAL_ACTION")
    references = passport["references"]
    if (type(references) is not list or len(references) < 2 or
            any(type(u) is not str or not u.startswith("https://") for u in references)
            or len(set(references)) != len(references)):
        raise PilotContractError("INVALID_PRIOR_RESEARCH_REFERENCES")
    if raw_sha256 is not None and (type(raw_sha256) is not str or
                                   len(raw_sha256) != 64):
        raise PilotContractError("INVALID_PASSPORT_DIGEST")
    return {
        "study_id": passport["study_id"],
        "schema_version": SCHEMA,
        "passport_sha256": raw_sha256,
        "structural_contract_passed": True,
        "blocking_fields": sorted(missing),
        "blocking_count": len(missing),
        "has_external_scientific_review": False,
        "independent_physical_validation_established": False,
        "model_families_physically_verified": False,
        "posterior_calibration_established": False,
        "statistical_risk_guarantee_established": False,
        "real_savings_measured": False,
        "physical_recommendation_allowed": False,
        "laboratory_action_allowed": False,
        "decision": "NO_GO_EXTERNAL_REVIEW_REQUIRED",
        "existing_historical_source_used_for_validation": False,
    }


def audit_passport_bytes(raw: bytes):
    passport = parse_passport(raw)
    return validate_passport(passport, raw_sha256=hashlib.sha256(raw).hexdigest())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--passport", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.passport is None and args.out is None:
        print("Protocol-only: no measurements, no validation outcome, no action.")
        return 0
    if args.passport is None or args.out is None:
        parser.error("Both --passport and --out are required")
    report = audit_passport_bytes(args.passport.read_bytes())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("Passport inspected; physical actions and validation claims remain prohibited.")
    print("Unresolved review fields:", report["blocking_count"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
