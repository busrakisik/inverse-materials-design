"""BHS v6: audit assumptions before physical interpretation of concrete strength.

Development-only source-data diagnostics, not a causal experiment.
No unseen responses are exposed to pair selection; no laboratory mix is recommended.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

from scripts.uci_concrete_v5 import fetch_source, select_28_day_pool

EXPECTED_PARSED_SHA256 = "98958f558e46763cf6d5403de8784af39ebe906c4604447c188889c3e346cd87"
SOURCE_DOI = "10.24432/C5PK67"
FIELD_ORDER = (
    "cement", "blastfurnaceslag", "flyash", "water",
    "superplasticizer", "coarseaggregate", "fineaggregate", "age"
)
MATCH_TOLERANCES_KG_M3 = (5.0, 15.0, 30.0)
MIN_WATER_DIFFERENCE_KG_M3 = 10.0
MIN_WATER_BINDER_RATIO_DIFFERENCE = 0.03
MIN_DISJOINT_PAIRS_FOR_DESCRIPTIVE_REVIEW = 20
REPEATED_PROFILE_SPAN_FLAG_MPA = 1.0
REQUIRED_UNAVAILABLE_CONTEXT = (
    "cement_and_scm_material_identity_and_lot",
    "curing_temperature_and_humidity",
    "specimen_geometry_and_test_protocol",
    "measurement_repeatability_and_uncertainty"
)


class AssumptionViolation(ValueError):
    """A decision must stop because a required observable contract failed."""


def canonical_field_order(columns):
    if len(columns) != len(FIELD_ORDER):
        raise AssumptionViolation("SCHEMA_MISMATCH: require exactly eight known UCI features.")
    actual = tuple(re.sub("[^a-z]", "", str(x).lower()) for x in columns)
    if any(not actual[i].startswith(field) for i, field in enumerate(FIELD_ORDER)):
        raise AssumptionViolation("SCHEMA_MISMATCH: identity/order/units need manual source verification.")
    return actual


def verify_source(features, labels, columns):
    canonical_field_order(columns)
    X = np.asarray(features, dtype=float)
    y = np.asarray(labels, dtype=float).reshape(-1)
    if X.shape != (1030, 8) or y.shape != (1030,):
        raise AssumptionViolation("SOURCE_SHAPE_CHANGED: accession no longer matches the recorded study.")
    if not np.isfinite(X).all() or not np.isfinite(y).all():
        raise AssumptionViolation("INVALID_MEASUREMENT: finite source measurements required.")
    if np.any(X[:, :7] < 0) or np.any(X[:, 7] <= 0):
        raise AssumptionViolation("PHYSICALLY_INVALID_INPUT: negatives or invalid curing ages.")
    if not np.any(np.isclose(X[:, 7], 28.0, rtol=0, atol=1e-9)):
        raise AssumptionViolation("AGE_SUPPORT_ABSENT: no 28-day measurements.")
    selected = np.isclose(X[:, 7], 28.0, rtol=0, atol=1e-9)
    if np.any(X[selected, 0] + X[selected, 1] + X[selected, 2] <= 0):
        raise AssumptionViolation("BINDER_NOT_POSITIVE: undefined water-to-binder ratio.")
    if np.any(X[selected, 0] <= 0):
        raise AssumptionViolation("CEMENT_NOT_POSITIVE: undefined water-to-cement ratio.")
    return X, y


def audit_same_input_repeats(X, y):
    """Measurement inconsistency indicator; do not average away replicate differences."""
    grouped = defaultdict(list)
    for x, outcome in zip(X, y):
        if np.isclose(x[7], 28.0, rtol=0, atol=1e-9):
            grouped[tuple(float(z) for z in x)].append(float(outcome))
    repeated = [v for v in grouped.values() if len(v) > 1]
    spans = [max(v) - min(v) for v in repeated]
    return {
        "duplicate_input_groups": len(repeated),
        "duplicate_input_extra_rows": int(sum(len(v) - 1 for v in repeated)),
        "max_response_span_mpa": float(max(spans)) if spans else 0.0,
        "groups_response_span_over_1_mpa": int(sum(s > REPEATED_PROFILE_SPAN_FLAG_MPA for s in spans)),
        "measurement_noise_model_identified": False
    }


def choose_disjoint_pairs_from_features(X, tolerance):
    """Pair construction uses ONLY measured mixture inputs, never target strengths."""
    a = np.asarray(X, dtype=float)
    if a.ndim != 2 or a.shape[1] != 8 or not np.isfinite(a).all():
        raise AssumptionViolation("INVALID_FEATURE_MATRIX")
    if tolerance not in MATCH_TOLERANCES_KG_M3:
        raise AssumptionViolation("TOLERANCE_NOT_PREDECLARED")
    binder = a[:, 0] + a[:, 1] + a[:, 2]
    if np.any(binder <= 0):
        raise AssumptionViolation("BINDER_NOT_POSITIVE")
    ratio = a[:, 3] / binder
    controls = a[:, [0, 1, 2, 4, 5, 6]]
    edges = []
    for i in range(len(a) - 1):
        # Distance is the maximum difference among SIX other mixture ingredients;
        # this is a screening heuristic, not proof of matched source/curing context.
        differences = np.max(np.abs(controls[i + 1:] - controls[i]), axis=1)
        water_difference = np.abs(a[i + 1:, 3] - a[i, 3])
        ratio_difference = np.abs(ratio[i + 1:] - ratio[i])
        allowed = np.flatnonzero(
            (differences <= tolerance) &
            (water_difference >= MIN_WATER_DIFFERENCE_KG_M3) &
            (ratio_difference >= MIN_WATER_BINDER_RATIO_DIFFERENCE)
        )
        for j0 in allowed:
            j = int(i + j0 + 1)
            edges.append((float(differences[j0]), -float(ratio_difference[j0]), i, j))
    edges.sort()
    used = set()
    disjoint = []
    for _, _, i, j in edges:
        if i not in used and j not in used:
            disjoint.append((i, j))
            used.update((i, j))
    return len(edges), disjoint


def score_descriptive_contrasts(X, y, tolerance):
    possible, pairs = choose_disjoint_pairs_from_features(X, tolerance)
    ratio = X[:, 3] / (X[:, 0] + X[:, 1] + X[:, 2])
    expected, reversed_, tied = 0, 0, 0
    for i, j in pairs:
        # Labels are used here only AFTER pairing and solely for descriptive scoring.
        sign = float((ratio[j] - ratio[i]) * (y[j] - y[i]))
        if sign < 0:
            expected += 1
        elif sign > 0:
            reversed_ += 1
        else:
            tied += 1
    informative = expected + reversed_
    return {
        "other_ingredient_absolute_tolerance_kg_m3": tolerance,
        "eligible_observational_pairs": possible,
        "disjoint_paired_comparisons": len(pairs),
        "direction_matches_water_binder_expectation": expected,
        "direction_opposes_water_binder_expectation": reversed_,
        "tied_strengths": tied,
        "descriptive_direction_fraction": float(expected / informative) if informative else None,
        "passes_arbitrary_minimum_pair_count": bool(len(pairs) >= MIN_DISJOINT_PAIRS_FOR_DESCRIPTIVE_REVIEW),
        "causal_identification_established": False
    }


def analyze(X, y, columns, source_fingerprint):
    X, y = verify_source(X, y, columns)
    if source_fingerprint != EXPECTED_PARSED_SHA256:
        raise AssumptionViolation("SOURCE_VERSION_DRIFT: parsed numerical table hash changed.")
    unique_X, unique_y, pool = select_28_day_pool(X, y, columns)
    repetition = audit_same_input_repeats(X, y)
    match = [score_descriptive_contrasts(unique_X, unique_y, tolerance)
             for tolerance in MATCH_TOLERANCES_KG_M3]
    reasons = [
        "UNRECORDED_CURING_AND_LAB_CONDITIONS",
        "UNMEASURED_SOURCE_AND_TEST_PROTOCOL_CONFOUNDING",
        "OBSERVATIONAL_PAIRING_CANNOT_IDENTIFY_CAUSAL_WATER_EFFECT",
        "NO_VERIFIED_INSTRUMENT_OR_REPLICATION_ERROR_MODEL",
    ]
    if any(x["disjoint_paired_comparisons"] < MIN_DISJOINT_PAIRS_FOR_DESCRIPTIVE_REVIEW for x in match):
        reasons.append("PAIR_SUPPORT_SENSITIVE_TO_MATCH_TOLERANCE")
    if repetition["groups_response_span_over_1_mpa"] > 0:
        reasons.append("IDENTICAL_FEATURE_PROFILES_HAVE_DISCORDANT_STRENGTHS")
    return {
        "study": "BHS v6 assumption audit of water-to-binder contrast at 28 days",
        "source": {"dataset_id": 165, "doi": SOURCE_DOI, "license": "CC BY 4.0",
                   "parsed_table_sha256": source_fingerprint, "original_xls_sha256_verified": False},
        "question": "Is the expected inverse water-to-binder versus 28-day strength pattern assessable under sufficiently comparable observational mixtures?",
        "scope": "exploratory observational diagnostics, not a causal test or lab decision",
        "pool": pool,
        "repeat_audit": repetition,
        "matching_sensitivity": match,
        "assumptions": [
            {"id": "source_schema_age_units", "observed": True, "basis": "UCI metadata and numerical source checks"},
            {"id": "binder_definition", "observed": False, "basis": "cement+slag+fly ash is an explicit proxy; unequal reactivity unverified"},
            {"id": "material_lot_curing_and_test_protocol", "observed": False, "missing": list(REQUIRED_UNAVAILABLE_CONTEXT)},
            {"id": "measurement_noise_and_repeatability", "observed": False, "basis": "no per-sample uncertainty model"},
            {"id": "randomized_water_intervention", "observed": False, "basis": "retrospective observational table"}
        ],
        "decision": {
            "status": "ABSTAIN_FROM_PHYSICAL_OR_LAB_RECOMMENDATION",
            "reason_codes": reasons,
            "permitted_use": "report descriptive pair counts, conflicts and sensitivity only",
            "next_evidence": "domain specialist, matched controlled water intervention, recorded material lots/curing/testing, calibrated replicate variability"
        },
        "evidence_boundaries": {
            "development_only": True,
            "scored_validation_allowed": False,
            "independent_holdout_used": False,
            "physical_validation": False,
            "causal_identification": False,
            "physical_mechanism_confirmed": False,
            "claim_of_superiority": False,
            "laboratory_recipe_recommended": False,
            "reserved_seeds_used": False
        }
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--execute", action="store_true", help="Acquire external UCI observations and run an exploratory audit.")
    p.add_argument("--out", default="runs/uci_concrete_assumptions_v6.json")
    args = p.parse_args(argv)
    if not args.execute:
        print("Protocol only. External observations are not accessed unless --execute is provided.")
        return 0
    X, y, columns, fingerprint = fetch_source()
    report = analyze(X, y, columns, fingerprint)
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_rows": report["pool"]["source_rows"],
        "age_28_unique_profiles": report["pool"]["unique_profiles_age_28"],
        "repeat_audit": report["repeat_audit"],
        "matching_sensitivity": report["matching_sensitivity"],
        "decision": report["decision"]
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
