"""V12.3 source-independent controlled measurement-order evaluation.

A private evaluator holds deterministic manufactured latent values and outcomes.
Selectors receive candidate descriptors and already revealed response values only.
No historical source files, protected seeds or physical results are used here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from scripts.bhs_measurement_allocation_v12 import (
    INITIAL_GEOMETRIES, INITIAL_MEASUREMENTS, REPEATS, TOTAL_MEASUREMENTS,
    MeasurementContractError, initial_geometry_ids, require_development_seed,
)
from scripts.bhs_v121_order_contracts import select_canonical_measurement
from scripts.bhs_v122_adaptive_gp_reference import select_gp_measurement

DESCRIPTOR_SEED = 20261107
NOISE_SEED = 73123
POOL_SIZE = 48
SEEDS = (7, 13)
ORDER_VARIANTS = (0, 1)
REGIMES = ("constant", "varying")
POLICIES = (
    "random_bundled", "gp_ard_bundled", "evidence_gate_development",
    "gp_pooled_noise_ivr", "gp_pooled_noise_ei",
)
BUNDLED_AND_GATE = POLICIES[:3]
HARD_GATES = {
    "development_only": True,
    "scored_validation_allowed": False,
    "independent_holdout_used": False,
    "physical_validation_by_bhs": False,
    "causal_identification": False,
    "calibrated_uncertainty_proven": False,
    "claim_of_superiority": False,
    "real_savings_measured": False,
    "reserved_nist_seeds_used": False,
}


@dataclass(frozen=True)
class SyntheticScenario:
    descriptors: np.ndarray
    latent: np.ndarray
    outcomes: np.ndarray
    regime: str
    digest: str


def make_scenario(regime: str) -> SyntheticScenario:
    """Fixed manufactured inputs, unaffected by policy, seed or reveal order."""
    if regime not in REGIMES:
        raise MeasurementContractError("UNKNOWN_SYNTHETIC_REGIME")
    x = np.random.default_rng(DESCRIPTOR_SEED).uniform(-1.0, 1.0, (POOL_SIZE, 4))
    latent = (4.0 + 1.8 * np.sin(1.4 * np.pi * x[:, 0])
              + 0.9 * x[:, 1] ** 2 - 0.7 * x[:, 2] + 0.5 * x[:, 0] * x[:, 3])
    noise = np.random.default_rng(NOISE_SEED).normal(size=(POOL_SIZE, REPEATS))
    sigma = (np.full(POOL_SIZE, 0.35) if regime == "constant"
             else 0.15 + 0.60 * (x[:, 0] + 1.0) / 2.0)
    outcomes = latent[:, None] + sigma[:, None] * noise
    digest = hashlib.sha256(
        np.ascontiguousarray(x, dtype="<f8").tobytes()
        + np.ascontiguousarray(latent, dtype="<f8").tobytes()
        + np.ascontiguousarray(outcomes, dtype="<f8").tobytes()
    ).hexdigest()
    if (x.shape != (POOL_SIZE, 4) or latent.shape != (POOL_SIZE,)
            or outcomes.shape != (POOL_SIZE, REPEATS)
            or not np.isfinite(outcomes).all()):
        raise MeasurementContractError("BAD_SYNTHETIC_SOURCE")
    return SyntheticScenario(x, latent, outcomes, regime, digest)


class ControlledSyntheticOracle:
    """Evaluator-only outcome ledger, deterministic independently of action order."""

    def __init__(self, scenario: SyntheticScenario, seed: int, variant: int):
        require_development_seed(seed)
        if type(variant) is not int or variant not in ORDER_VARIANTS:
            raise MeasurementContractError("UNKNOWN_RESPONSE_ORDER_VARIANT")
        self.__descriptors = np.asarray(scenario.descriptors, float).copy()
        self.__latent = np.asarray(scenario.latent, float).copy()
        self.__outcomes = np.asarray(scenario.outcomes, float).copy()
        if (self.__descriptors.shape != (POOL_SIZE, 4)
                or self.__latent.shape != (POOL_SIZE,)
                or self.__outcomes.shape != (POOL_SIZE, REPEATS)
                or not np.isfinite(self.__latent).all()
                or not np.isfinite(self.__outcomes).all()):
            raise MeasurementContractError("CORRUPTED_PRIVATE_SYNTHETIC_SOURCE")
        self.__permutations = [
            np.random.default_rng(
                np.random.SeedSequence([DESCRIPTOR_SEED, seed, variant, i])
            ).permutation(REPEATS)
            for i in range(POOL_SIZE)
        ]
        self.__ledger = np.zeros(POOL_SIZE, dtype=np.int8)

    def reveal_one(self, idx: int, ordinal: int) -> float:
        if (type(idx) is not int or type(ordinal) is not int
                or not (0 <= idx < POOL_SIZE) or not (1 <= ordinal <= REPEATS)):
            raise MeasurementContractError("INVALID_SYNTHETIC_MEASUREMENT_REQUEST")
        if ordinal != int(self.__ledger[idx]) + 1:
            raise MeasurementContractError("MEASUREMENT_ALREADY_SEEN_OR_OUT_OF_ORDER")
        value = float(self.__outcomes[idx, self.__permutations[idx][ordinal - 1]])
        self.__ledger[idx] += 1
        return value

    def evaluate(self, observed: dict[int, tuple[float, ...]]) -> dict:
        """Check all revealed responses, then score a complete recommendation only."""
        ids = {i for i, count in enumerate(self.__ledger) if count > 0}
        if (not isinstance(observed, dict) or set(observed) != ids
                or any(type(i) is not int for i in observed)):
            raise MeasurementContractError("EVALUATOR_TRANSCRIPT_IDS_DIFFER")
        for idx, values in observed.items():
            count = int(self.__ledger[idx])
            expected = self.__outcomes[idx, self.__permutations[idx][:count]]
            if (not isinstance(values, tuple) or len(values) != count
                    or not np.array_equal(np.asarray(values, float), expected)):
                raise MeasurementContractError("EVALUATOR_TRANSCRIPT_VALUES_DIFFER")
        if int(self.__ledger.sum()) != TOTAL_MEASUREMENTS:
            raise MeasurementContractError("EVALUATOR_BUDGET_NOT_EXACT")
        completed = [i for i, values in observed.items() if len(values) == REPEATS]
        if len(completed) < INITIAL_GEOMETRIES:
            raise MeasurementContractError("NO_COMPLETED_RECOMMENDATION")
        recommended = min(completed, key=lambda i: (-float(np.mean(observed[i])), i))
        optimum = float(np.max(self.__latent))
        regret = max(0.0, optimum - float(self.__latent[recommended]))
        best_completed_regret = max(0.0, optimum - float(np.max(self.__latent[completed])))
        if best_completed_regret > regret + 1e-9:
            raise MeasurementContractError("LATENT_RECOMMENDATION_ORDER_ERROR")
        return {
            "latent_simple_regret": regret,
            "best_completed_latent_regret": best_completed_regret,
            "completed_geometries": len(completed),
            "partial_geometries": len(observed) - len(completed),
            "measurement_count": int(self.__ledger.sum()),
            "selection_sees_latent_quality": False,
            "unobserved_responses_used_by_selector": False,
        }


def choose_action(policy: str, descriptors, observed, *, seed: int, step: int):
    """Only public features, acquired responses, seed and step enter a selector."""
    if policy in BUNDLED_AND_GATE:
        return select_canonical_measurement(
            policy, descriptors, observed, seed=seed, step=step)
    if policy in POLICIES[3:]:
        return select_gp_measurement(
            policy, descriptors, observed, seed=seed, step=step)
    raise MeasurementContractError("UNKNOWN_SYNTHETIC_POLICY")


def run_campaign(scenario: SyntheticScenario, policy: str, seed: int, variant: int):
    """Pass only a public acquired-view into choose_action at each step."""
    if policy not in POLICIES or seed not in SEEDS or type(seed) is not int:
        raise MeasurementContractError("UNEXPECTED_STUDY_POLICY_OR_SEED")
    oracle = ControlledSyntheticOracle(scenario, seed, variant)
    x = np.asarray(scenario.descriptors, float).copy()
    observed: dict[int, tuple[float, ...]] = {}
    for i in initial_geometry_ids(POOL_SIZE, seed):
        observed[i] = tuple(oracle.reveal_one(i, j) for j in range(1, REPEATS + 1))
    for step in range(TOTAL_MEASUREMENTS - INITIAL_MEASUREMENTS):
        visible = {i: tuple(values) for i, values in observed.items()}
        idx, ordinal = choose_action(policy, x.copy(), visible, seed=seed, step=step)
        if (type(idx) is not int or type(ordinal) is not int
                or not (0 <= idx < POOL_SIZE)
                or ordinal != len(observed.get(idx, ())) + 1):
            raise MeasurementContractError("INVALID_SELECTOR_ACTION")
        observed[idx] = observed.get(idx, ()) + (oracle.reveal_one(idx, ordinal),)
    result = oracle.evaluate(observed)
    return {"regime": scenario.regime, "policy": policy, "seed": seed,
            "order_variant": variant, **result}


def run_frozen_study():
    rows = []
    fingerprints = {}
    for regime in REGIMES:
        scenario = make_scenario(regime)
        fingerprints[regime] = scenario.digest
        for seed in SEEDS:
            for variant in ORDER_VARIANTS:
                for policy in POLICIES:
                    rows.append(run_campaign(scenario, policy, seed, variant))
    aggregates = {}
    sensitivity = {}
    for regime in REGIMES:
        aggregates[regime] = {}
        sensitivity[regime] = {}
        for policy in POLICIES:
            sample = [r for r in rows if r["regime"] == regime and r["policy"] == policy]
            aggregates[regime][policy] = {
                "campaigns": len(sample),
                "mean_latent_simple_regret": float(np.mean([r["latent_simple_regret"] for r in sample])),
                "mean_best_completed_latent_regret": float(np.mean([r["best_completed_latent_regret"] for r in sample])),
                "mean_completed_geometries": float(np.mean([r["completed_geometries"] for r in sample])),
                "mean_partial_geometries": float(np.mean([r["partial_geometries"] for r in sample])),
            }
            sensitivity[regime][policy] = {
                str(seed): abs(
                    next(r["latent_simple_regret"] for r in sample if r["seed"] == seed and r["order_variant"] == 0)
                    - next(r["latent_simple_regret"] for r in sample if r["seed"] == seed and r["order_variant"] == 1)
                ) for seed in SEEDS
            }
    return {
        "study": "BHS v12.3 controlled synthetic response-order decision audit",
        "protocol": "research/BHS_V123_CONTROLLED_SYNTHETIC_PROTOCOL.md",
        "historical_physical_source_accessed": False,
        "physical_measurements_performed": False,
        "source_seed": DESCRIPTOR_SEED,
        "noise_seed": NOISE_SEED,
        "regimes": list(REGIMES),
        "decision_seeds": list(SEEDS),
        "order_variants": list(ORDER_VARIANTS),
        "policies": list(POLICIES),
        "pool_size": POOL_SIZE,
        "measurements_per_campaign": TOTAL_MEASUREMENTS,
        "source_digests": fingerprints,
        "campaigns": rows,
        "aggregates": aggregates,
        "order_sensitivity": sensitivity,
        "hard_gates": dict(HARD_GATES),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true",
                        help="Run only the fixed manufactured development study.")
    parser.add_argument("--out", default="runs/bhs_v123_synthetic_decision_audit.json")
    args = parser.parse_args(argv)
    if not args.execute:
        print("Protocol-only mode: no outcomes scored or physical data accessed.")
        return 0
    report = run_frozen_study()
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Source-independent manufactured development study complete.")
    print("Campaigns:", len(report["campaigns"]))
    print("Report:", target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
