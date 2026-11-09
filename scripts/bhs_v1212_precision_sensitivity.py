"""V12.12 outcome-free conditional variance analysis of historical design fixtures."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

PINS = {
    "v129": ("research/BHS_V129_DESIGN_VARIANTS.json", "e65e85a6c2d1a8fed749fdd3502c9021343ca53bb01fb0ec06306101961abde6"),
    "v1210": ("research/BHS_V1210_ASSIGNMENT_UNIT_FIXTURES.json", "adc920e2eba62c7e86ad93b227a0327c692952e0bbb2036907c38326974a5a42"),
}
COMPONENTS = ("run", "session", "coupon", "trace")


def load_frozen(root: Path) -> dict:
    out = {}
    for version, (name, pin) in PINS.items():
        raw = (root / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != pin:
            raise ValueError("FROZEN_SOURCE_HASH_MISMATCH:" + name)
        doc = json.loads(raw)
        if version == "v129":
            scenarios = doc["variants"]
        else:
            scenarios = doc["scenarios"]
        for title, scenario in scenarios.items():
            if any(scenario.get(flag) is True for flag in (
                    "physical_action_allowed", "raw_outcomes_present", "new_physical_measurements_present")):
                raise ValueError("OUTCOME_OR_ACTION_PRESENT")
            out[version + "/" + title] = [dict(row) for row in scenario["specimens"]]
    return out


def _block(row: dict) -> str:
    return str(row.get("matched_block_id", row.get("synthesis_batch_id", "")))


def _run(row: dict) -> str:
    return str(row.get("source_deposition_run_id", row.get("synthesis_batch_id", "")))


def paired_coefficients(rows: list[dict]) -> dict:
    """Exact linear variance coefficients, no noise values or physical outcomes."""
    seen = set()
    paired = defaultdict(dict)
    for row in rows:
        coupon = row.get("coupon_id")
        block = _block(row)
        arm = row.get("processing_arm")
        traces = row.get("planned_moke_traces")
        if not isinstance(coupon, str) or not coupon or coupon in seen:
            raise ValueError("BAD_COUPON_ID")
        seen.add(coupon)
        if not block or not _run(row) or not row.get("moke_session_id"):
            raise ValueError("MISSING_GROUP_ID")
        if arm not in ("reference", "modified") or arm in paired[block]:
            raise ValueError("DUPLICATE_OR_INVALID_ARM")
        if type(traces) is not int or traces < 1:
            raise ValueError("INVALID_TRACE_COUNT")
        paired[block][arm] = row
    valid = {b: arm_rows for b, arm_rows in paired.items() if len(arm_rows) == 2}
    count = len(valid)
    if count < 2:
        return {"status": "NOT_ESTIMABLE", "complete_pairs": count, "coefficients": None}
    group_weights = {"run": defaultdict(Fraction), "session": defaultdict(Fraction)}
    coefficients = {label: Fraction(0) for label in COMPONENTS}
    for block, arm_rows in valid.items():
        for arm, row in arm_rows.items():
            weight = Fraction(1 if arm == "modified" else -1, count)
            group_weights["run"][_run(row)] += weight
            group_weights["session"][str(row["moke_session_id"])] += weight
            coefficients["coupon"] += weight * weight
            coefficients["trace"] += weight * weight / int(row["planned_moke_traces"])
    for component in ("run", "session"):
        coefficients[component] = sum((w * w for w in group_weights[component].values()), Fraction(0))
    return {"status": "CONDITIONAL_COEFFICIENTS_ONLY", "complete_pairs": count,
            "coefficients": {label: str(coefficients[label]) for label in COMPONENTS}}


def loss_sweep(rows: list[dict], group_func) -> dict:
    ids = sorted({str(group_func(r)) for r in rows})
    runs = []
    for key in ids:
        remaining = [r for r in rows if str(group_func(r)) != key]
        audit = paired_coefficients(remaining)
        runs.append({"deleted_id": key, **audit})
    return {"tested_deletions": len(ids), "results": runs}


def evaluate(root: Path) -> dict:
    scenarios = load_frozen(root)
    result = {}
    for name, rows in sorted(scenarios.items()):
        result[name] = {
            "full": paired_coefficients(rows),
            "loss_one_source_run": loss_sweep(rows, _run),
            "loss_one_session": loss_sweep(rows, lambda r: r["moke_session_id"]),
            "loss_one_matched_block": loss_sweep(rows, _block),
        }
    return {
        "schema": "BHS-V12.12",
        "study_type": "outcome_free_conditional_sensitivity",
        "fixture_sha256": {k: v[1] for k, v in PINS.items()},
        "model": "independent_zero_mean_random_intercepts_additive",
        "measurement_unit": "coercive_field_A_per_m_not_observed",
        "hypothetical_noise_sd_ratios": {"coupon": 1, "trace": 1, "run": [0, 1, 2], "session": [0, 1, 2]},
        "findings": result,
        "development_only": True,
        "independent_holdout_used": False,
        "physical_validation_by_bhs": False,
        "formal_power_or_precision_established": False,
        "claim_of_superiority": False,
        "laboratory_action_allowed": False,
    }


def conditional_variance(coefficients: dict, run_sd: float, session_sd: float,
                         coupon_sd: float = 1.0, trace_sd: float = 1.0) -> float:
    if coefficients is None or min(run_sd, session_sd, coupon_sd, trace_sd) < 0:
        raise ValueError("MISSING_COEFFICIENTS_OR_BAD_SD")
    return float(sum(Fraction(coefficients[name]) * sd ** 2 for name, sd in (
        ("run", run_sd), ("session", session_sd),
        ("coupon", coupon_sd), ("trace", trace_sd))))


def write_first_report(root: Path, target: Path) -> None:
    obj = evaluate(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    write_first_report(args.root, args.out)
