"""BHS v12 draft: source-locked, measurement-level retrospective replay.

The real observations were collected by the cited source researchers.
One action reveals exactly one historical response, never a full triplicate.
This is a DEVELOPMENT-ONLY simulator, not laboratory validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Mapping

import numpy as np
from scipy.stats import norm
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern

SEEDS = (7, 13, 23, 31, 43)  # explored development seeds, NOT a fresh holdout
POLICIES = ("random_bundled", "gp_ard_bundled", "rf_ucb_bundled", "evidence_gate_development")
INITIAL_GEOMETRIES = 6
REPEATS = 3
INITIAL_MEASUREMENTS = INITIAL_GEOMETRIES * REPEATS
TOTAL_MEASUREMENTS = 48
MAX_PENDING_GEOMETRIES = 3  # conservative guard against unlimited unfinished screening
SOURCE_SHA256 = "2c01f875f3c210e986ca6142bf20f417884c2ad7d6f008c2fc574b44a3d5f606"
FORBIDDEN_SEEDS = range(10000, 10100)


class MeasurementContractError(ValueError):
    """Failed data visibility, protocol, or measurement-budget contract."""


def require_development_seed(seed: int) -> None:
    if (type(seed) is not int or seed < 0 or seed in FORBIDDEN_SEEDS):
        raise MeasurementContractError("DEVELOPMENT_SEED_REQUIRED; RESERVED_SEEDS_PROHIBITED")


def initial_geometry_ids(n: int, seed: int) -> tuple[int, ...]:
    require_development_seed(seed)
    if n < INITIAL_GEOMETRIES + 1:
        raise MeasurementContractError("INSUFFICIENT_GEOMETRY_POOL")
    return tuple(map(int, np.random.default_rng(seed).choice(n, INITIAL_GEOMETRIES, replace=False)))


def acquisition_view(candidate_features, observed: Mapping[int, tuple[float, ...]]):
    """Validate public descriptors and revealed-only measurements; no oracle argument."""
    features = np.asarray(candidate_features, dtype=float)
    if (features.ndim != 2 or features.shape[1] != 4 or
            features.shape[0] < INITIAL_GEOMETRIES + 1 or
            not np.isfinite(features).all()):
        raise MeasurementContractError("INVALID_PUBLIC_FEATURES")
    if not isinstance(observed, Mapping) or len(observed) < INITIAL_GEOMETRIES:
        raise MeasurementContractError("INVALID_OBSERVED_MAP")
    clean: dict[int, tuple[float, ...]] = {}
    for idx, values in observed.items():
        if type(idx) is not int or not (0 <= idx < len(features)) or idx in clean:
            raise MeasurementContractError("INVALID_OBSERVED_ID")
        if not isinstance(values, (tuple, list)) or not (1 <= len(values) <= REPEATS):
            raise MeasurementContractError("INVALID_OBSERVED_REPLICATE_COUNT")
        arr = np.asarray(values, dtype=float)
        if arr.shape != (len(values),) or not np.isfinite(arr).all():
            raise MeasurementContractError("NONFINITE_REVEALED_OUTCOME")
        clean[idx] = tuple(map(float, arr))
    full = [i for i, vals in clean.items() if len(vals) == REPEATS]
    if len(full) < INITIAL_GEOMETRIES:
        raise MeasurementContractError("INITIAL_FULLY_MEASURED_GEOMETRIES_REQUIRED")
    return features, clean, full


def _standardized_means(values: np.ndarray):
    means = values.mean(axis=1)
    center = float(np.mean(means))
    scale = max(float(np.std(means)), 1e-8)
    return means, (means - center) / scale, scale


def _expected_improvement(mu, sd, incumbent):
    mu, sd = np.asarray(mu, float), np.asarray(sd, float)
    delta = mu - incumbent - 0.01
    z = delta / np.maximum(sd, 1e-12)
    return np.where(sd > 1e-12,
                    np.maximum(delta * norm.cdf(z) + sd * norm.pdf(z), 0.0),
                    np.maximum(delta, 0.0))


def _new_geometry_scores(policy: str, X: np.ndarray,
                         full_ids: list[int], observed: Mapping[int, tuple[float, ...]],
                         available: np.ndarray, seed: int):
    """Acquired FULL triplicates only; observed PARTIAL values are not fit by GP/RF."""
    values = np.asarray([observed[i] for i in full_ids], float)
    means, standardized, scale = _standardized_means(values)
    if policy in ("gp_ard_bundled", "evidence_gate_development"):
        noise_diagonal = np.clip(
            np.var(values, axis=1, ddof=1) / (REPEATS * scale * scale), 1e-3, 1.0
        )
        kernel = ConstantKernel(1.0, (0.1, 10.0)) * Matern(
            length_scale=np.ones(4), length_scale_bounds=(0.1, 10.0), nu=2.5
        )
        model = GaussianProcessRegressor(
            kernel=kernel, alpha=noise_diagonal, optimizer="fmin_l_bfgs_b",
            n_restarts_optimizer=0, normalize_y=False, random_state=0
        )
        model.fit(X[full_ids], standardized)
        mu, sd = model.predict(X[available], return_std=True)
        return _expected_improvement(mu, sd, float(standardized.max()))
    if policy == "rf_ucb_bundled":
        model = RandomForestRegressor(
            n_estimators=160, min_samples_leaf=2, max_features=1.0,
            bootstrap=True, n_jobs=1, random_state=seed
        )
        model.fit(X[full_ids], standardized)
        votes = np.stack([tree.predict(X[available]) for tree in model.estimators_])
        return votes.mean(axis=0) + votes.std(axis=0)  # heuristic, NOT a calibrated bound
    raise MeasurementContractError("UNSUPPORTED_MODEL")


def select_measurement(policy: str, candidate_features, observed: Mapping[int, tuple[float, ...]],
                       *, seed: int, step: int) -> tuple[int, int]:
    """Return (geometry ID, next measurement ordinal); no unrevealed labels in API."""
    require_development_seed(seed)
    if policy not in POLICIES or type(step) is not int or step < 0:
        raise MeasurementContractError("INVALID_POLICY_OR_STEP")
    X, seen, full = acquisition_view(candidate_features, observed)
    initial = initial_geometry_ids(len(X), seed)
    if any(i not in seen or len(seen[i]) != REPEATS for i in initial):
        raise MeasurementContractError("FROZEN_SHARED_INITIAL_DESIGNS_NOT_PRESENT")
    if INITIAL_MEASUREMENTS + step != sum(map(len, seen.values())):
        raise MeasurementContractError("MEASUREMENT_STEP_AND_OBSERVATIONS_MISMATCH")
    if INITIAL_MEASUREMENTS + step >= TOTAL_MEASUREMENTS:
        raise MeasurementContractError("BUDGET_EXHAUSTED")
    partial = [i for i, vals in seen.items() if len(vals) < REPEATS]
    new = np.asarray([i for i in range(len(X)) if i not in seen], dtype=int)
    bundled = policy.endswith("_bundled")
    if bundled and len(partial) > 1:
        raise MeasurementContractError("BUNDLED_POLICY_HAS_MULTIPLE_PARTIALS")
    if bundled and partial:
        index = partial[0]
    else:
        index = None
        if policy == "evidence_gate_development" and partial:
            best_complete = max(float(np.mean(seen[i])) for i in full)
            sample_sd = np.asarray([np.std(seen[i], ddof=1) for i in full], float)
            # Descriptive historical spread, NOT a physical noise calibration.
            noise_scale = float(np.sqrt(np.mean(np.square(sample_sd))))
            # Fixed exploratory rule; not an expected-utility or calibrated-risk estimate.
            eligible = [i for i in partial if float(np.mean(seen[i])) + noise_scale >= best_complete]
            # Do not allow unlimited one-off screens to consume the budget.
            # At the cap, complete the most promising pending candidate even
            # when the uncalibrated descriptive screening threshold is unmet.
            remaining_actions = TOTAL_MEASUREMENTS - (INITIAL_MEASUREMENTS + step)
            if remaining_actions == 1:
                finishable = [i for i in partial if len(seen[i]) == REPEATS - 1]
                if finishable:
                    index = min(finishable, key=lambda i: (-float(np.mean(seen[i])), i))
            if index is None and (eligible or len(partial) >= MAX_PENDING_GEOMETRIES):
                pool = eligible if eligible else partial
                index = min(pool, key=lambda i: (-float(np.mean(seen[i])), i))
        if index is None:
            if not len(new):
                if not partial:
                    raise MeasurementContractError("NO_REMAINING_MEASUREMENT_ACTIONS")
                index = min(partial, key=lambda i: (-float(np.mean(seen[i])), i))
            elif policy == "random_bundled":
                batch_number = step // REPEATS
                index = int(np.random.default_rng(seed + 1009 * (batch_number + 1)).choice(new))
            else:
                # The gate explores using only fully observed groups. Partial values
                # affect repeat selection but are not silently treated as full triples.
                batch_number = step // REPEATS
                scores = _new_geometry_scores(policy, X, full, seen, new,
                                             seed + 1009 * batch_number)
                if scores.shape != new.shape or not np.isfinite(scores).all():
                    raise MeasurementContractError("INVALID_ACQUISITION_SCORES")
                index = int(new[int(np.argmax(scores))])
    ordinal = len(seen.get(index, ())) + 1
    if not 1 <= ordinal <= REPEATS:
        raise MeasurementContractError("DUPLICATE_OR_EXCESS_REPLICATE")
    return index, ordinal


class HistoricalMeasurementOracle:
    """Holds all historical outcomes ONLY on the evaluator side."""

    def __init__(self, triplicates, seed: int):
        require_development_seed(seed)
        hidden = np.asarray(triplicates, float)
        if hidden.ndim != 2 or hidden.shape[1] != REPEATS or not np.isfinite(hidden).all():
            raise MeasurementContractError("INVALID_PRIVATE_HISTORICAL_ORACLE")
        self.__hidden = hidden.copy()
        self.__permutation = [
            np.random.default_rng(np.random.SeedSequence([seed, i])).permutation(REPEATS)
            for i in range(len(hidden))
        ]
        # Only the evaluator owns the use-once measurement ledger. Re-requests
        # and skipped ordinals fail rather than revealing another source value.
        self.__revealed_counts = np.zeros(len(hidden), dtype=np.int8)

    def reveal_one(self, idx: int, ordinal: int) -> float:
        if (type(idx) is not int or type(ordinal) is not int or
                not (0 <= idx < len(self.__hidden)) or not (1 <= ordinal <= REPEATS)):
            raise MeasurementContractError("INVALID_ONE_MEASUREMENT_REQUEST")
        expected = int(self.__revealed_counts[idx]) + 1
        if ordinal != expected:
            raise MeasurementContractError("MEASUREMENT_ALREADY_REVEALED_OR_OUT_OF_ORDER")
        response = float(self.__hidden[idx, self.__permutation[idx][ordinal - 1]])
        self.__revealed_counts[idx] += 1
        return response

    def evaluate_complete_only(self, observed: Mapping[int, tuple[float, ...]]):
        # Verify the public acquisition transcript against the private ledger
        # before computing any retrospective statistic. Evaluator-only check;
        # the acquisition policy never receives the source array or ledger.
        if not isinstance(observed, Mapping):
            raise MeasurementContractError("INVALID_EVALUATION_TRANSCRIPT")
        actual_ids = {i for i in range(len(self.__hidden)) if self.__revealed_counts[i]}
        if (set(observed) != actual_ids or
                any(type(i) is not int for i in observed)):
            raise MeasurementContractError("EVALUATION_TRANSCRIPT_IDS_MISMATCH")
        for idx, values in observed.items():
            count = int(self.__revealed_counts[idx])
            if not isinstance(values, (tuple, list)) or len(values) != count:
                raise MeasurementContractError("EVALUATION_TRANSCRIPT_COUNT_MISMATCH")
            recorded = np.asarray(values, dtype=float)
            expected = self.__hidden[idx, self.__permutation[idx][:count]]
            if recorded.shape != expected.shape or not np.array_equal(recorded, expected):
                raise MeasurementContractError("EVALUATION_TRANSCRIPT_VALUES_MISMATCH")
        completed = [idx for idx, values in observed.items() if len(values) == REPEATS]
        if not completed:
            return {"abstained_no_complete_design": True, "regret_j": None}
        finite_pool_means = self.__hidden.mean(axis=1)
        best_empirical = float(finite_pool_means.max())
        recommended_id = max(completed, key=lambda i: (float(np.mean(observed[i])), -i))
        recommended_empirical = float(finite_pool_means[recommended_id])
        return {
            "abstained_no_complete_design": False,
            "regret_j": max(0.0, best_empirical - recommended_empirical),
            "recommended_historical_triplicate_range_j": float(np.ptp(self.__hidden[recommended_id])),
            "recommended_uses_all_three_observations": True,
        }


def run_campaign(features, hidden_triplicates, policy: str, seed: int,
                 *, budget: int = TOTAL_MEASUREMENTS):
    require_development_seed(seed)
    if (policy not in POLICIES or type(budget) is not int or
            budget < INITIAL_MEASUREMENTS or budget > TOTAL_MEASUREMENTS):
        raise MeasurementContractError("INVALID_POLICY_OR_MEASUREMENT_BUDGET")
    X = np.asarray(features, float)
    if X.ndim != 2 or X.shape[1] != 4 or not np.isfinite(X).all():
        raise MeasurementContractError("INVALID_PUBLIC_FEATURES")
    oracle = HistoricalMeasurementOracle(hidden_triplicates, seed)
    if np.asarray(hidden_triplicates).shape[0] != len(X):
        raise MeasurementContractError("ORACLE_POOL_SIZE_MISMATCH")
    acquired: dict[int, tuple[float, ...]] = {}
    for i in initial_geometry_ids(len(X), seed):
        acquired[i] = tuple(oracle.reveal_one(i, j) for j in range(1, REPEATS + 1))
    for step in range(budget - INITIAL_MEASUREMENTS):
        policy_view = {i: tuple(values) for i, values in acquired.items()}
        chosen, ordinal = select_measurement(policy, X.copy(), policy_view, seed=seed, step=step)
        if ordinal != len(acquired.get(chosen, ())) + 1:
            raise MeasurementContractError("ACTION_ORDINAL_INCONSISTENT")
        acquired[chosen] = acquired.get(chosen, ()) + (oracle.reveal_one(chosen, ordinal),)
    if sum(len(v) for v in acquired.values()) != budget:
        raise MeasurementContractError("MEASUREMENT_BUDGET_NOT_EXACT")
    evaluation = oracle.evaluate_complete_only(acquired)
    return {
        "seed": seed,
        "policy": policy,
        "historical_measurements_revealed": budget,
        "distinct_geometries_seen": len(acquired),
        "completely_measured_geometries": sum(len(v) == REPEATS for v in acquired.values()),
        "partially_measured_geometries": sum(len(v) < REPEATS for v in acquired.values()),
        "partially_measured_response_count": sum(len(v) for v in acquired.values() if len(v) < REPEATS),
        "all_unrevealed_measurements_hidden_from_policy": True,
        "recommendation_complete_triplicates_only": True,
        **evaluation,
    }


def run_development(features, hidden_triplicates, *, seeds=SEEDS, policies=POLICIES):
    if tuple(seeds) != SEEDS or tuple(policies) != POLICIES:
        raise MeasurementContractError("UNAUTHORIZED_CHANGE_TO_FROZEN_DEVELOPMENT_PROTOCOL")
    X, hidden = np.asarray(features, float), np.asarray(hidden_triplicates, float)
    if X.shape != (600, 4) or hidden.shape != (600, REPEATS):
        raise MeasurementContractError("SOURCE_STRUCTURE_CHANGED")
    rows = [run_campaign(X, hidden, policy, int(seed)) for seed in seeds for policy in policies]
    aggregates = {}
    for policy in POLICIES:
        sample = [r for r in rows if r["policy"] == policy]
        aggregates[policy] = {
            "campaign_count": len(sample),
            "mean_empirical_simple_regret_j": float(np.mean([r["regret_j"] for r in sample])),
            "mean_complete_geometries": float(np.mean([r["completely_measured_geometries"] for r in sample])),
            "mean_partial_geometries": float(np.mean([r["partially_measured_geometries"] for r in sample])),
            "mean_recommended_recorded_triplicate_range_j": float(np.mean([
                r["recommended_historical_triplicate_range_j"] for r in sample])),
        }
    return rows, aggregates


def build_report(raw_source: bytes):
    if hashlib.sha256(raw_source).hexdigest() != SOURCE_SHA256:
        raise MeasurementContractError("PINNED_SOURCE_SHA256_MISMATCH")
    # Import source-locked validated loaders only after the immutable checksum passes.
    from scripts.bhs_replicate_leakage_v10 import parse_source
    from scripts.bhs_replicate_pool_v11 import group_source
    X, y, group = parse_source(raw_source)
    features, triples = group_source(X, y, group)
    rows, aggregates = run_development(features, triples)
    return {
        "study": "BHS v12 retrospective one-measurement action allocation; exploratory only",
        "source": {
            "repository": "PV-Lab/Benchmarking",
            "original_experimental_doi": "10.1126/sciadv.aaz1708",
            "benchmark_doi": "10.1038/s41524-021-00656-9",
            "source_sha256": SOURCE_SHA256,
            "raw_source_redistributed": False,
            "new_experiments_by_bhs": False,
        },
        "protocol": {
            "development_seeds": list(SEEDS),
            "policies": list(POLICIES),
            "initial_complete_geometries": INITIAL_GEOMETRIES,
            "initial_measurements": INITIAL_MEASUREMENTS,
            "total_measurement_actions": TOTAL_MEASUREMENTS,
            "max_pending_geometries_for_evidence_gate": MAX_PENDING_GEOMETRIES,
            "one_action_one_historical_response": True,
            "within_geometry_order_artificially_permuted_from_seed": True,
            "unobserved_responses_isolated": True,
            "baseline_reuses_full_triplicates": True,
            "pool_features_derived_from_unlabelled_source_only": True,
        },
        "campaigns": rows,
        "aggregates": aggregates,
        "hard_gates": {
            "development_only": True,
            "scored_validation_allowed": False,
            "independent_holdout_used": False,
            "physical_validation_by_bhs": False,
            "causal_identification": False,
            "calibrated_uncertainty_proven": False,
            "claim_of_superiority": False,
            "real_savings_measured": False,
            "reserved_nist_seeds_used": False,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Fetch pinned original data and run development")
    parser.add_argument("--out", default="runs/bhs_measurement_allocation_v12.json")
    args = parser.parse_args(argv)
    if not args.execute:
        print("Protocol and synthetic contracts only. Historical source not accessed.")
        return 0
    from scripts.bhs_replicate_leakage_v10 import fetch_pinned_source
    report = build_report(fetch_pinned_source())
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "DEVELOPMENT_ONLY", "aggregates": report["aggregates"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
