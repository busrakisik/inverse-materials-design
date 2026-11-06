"""BHS v7: evidence-sufficiency and robust-risk contract for scientific decisions.

This is deterministic decision-governance software, NOT a calibrated laboratory
recommendation engine. No synthetic test implies prospective scientific safety.
It cannot authenticate a referenced external record; that requires expert review.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VALID_LEVELS = ("descriptive", "observational", "laboratory")
VALID_STATES = ("verified", "missing", "unknown", "contradicted")
BASE = ("source_identity", "schema_and_units", "source_integrity")
REQUIRED = {
    "descriptive": BASE,
    "observational": BASE + (
        "batch_identity", "curing_conditions", "testing_protocol",
        "replicate_uncertainty",
    ),
    "laboratory": BASE + (
        "batch_identity", "curing_conditions", "testing_protocol",
        "replicate_uncertainty", "controlled_intervention",
        "randomization_or_blocking", "instrument_calibration",
        "independent_performance_evidence", "expert_protocol_approval",
    ),
}

def _decision(status, level, reason_codes, evidence_requested=(), **extra):
    return {
        "study": "BHS v7 evidence sufficiency and selective-decision contract",
        "requested_level": level,
        "status": status,
        "reason_codes": list(reason_codes),
        "evidence_requested": sorted(set(evidence_requested)),
        "automatic_laboratory_action_authorized": False,
        "human_review_required_for_laboratory_action": True,
        "independent_holdout_used": False,
        "physical_validation": False,
        "development_only": True,
        **extra,
    }


def assess(level, evidence, *, risk=None):
    """Fail closed on invalid provenance, contradictory or absent source checks.

    evidence is a mapping: id -> {status: ..., source_ref: ...}. A source_ref is
    a *pointer* not independent authentication; humans must check originals.
    """
    if level not in VALID_LEVELS:
        return _decision("ABSTAIN_INVALID_INPUT", str(level), ["UNKNOWN_DECISION_LEVEL"])
    if not isinstance(evidence, dict):
        return _decision("ABSTAIN_INVALID_INPUT", level, ["EVIDENCE_NOT_A_MAPPING"])
    if any(not isinstance(key, str) or not isinstance(value, dict)
           or value.get("status") not in VALID_STATES
           for key, value in evidence.items()):
        return _decision("ABSTAIN_INVALID_INPUT", level, ["MALFORMED_EVIDENCE"])
    required = REQUIRED[level]
    contradictions = [name for name in required if
                      evidence.get(name, {}).get("status") == "contradicted"]
    missing = [name for name in required if
               evidence.get(name, {}).get("status") in (None, "missing", "unknown")]
    unproven = [name for name in required if
                evidence.get(name, {}).get("status") == "verified"
                and (not isinstance(evidence[name].get("source_ref"), str)
                     or not evidence[name]["source_ref"].strip())]
    if unproven:
        return _decision("ABSTAIN_INVALID_PROVENANCE", level, ["VERIFIED_WITHOUT_SOURCE_REFERENCE"],
                         evidence_requested=unproven)
    if contradictions:
        return _decision("ABSTAIN_CONTRADICTED_ASSUMPTIONS", level,
                         ["CONTRADICTED:" + name for name in contradictions],
                         evidence_requested=contradictions)
    if missing:
        return _decision("REQUEST_ADDITIONAL_EVIDENCE", level,
                         ["EVIDENCE_UNAVAILABLE:" + name for name in missing],
                         evidence_requested=missing)
    # All required evidence is present and has a named provenance reference.
    # That does not establish its validity; references still need human audit.
    if level == "descriptive":
        return _decision("DESCRIPTIVE_REPORT_ONLY", level,
                         ["EVIDENCE_REFERENCES_REQUIRE_VERIFICATION"])
    if level == "observational":
        return _decision("OBSERVATIONAL_REVIEW_ONLY", level,
                         ["OBSERVATIONAL_ASSOCIATION_NOT_CAUSAL",
                          "EVIDENCE_REFERENCES_REQUIRE_VERIFICATION"])
    if not isinstance(risk, dict):
        return _decision("ABSTAIN_UNBOUNDED_DECISION_RISK", level,
                         ["NO_PREDECLARED_RISK_BOUND"])

    names = ("lower_success_probability", "benefit_if_correct",
             "harm_if_wrong", "abstention_cost")
    try:
        lower, benefit, harm, abstention = (float(risk[name]) for name in names)
    except (KeyError, ValueError, TypeError, OverflowError):
        return _decision("ABSTAIN_INVALID_RISK_INPUT", level, ["MISSING_OR_INVALID_RISK_TERMS"])
    if (not all(map(math.isfinite, (lower, benefit, harm, abstention)))
            or not 0 <= lower <= 1 or not benefit > 0
            or harm < 0 or abstention < 0):
        return _decision("ABSTAIN_INVALID_RISK_INPUT", level, ["OUT_OF_RANGE_RISK_TERMS"])

    if risk.get("lower_bound_provenance") != evidence["independent_performance_evidence"]["source_ref"]:
        return _decision("ABSTAIN_INVALID_RISK_PROVENANCE", level,
                         ["RISK_BOUND_NOT_LINKED_TO_INDEPENDENT_EVIDENCE"])

    # Worst-case expected utility at the independently supported lower
    # probability bound. Numbers must use coherent, domain-reviewed units.
    worst_case_action_utility = lower * benefit - (1.0 - lower) * harm
    abstain_utility = -abstention
    metric = {
        "worst_case_action_utility": worst_case_action_utility,
        "abstain_utility": abstain_utility,
        "decision_margin": worst_case_action_utility - abstain_utility,
        "threshold_probability": (harm - abstention) / (benefit + harm),
        "utility_units": risk.get("utility_units", "unspecified"),
        "risk_values_are_self_reported": True,
        "risk_probability_independently_verified_by_code": False,
    }
    if worst_case_action_utility <= abstain_utility:
        return _decision("ABSTAIN_RISK_NOT_ACCEPTABLE", level,
                         ["WORST_CASE_ACTION_VALUE_NOT_ABOVE_ABSTENTION"], risk_assessment=metric)
    return _decision("ELIGIBLE_FOR_EXPERT_REVIEW", level,
                     ["PROVENANCE_AND_RISK_REQUIRE_INDEPENDENT_EXPERT_CONFIRMATION"],
                     risk_assessment=metric)


def v6_source_case(source_report):
    """Map only OBSERVED v6 evidence to v7 fields; do not invent lab metadata."""
    if not isinstance(source_report, dict) or source_report.get("decision", {}).get(
            "status") != "ABSTAIN_FROM_PHYSICAL_OR_LAB_RECOMMENDATION":
        raise ValueError("Expected a v6 observation record with explicit refusal.")
    src = source_report.get("source", {})
    if src.get("dataset_id") != 165 or src.get("parsed_table_sha256") != (
            "98958f558e46763cf6d5403de8784af39ebe906c4604447c188889c3e346cd87"):
        raise ValueError("Source identity / parsed table fingerprint does not match the audited accession.")
    evidence = {
        "source_identity": {"status": "verified", "source_ref": "UCI-165:10.24432/C5PK67"},
        "schema_and_units": {"status": "verified", "source_ref": "UCI-165:published-metadata"},
        "source_integrity": {"status": "verified", "source_ref": "v6:parsed-fingerprint"},
    }
    for name in REQUIRED["laboratory"]:
        if name not in evidence:
            evidence[name] = {"status": "missing", "source_ref": None}
    return evidence


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v6-json", default="research/uci_concrete_assumptions_v6.json")
    parser.add_argument("--out", default="runs/bhs_evidence_sufficiency_v7.json")
    args = parser.parse_args(argv)
    v6 = json.loads(Path(args.v6_json).read_text(encoding="utf-8"))
    evidence = v6_source_case(v6)
    report = {
        "source_study": "v6 real UCI 165 assumption audit",
        "evidence_source": args.v6_json,
        "decisions": {
            level: assess(level, evidence)
            for level in VALID_LEVELS
        },
        "status_note": ("Deterministic evidence triage, not empirical validation "
                        "of risk, causal findings or improved laboratory outcomes."),
    }
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({name: result["status"] for name, result in report["decisions"].items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
