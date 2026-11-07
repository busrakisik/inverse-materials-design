"""BHS v12.6: post-result group-risk and physical intake contracts.

No physical source is accessed. No acquisition selector is invoked.
All archived v12.5 thresholds and numerical results are read-only.
Passing structural checks never authorizes a laboratory recommendation.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, datetime
import hashlib
import json
import math
from pathlib import Path

from scipy.stats import beta

EXPECTED_CALIBRATION_SHA256 = "fe47b0f79d04ff45df39498559d59dbfc941796c2d195dec4b1cfa4e406cfd48"
EXPECTED_EVALUATION_SHA256 = "654def586730c51793cf4040752770349a25dbcd4c808da86469a5f649e7b831"
FROZEN_PROTOCOL_BLOB = "719431338ee9cd0b3ecc50d197b946aeb79c4701"
CAL_GROUPS = (101, 103, 107, 109)
EVAL_GROUPS = (211, 223, 227, 229)
POLICIES = (
    "random_bundled", "gp_ard_bundled", "gp_pooled_noise_ivr",
    "gp_pooled_noise_ei", "evidence_gate_native", "evidence_gate_completion",
)
ORDER_VARIANTS = (0, 1)
PRIMARY_COVERAGE = "0.50"
REGRET_TOLERANCE = 0.35
GROUP_CONFIDENCE = 0.95
ILLUSTRATIVE_ERROR_TARGET = 0.25
MAX_INTAKE_BYTES = 5_000_000

class EvidenceContractError(ValueError):
    """Fail closed when an archived report or physical-source contract is invalid."""


def _require(condition: bool, message: str):
    if not condition:
        raise EvidenceContractError(message)


def _num(x, *, nonnegative=False, positive=False):
    if type(x) not in (int, float):
        return False
    z = float(x)
    return math.isfinite(z) and (not nonnegative or z >= 0.0) and (not positive or z > 0.0)


def _digest_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _stable_digest(value) -> str:
    content = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return _digest_bytes(content)


def _json_bytes(raw: bytes):
    _require(type(raw) is bytes and len(raw) <= MAX_INTAKE_BYTES, "INVALID_SOURCE_BYTES")
    try:
        return json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")),
        )
    except (ValueError, UnicodeError, TypeError) as exc:
        raise EvidenceContractError("INVALID_JSON_DOCUMENT") from exc


def _looks_sha256(s):
    return (type(s) is str and len(s) == 64
            and all(char in "0123456789abcdef" for char in s))


def _check_rows(rows, *, split, groups):
    _require(type(rows) is list and len(rows) == 48, "BAD_CAMPAIGN_COUNT")
    expected = {(g, v, p) for g in groups for v in ORDER_VARIANTS for p in POLICIES}
    observed_keys = set()
    sources = {}
    for row in rows:
        _require(type(row) is dict, "NONMAPPING_CAMPAIGN")
        g, v, p = row.get("group"), row.get("order_variant"), row.get("policy")
        _require(type(g) is int and type(v) is int and p in POLICIES
                 and g in groups and v in ORDER_VARIANTS and row.get("split") == split,
                 "UNEXPECTED_CAMPAIGN_SPLIT_OR_KEY")
        key = (g, v, p)
        _require(key not in observed_keys, "DUPLICATED_CAMPAIGN")
        observed_keys.add(key)
        fingerprint = row.get("source_fingerprint")
        _require(_looks_sha256(fingerprint), "INVALID_GROUP_FINGERPRINT")
        _require(g not in sources or sources[g] == fingerprint, "GROUP_SOURCE_CHANGED")
        sources[g] = fingerprint
        regret, high = row.get("latent_recommendation_regret"), row.get("high_regret_error")
        _require(_num(regret, nonnegative=True) and type(high) is bool
                 and high == (regret > REGRET_TOLERANCE), "REGRET_LABEL_INCONSISTENT")
        _require(_num(row.get("evidence_score"), nonnegative=True), "INVALID_EVIDENCE_SCORE")
        _require(type(row.get("measurement_count")) is int
                 and row["measurement_count"] == 48, "MEASUREMENT_BUDGET_CHANGED")
        for field in ("completed_designs", "incomplete_designs",
                      "stranded_partial_responses", "completion_interventions"):
            _require(type(row.get(field)) is int and row[field] >= 0, "INVALID_COST_COUNT")
        _require(row.get("latent_outcomes_passed_to_selector") is False
                 and row.get("future_responses_passed_to_selector") is False,
                 "SELECTOR_LEAKAGE_FLAG")
    _require(observed_keys == expected and len(sources) == len(groups),
             "MISSING_CAMPAIGNS")
    return sources


def _check_document(raw: bytes, *, kind: str):
    expected_hash = (EXPECTED_CALIBRATION_SHA256 if kind == "calibration"
                     else EXPECTED_EVALUATION_SHA256)
    _require(_digest_bytes(raw) == expected_hash, "ARCHIVED_JSON_SHA256_MISMATCH")
    obj = _json_bytes(raw)
    _require(type(obj) is dict and obj.get("stage") == kind
             and obj.get("protocol_blob") == FROZEN_PROTOCOL_BLOB,
             "ARCHIVE_IDENTITY_MISMATCH")
    rows = obj.get(f"{kind}_rows")
    _require(_stable_digest(rows) == obj.get(f"{kind}_rows_digest"),
             "ARCHIVED_ROWS_DIGEST_CHANGED")
    groups = CAL_GROUPS if kind == "calibration" else EVAL_GROUPS
    _require(obj.get(f"{kind}_groups") == list(groups), "GROUP_ASSIGNMENT_CHANGED")
    sources = _check_rows(rows, split=kind, groups=groups)
    gates = obj.get("hard_gates")
    _require(type(gates) is dict and gates.get("development_only") is True
             and all(gates.get(k) is False for k in (
                 "scored_validation_allowed", "independent_holdout_used",
                 "physical_validation_by_bhs", "claim_of_superiority",
                 "real_savings_measured", "reserved_nist_seeds_used")),
             "EVIDENCE_BOUNDARY_CHANGED")
    return obj, sources


def hypothetical_group_upper_bound(failures: int, covered_groups: int, confidence=0.95):
    """One-sided exact binomial upper limit *if covered groups were iid*.

    Not applicable as a verified physical error guarantee to this archive.
    """
    _require(type(failures) is int and type(covered_groups) is int
             and 0 <= failures <= covered_groups
             and type(confidence) is float and 0 < confidence < 1,
             "INVALID_BINOMIAL_INPUT")
    if covered_groups == 0:
        return None
    if failures == covered_groups:
        return 1.0
    return float(beta.ppf(confidence, failures + 1, covered_groups - failures))


def minimum_zero_error_groups(target=0.25, confidence=0.95):
    _require(_num(target, positive=True) and target < 1
             and _num(confidence, positive=True) and confidence < 1,
             "INVALID_RISK_ILLUSTRATION")
    # Zero-error upper 1-(1-confidence)**(1/n) <= target.
    return int(math.ceil(math.log(1-confidence) / math.log(1-target)))


def audit_v125(calibration_bytes: bytes, evaluation_bytes: bytes):
    """Post hoc descriptive regrouping. Archived thresholds remain unchanged."""
    cal, cal_sources = _check_document(calibration_bytes, kind="calibration")
    ev, eval_sources = _check_document(evaluation_bytes, kind="evaluation")
    _require(not set(cal_sources) & set(eval_sources)
             and not set(cal_sources.values()) & set(eval_sources.values()),
             "CALIBRATION_EVALUATION_SOURCE_OVERLAP")
    _require(cal.get("untouched_evaluation_groups") == list(EVAL_GROUPS)
             and ev.get("calibration_groups") == list(CAL_GROUPS)
             and ev.get("calibration_file_sha256") == EXPECTED_CALIBRATION_SHA256,
             "FROZEN_CALIBRATION_LINK_MISMATCH")
    thresholds = cal.get("thresholds")
    _require(type(thresholds) is dict and set(thresholds) == set(POLICIES)
             and ev.get("thresholds_frozen_from_calibration") == thresholds,
             "EVALUATION_THRESHOLDS_CHANGED")
    _require(ev.get("physical_measurements_performed") is False
             and ev.get("historical_source_accessed") is False,
             "UNSUPPORTED_SOURCE_DECLARATION")
    report = {}
    for policy in POLICIES:
        _require(PRIMARY_COVERAGE in thresholds[policy], "PRIMARY_THRESHOLD_MISSING")
        threshold = thresholds[policy][PRIMARY_COVERAGE].get("threshold")
        _require(_num(threshold), "INVALID_FROZEN_THRESHOLD")
        rows = [r for r in ev["evaluation_rows"] if r["policy"] == policy]
        by_group = {g: [r for r in rows if r["group"] == g] for g in EVAL_GROUPS}
        accepted_groups = 0
        failed_groups = 0
        accepted_decisions = 0
        failed_decisions = 0
        detail = {}
        for group, variants in by_group.items():
            _require(len(variants) == 2, "WRONG_GROUP_MULTIPLICITY")
            accepted = [r for r in variants if r["evidence_score"] > threshold]
            errors = sum(r["high_regret_error"] for r in accepted)
            accepted_decisions += len(accepted)
            failed_decisions += errors
            is_covered = bool(accepted)
            has_failure = bool(errors)
            accepted_groups += int(is_covered)
            failed_groups += int(has_failure)
            detail[str(group)] = {
                "accepted_decisions": len(accepted),
                "failed_decisions": errors,
                "covered": is_covered,
                "any_accepted_failure": has_failure,
            }
        report[policy] = {
            "evaluation_decisions": 8,
            "accepted_decisions": accepted_decisions,
            "failed_accepted_decisions": failed_decisions,
            "evaluation_groups": 4,
            "covered_groups": accepted_groups,
            "failed_covered_groups": failed_groups,
            "decision_coverage": accepted_decisions / 8,
            "group_coverage": accepted_groups / 4,
            "observed_group_failure_rate": (
                failed_groups / accepted_groups if accepted_groups else None),
            "hypothetical_iid_group_upper_95": hypothetical_group_upper_bound(
                failed_groups, accepted_groups, GROUP_CONFIDENCE),
            "zero_coverage": accepted_groups == 0,
            "by_group": detail,
            "physical_recommendation_allowed": False,
            "independent_validation_established": False,
            "statistical_guarantee_supported": False,
        }
    return {
        "study": "BHS v12.6 read-only post-result group-risk audit",
        "evidence_type": "previously_seen_manufactured_development_only",
        "new_measurements_performed": False,
        "thresholds_changed": False,
        "calibration_json_sha256": EXPECTED_CALIBRATION_SHA256,
        "evaluation_json_sha256": EXPECTED_EVALUATION_SHA256,
        "historical_source_accessed": False,
        "independent_physical_validation": False,
        "iid_independence_assumed_for_display_only": True,
        "iid_independence_verified": False,
        "minimum_independent_zero_error_groups_illustration": minimum_zero_error_groups(
            ILLUSTRATIVE_ERROR_TARGET, GROUP_CONFIDENCE),
        "policies": report,
        "physical_recommendation_allowed": False,
        "statistical_guarantee_supported": False,
    }


def validate_prospective_intake(raw_bytes: bytes, manifest: dict):
    """Structural checker; external signatures, science and safety stay unverified.

    The checksum authenticates only the supplied bytes against a supplied digest.
    Actual provenance and human approvals require verification outside this code.
    """
    _require(type(manifest) is dict, "INVALID_INTAKE_MANIFEST")
    required_strings = ("source_id", "source_license", "units", "review_reference")
    _require(all(type(manifest.get(k)) is str and bool(manifest[k].strip())
                 for k in required_strings), "MISSING_PROSPECTIVE_METADATA")
    _require(_looks_sha256(manifest.get("raw_sha256"))
             and _digest_bytes(raw_bytes) == manifest["raw_sha256"],
             "INTAKE_SOURCE_DIGEST_MISMATCH")
    cg, eg = manifest.get("calibration_groups"), manifest.get("evaluation_groups")
    _require(type(cg) is list and type(eg) is list
             and all(type(v) is str and bool(v.strip()) for v in cg+eg)
             and len(set(cg)) == len(cg) and len(set(eg)) == len(eg)
             and cg and eg and not set(cg) & set(eg), "PROSPECTIVE_GROUP_SPLIT_INVALID")
    records = _json_bytes(raw_bytes)
    _require(type(records) is list and records, "INVALID_PROSPECTIVE_RECORDS")
    events, replicates = set(), set()
    seen_groups = {"calibration": set(), "evaluation": set()}
    design_split, synth_split, measurement_split = {}, {}, {}
    chronology = defaultdict(list)
    for row in records:
        _require(type(row) is dict, "INVALID_PROSPECTIVE_ROW")
        split = row.get("split")
        group = row.get("group_id")
        _require(split in ("calibration", "evaluation")
                 and group in (cg if split == "calibration" else eg),
                 "INVALID_PROSPECTIVE_GROUP")
        seen_groups[split].add(group)
        for field in ("event_id", "design_id", "site_id", "instrument_id",
                      "instrument_calibration_ref", "synthesis_batch_id",
                      "measurement_batch_id", "timestamp", "experiment_date"):
            _require(type(row.get(field)) is str and bool(row[field].strip()),
                     "MISSING_MEASUREMENT_PROVENANCE")
        _require(row.get("units") == manifest["units"], "MEASUREMENT_UNIT_MISMATCH")
        ordinal = row.get("replicate_ordinal")
        _require(type(ordinal) is int and 1 <= ordinal <= 3,
                 "INVALID_REPLICATE_ORDINAL")
        _require(_num(row.get("value")) and _num(row.get("reported_uncertainty"), positive=True)
                 and _num(row.get("acquisition_cost"), positive=True)
                 and _num(row.get("acquisition_seconds"), positive=True),
                 "INVALID_MEASUREMENT_VALUE_OR_COST")
        try:
            instant = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            event_date = date.fromisoformat(row["experiment_date"])
        except ValueError as exc:
            raise EvidenceContractError("INVALID_EXPERIMENT_TIME") from exc
        _require(instant.tzinfo is not None and instant.utcoffset() is not None
                 and instant.date() == event_date,
                 "TIMEZONE_OR_DATE_UNVERIFIED")
        event = row["event_id"]
        rep = (group, row["design_id"], ordinal)
        _require(event not in events and rep not in replicates,
                 "DUPLICATE_EVENT_OR_REPLICATE")
        events.add(event)
        replicates.add(rep)
        chronology[(group, row["design_id"])].append((ordinal, instant))
        for field, previous in (("design_id", design_split),
                                ("synthesis_batch_id", synth_split),
                                ("measurement_batch_id", measurement_split)):
            item = row[field]
            _require(item not in previous or previous[item] == split,
                     "CROSS_SPLIT_DESIGN_OR_BATCH_LEAKAGE")
            previous[item] = split
    _require(seen_groups == {"calibration": set(cg), "evaluation": set(eg)},
             "MISSING_PROSPECTIVE_GROUP")
    for key, sequence in chronology.items():
        ordered = sorted(sequence)
        ordinals = [a for a, _ in ordered]
        _require(ordinals == list(range(1, len(ordered)+1))
                 and all(ordered[j][1] < ordered[j+1][1]
                         for j in range(len(ordered)-1)),
                 "NONCHRONOLOGICAL_OR_MISSING_REPLICATES")
    return {
        "structural_record_count": len(records),
        "calibration_group_count": len(cg),
        "evaluation_group_count": len(eg),
        "source_sha256_matched": True,
        "split_and_replicate_structure_accepted": True,
        "source_authenticity_externally_verified": False,
        "instrument_calibration_externally_verified": False,
        "investigator_approval_externally_verified": False,
        "physical_recommendation_allowed": False,
        "statistical_guarantee_supported": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--calibration", type=Path)
    p.add_argument("--evaluation", type=Path)
    p.add_argument("--out", type=Path)
    args = p.parse_args(argv)
    if args.calibration is None and args.evaluation is None and args.out is None:
        print("Read-only risk and physical intake contracts; no study executed.")
        return 0
    if args.calibration is None or args.evaluation is None or args.out is None:
        p.error("Both frozen archives and an output are required")
    report = audit_v125(args.calibration.read_bytes(), args.evaluation.read_bytes())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print("Post-result descriptive audit complete; no independence or physical guarantee.")
    print("Output:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
