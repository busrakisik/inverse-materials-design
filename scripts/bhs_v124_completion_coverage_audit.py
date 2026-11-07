"""V12.4 matched completion and abstention audit on manufactured responses.

The evaluator owns all hidden latent quantities, unseen responses and the reveal
ledger. Each selector sees only public descriptors and acquired observations.
There is no historical source retrieval or real laboratory experimentation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from scripts.bhs_measurement_allocation_v12 import (
    INITIAL_GEOMETRIES, INITIAL_MEASUREMENTS, TOTAL_MEASUREMENTS,
    MAX_PENDING_GEOMETRIES, REPEATS, MeasurementContractError,
    initial_geometry_ids, require_development_seed,
)
from scripts.bhs_v123_synthetic_decision_audit import choose_action

SOURCE_SEED = 48121
NOISE_SEED = 79331
POOL_SIZE = 48
SEEDS = (19, 29)
ORDER_VARIANTS = (0, 1)
LANDSCAPES = ("ridge", "oscillatory")
REGIMES = ("constant", "varying")
POLICIES = (
    "random_bundled", "gp_ard_bundled", "gp_pooled_noise_ivr",
    "gp_pooled_noise_ei", "evidence_gate_native",
    "evidence_gate_completion",
)
MATCHED_POLICIES = tuple(p for p in POLICIES if p != "evidence_gate_native")
ABSTENTION_Z = (0.0, 1.0, 1.645)
ABSTENTION_PENALTIES = (0.25, 0.50, 1.0)
PRIMARY_Z = 1.0
PRIMARY_PENALTY = 0.50
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
class ManufacturedSource:
    descriptors: np.ndarray
    latent: np.ndarray
    outcomes: np.ndarray
    landscape: str
    regime: str
    digest: str


def make_source(landscape: str, regime: str) -> ManufacturedSource:
    if landscape not in LANDSCAPES or regime not in REGIMES:
        raise MeasurementContractError("UNKNOWN_MANUFACTURED_SOURCE")
    x = np.random.default_rng(SOURCE_SEED).uniform(-1, 1, (POOL_SIZE, 4))
    if landscape == "ridge":
        latent = (3.0 + 1.4*np.exp(-6.0*(x[:, 0] - .35)**2)
                  + .9*x[:, 1] - .6*x[:, 2]**2 + .5*x[:, 0]*x[:, 3])
    else:
        latent = (3.0 + 1.1*np.sin(2.5*np.pi*x[:, 0])*np.cos(1.5*np.pi*x[:, 1])
                  + .7*x[:, 2]*x[:, 3] - .4*x[:, 1]**2)
    noise = np.random.default_rng(NOISE_SEED).normal(size=(POOL_SIZE, REPEATS))
    sigma = (np.full(POOL_SIZE, .35) if regime == "constant"
             else .15 + .55*(x[:, 0] + 1)/2)
    outcomes = latent[:, None] + sigma[:, None]*noise
    if (x.shape != (POOL_SIZE, 4) or latent.shape != (POOL_SIZE,)
            or outcomes.shape != (POOL_SIZE, REPEATS)
            or not np.isfinite(x).all() or not np.isfinite(latent).all()
            or not np.isfinite(outcomes).all()):
        raise MeasurementContractError("INVALID_MANUFACTURED_SOURCE")
    digest = hashlib.sha256(b"".join(
        np.ascontiguousarray(a, dtype="<f8").tobytes() for a in (x, latent, outcomes)
    )).hexdigest()
    return ManufacturedSource(x, latent, outcomes, landscape, regime, digest)


def _observed_summary(observed):
    completed = [(i, np.asarray(values, float)) for i, values in observed.items()
                 if len(values) == REPEATS]
    if len(completed) < INITIAL_GEOMETRIES:
        raise MeasurementContractError("NO_COMPLETED_DESIGN_FOR_DECISION")
    ranked = sorted(completed, key=lambda v: (-float(v[1].mean()), v[0]))
    pooled_sse = sum(float(np.sum((v - v.mean())**2)) for _, v in completed)
    dof = len(completed)*(REPEATS - 1)
    if dof <= 0:
        raise MeasurementContractError("INSUFFICIENT_NOISE_DEGREES")
    pooled = max(0.0, pooled_sse/dof)
    stderr = float(np.sqrt(2*pooled/REPEATS))
    margin = float(ranked[0][1].mean() - ranked[1][1].mean())
    if not np.isfinite(margin + stderr) or margin < -1e-10:
        raise MeasurementContractError("INVALID_DECISION_SUMMARY")
    return ranked[0][0], margin, stderr


def _valid_action(idx, ordinal, observed, n):
    return (type(idx) is int and type(ordinal) is int
            and 0 <= idx < n
            and ordinal == len(observed.get(idx, ())) + 1
            and 1 <= ordinal <= REPEATS)


def completion_filter(action, observed, *, step: int, n: int):
    """Policy-neutral feasibility filter; never reads unobserved responses.

    Return (index, ordinal, intervened). We do not claim this is optimal.
    """
    if type(step) is not int or step < 0:
        raise MeasurementContractError("INVALID_COMPLETION_STEP")
    idx, ordinal = action
    if not _valid_action(idx, ordinal, observed, n):
        raise MeasurementContractError("INVALID_ORIGINAL_POLICY_ACTION")
    seen = INITIAL_MEASUREMENTS + step
    if seen != sum(len(v) for v in observed.values()) or seen >= TOTAL_MEASUREMENTS:
        raise MeasurementContractError("INVALID_REMAINING_BUDGET")
    pending = [i for i in observed if len(observed[i]) < REPEATS]
    if len(pending) > MAX_PENDING_GEOMETRIES:
        raise MeasurementContractError("TOO_MANY_INCOMPLETE_DESIGNS")
    remaining = TOTAL_MEASUREMENTS - seen
    owed = sum(REPEATS-len(observed[i]) for i in pending)
    if owed > remaining:
        raise MeasurementContractError("REMAINING_BUDGET_CANNOT_FINISH_PENDING")
    if idx in observed:
        # A complete geometry would already have an invalid next ordinal.
        return idx, ordinal, False
    if (len(pending) < MAX_PENDING_GEOMETRIES and remaining >= owed+REPEATS):
        return idx, ordinal, False
    if not pending:
        raise MeasurementContractError("NO_FEASIBLE_COMPLETION_ACTION")
    fallback = min(pending, key=lambda i: (
        REPEATS-len(observed[i]),
        -float(np.mean(observed[i])),
        i,
    ))
    return fallback, len(observed[fallback])+1, True


def propose_action(policy: str, descriptors, observed, *, seed: int, step: int):
    """Acquired-only selector interface, with no source, latent or oracle input."""
    require_development_seed(seed)
    if policy not in POLICIES:
        raise MeasurementContractError("UNKNOWN_MATCHED_STUDY_POLICY")
    delegate = ("evidence_gate_development" if policy.startswith("evidence_gate_")
                else policy)
    proposal = choose_action(delegate, descriptors, observed, seed=seed, step=step)
    if policy == "evidence_gate_native":
        return proposal[0], proposal[1], False
    return completion_filter(proposal, observed, step=step, n=len(descriptors))


class PrivateManufacturedOracle:
    """Private source and use-once ledger, with final transcript verification."""

    def __init__(self, source: ManufacturedSource, seed: int, order_variant: int):
        require_development_seed(seed)
        if (seed not in SEEDS or type(order_variant) is not int
                or order_variant not in ORDER_VARIANTS):
            raise MeasurementContractError("UNAUTHORIZED_DECISION_SEED_OR_ORDER")
        self.__latent = np.asarray(source.latent, dtype=float).copy()
        self.__outcomes = np.asarray(source.outcomes, dtype=float).copy()
        if (self.__latent.shape != (POOL_SIZE,) or
                self.__outcomes.shape != (POOL_SIZE, REPEATS) or
                not np.isfinite(self.__outcomes).all()):
            raise MeasurementContractError("INVALID_PRIVATE_ORACLE_SOURCE")
        self.__orders = tuple(
            np.random.default_rng(
                np.random.SeedSequence([SOURCE_SEED, seed, order_variant, i])
            ).permutation(REPEATS)
            for i in range(POOL_SIZE)
        )
        self.__ledger = np.zeros(POOL_SIZE, dtype=np.int8)

    def reveal(self, index: int, ordinal: int) -> float:
        if (type(index) is not int or type(ordinal) is not int
                or not 0 <= index < POOL_SIZE or not 1 <= ordinal <= REPEATS):
            raise MeasurementContractError("INVALID_ORACLE_REQUEST")
        if ordinal != int(self.__ledger[index])+1:
            raise MeasurementContractError("ORACLE_REVEAL_ALREADY_USED_OR_SKIPPED")
        v = float(self.__outcomes[index, self.__orders[index][ordinal-1]])
        self.__ledger[index] += 1
        return v

    def evaluate(self, observed):
        if not isinstance(observed, dict):
            raise MeasurementContractError("INVALID_REVEAL_TRANSCRIPT")
        actual_ids = {i for i, count in enumerate(self.__ledger) if count}
        if set(observed) != actual_ids or any(type(i) is not int for i in observed):
            raise MeasurementContractError("REVEAL_TRANSCRIPT_ID_MISMATCH")
        for i, values in observed.items():
            count = int(self.__ledger[i])
            expected = self.__outcomes[i, self.__orders[i][:count]]
            if (not isinstance(values, tuple) or len(values) != count
                    or not np.array_equal(np.asarray(values, float), expected)):
                raise MeasurementContractError("REVEAL_TRANSCRIPT_VALUE_MISMATCH")
        if int(self.__ledger.sum()) != TOTAL_MEASUREMENTS:
            raise MeasurementContractError("REVEAL_BUDGET_MISMATCH")
        chosen, margin, stderr = _observed_summary(observed)
        completed = [i for i in observed if len(observed[i]) == REPEATS]
        partial = [i for i in observed if len(observed[i]) < REPEATS]
        optimum = float(np.max(self.__latent))
        regret = max(0.0, optimum-float(self.__latent[chosen]))
        best_completed = max(0.0, optimum-float(max(self.__latent[completed])))
        best_measured = max(0.0, optimum-float(max(self.__latent[list(observed)])))
        if best_measured > best_completed+1e-10 or best_completed > regret+1e-10:
            raise MeasurementContractError("EVALUATOR_LATENT_ORDER_CONTRACT")
        outcomes = []
        for z in ABSTENTION_Z:
            accept = bool(margin > z*stderr)
            outcomes.append({
                "z": z,
                "accepted": accept,
                "regret_if_accepted": (regret if accept else None),
                "loss_by_penalty": {
                    f"{penalty:.2f}": (regret if accept else penalty)
                    for penalty in ABSTENTION_PENALTIES
                },
            })
        primary = next(x for x in outcomes if x["z"] == PRIMARY_Z)
        return {
            "latent_recommendation_regret": regret,
            "latent_best_completed_regret": best_completed,
            "latent_best_measured_regret": best_measured,
            "completed_designs": len(completed),
            "incomplete_designs": len(partial),
            "stranded_partial_responses": sum(len(observed[i]) for i in partial),
            "total_measured_responses": int(self.__ledger.sum()),
            "accepted_primary": primary["accepted"],
            "primary_loss": primary["loss_by_penalty"][f"{PRIMARY_PENALTY:.2f}"],
            "decision_grid": outcomes,
            "latent_outcomes_passed_to_selector": False,
            "future_responses_passed_to_selector": False,
        }


def run_campaign(source: ManufacturedSource, policy: str, seed: int, order_variant: int):
    if policy not in POLICIES or type(seed) is not int or seed not in SEEDS:
        raise MeasurementContractError("UNAUTHORIZED_CAMPAIGN_POLICY_OR_SEED")
    oracle = PrivateManufacturedOracle(source, seed, order_variant)
    x = source.descriptors.copy()
    observed: dict[int, tuple[float, ...]] = {}
    for i in initial_geometry_ids(POOL_SIZE, seed):
        observed[i] = tuple(oracle.reveal(i, j) for j in range(1, REPEATS+1))
    overrides = 0
    for step in range(TOTAL_MEASUREMENTS-INITIAL_MEASUREMENTS):
        acquired_only = {i: tuple(v) for i, v in observed.items()}
        idx, ordinal, overridden = propose_action(
            policy, x.copy(), acquired_only, seed=seed, step=step)
        if not _valid_action(idx, ordinal, observed, len(x)):
            raise MeasurementContractError("INVALID_MEASUREMENT_ACTION")
        overrides += int(overridden)
        observed[idx] = observed.get(idx, ())+(oracle.reveal(idx, ordinal),)
    result = oracle.evaluate(observed)
    return {
        "landscape": source.landscape, "regime": source.regime,
        "seed": seed, "order_variant": order_variant, "policy": policy,
        "completion_interventions": overrides, **result,
    }


def _aggregate(rows, policy):
    chosen = [x for x in rows if x["policy"] == policy]
    if len(chosen) != len(LANDSCAPES)*len(REGIMES)*len(SEEDS)*len(ORDER_VARIANTS):
        raise MeasurementContractError("UNEXPECTED_AGGREGATE_CAMPAIGN_COUNT")
    return {
        "campaign_count": len(chosen),
        "mean_primary_loss": float(np.mean([x["primary_loss"] for x in chosen])),
        "primary_coverage": float(np.mean([x["accepted_primary"] for x in chosen])),
        "conditional_primary_regret": (
            float(np.mean([x["latent_recommendation_regret"] for x in chosen
                           if x["accepted_primary"]]))
            if any(x["accepted_primary"] for x in chosen) else None),
        "mean_latent_recommendation_regret": float(np.mean([
            x["latent_recommendation_regret"] for x in chosen])),
        "mean_completed_designs": float(np.mean([x["completed_designs"] for x in chosen])),
        "mean_incomplete_designs": float(np.mean([x["incomplete_designs"] for x in chosen])),
        "mean_stranded_partial_responses": float(np.mean([
            x["stranded_partial_responses"] for x in chosen])),
        "mean_completion_interventions": float(np.mean([
            x["completion_interventions"] for x in chosen])),
        "coverage_loss_grid": [
            {
                "z": z, "penalty": cost,
                "coverage": float(np.mean([
                    next(v["accepted"] for v in row["decision_grid"] if v["z"] == z)
                    for row in chosen])),
                "mean_loss": float(np.mean([
                    next(v["loss_by_penalty"][f"{cost:.2f}"] for v in row["decision_grid"]
                         if v["z"] == z) for row in chosen])),
            }
            for z in ABSTENTION_Z for cost in ABSTENTION_PENALTIES
        ],
    }


def run_frozen_study():
    rows = []
    digest = {}
    for landscape in LANDSCAPES:
        for regime in REGIMES:
            source = make_source(landscape, regime)
            digest[f"{landscape}:{regime}"] = source.digest
            for seed in SEEDS:
                for order in ORDER_VARIANTS:
                    for policy in POLICIES:
                        rows.append(run_campaign(source, policy, seed, order))
    expected = (len(LANDSCAPES)*len(REGIMES)*len(SEEDS)*len(ORDER_VARIANTS)*len(POLICIES))
    if len(rows) != expected or any(x["total_measured_responses"] != TOTAL_MEASUREMENTS for x in rows):
        raise MeasurementContractError("STUDY_MISSING_OR_BUDGET_INCONSISTENT")
    summary = {p: _aggregate(rows, p) for p in POLICIES}
    return {
        "study": "BHS v12.4 fixed-response completion and abstention development audit",
        "frozen_protocol": "research/BHS_V124_MATCHED_COMPLETION_PROTOCOL.md",
        "synthetic_source_digests": digest,
        "landscapes": list(LANDSCAPES), "regimes": list(REGIMES),
        "decision_seeds": list(SEEDS), "response_order_variants": list(ORDER_VARIANTS),
        "policies": list(POLICIES), "primary_abstention_z": PRIMARY_Z,
        "primary_abstention_penalty": PRIMARY_PENALTY,
        "measurement_budget": TOTAL_MEASUREMENTS,
        "physical_experiments_performed": False,
        "historical_source_accessed": False,
        "campaigns": rows, "aggregates": summary,
        "hard_gates": dict(HARD_GATES),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true",
                        help="Run the fixed manufactured development comparison only.")
    parser.add_argument("--out", default="runs/bhs_v124_completion_coverage.json")
    args = parser.parse_args(argv)
    if not args.execute:
        print("V12.4 protocol and software contracts; no outcome evaluation performed.")
        return 0
    result = run_frozen_study()
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print("Manufactured development campaigns:", len(result["campaigns"]))
    print("Output:", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
