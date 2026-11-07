"""BHS v11: label-isolated sequential selection on actual historical triplicates.

Only the evaluator holds unrevealed raw responses. The selector receives public
candidate descriptors, selected IDs and their 3 revealed historical values.
Actual physical experiments were performed by the original source authors.
This is retrospective DEVELOPMENT ONLY, not independent validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import norm
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern

from scripts.bhs_replicate_leakage_v10 import (
    fetch_pinned_source, parse_source, require_development_seeds,
    SOURCE_BLOB_SHA1, SOURCE_COMMIT
)
from scripts.uci_concrete_v5 import choose_next as existing_bhs_v5_selector, scale_candidates

INITIAL = 6
ADDITIONAL = 10
SEEDS = (7, 13, 23, 31, 43)
POLICIES = ("random", "gp_ard_ei", "rf_ucb", "bhs_v5_kernel_portfolio_ei")
REPLICATES = 3
RF_TREES = 160


class SelectionContractError(ValueError):
    """Unobserved label visibility or acquisition-budget contract violated."""


def group_source(X, y, group):
    """Only the evaluator converts all recorded responses into an oracle table."""
    descriptors = np.unique(X, axis=0)
    if X.shape != (1800, 4) or len(descriptors) != 600:
        raise SelectionContractError("SOURCE_GROUP_STRUCTURE_CHANGED")
    triples = np.empty((600, REPLICATES), dtype=float)
    if np.any(np.bincount(group) != REPLICATES):
        raise SelectionContractError("SOURCE_REPLICATES_NOT_TRIPLETS")
    for g in range(600):
        measured = np.asarray(y[group == g], dtype=float)
        if measured.shape != (REPLICATES,):
            raise SelectionContractError("MISSING_REPLICATE")
        triples[g] = measured
    if not np.isfinite(triples).all():
        raise SelectionContractError("NONFINITE_SOURCE_MEASUREMENT")
    return scale_candidates(descriptors), triples


def check_acquisition_view(X, selected, revealed):
    """The policy view has NO unrevealed outcomes, oracle, or known optimum."""
    candidates = np.asarray(X, dtype=float)
    chosen = np.asarray(selected)
    responses = np.asarray(revealed, dtype=float)
    if (candidates.ndim != 2 or candidates.shape[1] != 4
            or len(candidates) < INITIAL + ADDITIONAL
            or not np.isfinite(candidates).all()):
        raise SelectionContractError("INVALID_PUBLIC_CANDIDATE_FEATURES")
    if (chosen.ndim != 1 or chosen.dtype.kind not in "iu"
            or chosen.size < INITIAL or len(set(map(int, chosen))) != chosen.size
            or np.any(chosen < 0) or np.any(chosen >= len(candidates))):
        raise SelectionContractError("INVALID_ACQUIRED_DESIGN_IDS")
    if (responses.shape != (chosen.size, REPLICATES)
            or not np.isfinite(responses).all()):
        raise SelectionContractError("REVEALED_LABELS_MUST_BE_THREE_PER_ACQUIRED_GEOMETRY")
    return candidates, chosen.astype(int), responses


def _ei(mean, sigma, incumbent):
    """Gaussian expected improvement for maximization (fixed xi=0.01)."""
    sigma = np.asarray(sigma, dtype=float)
    mean = np.asarray(mean, dtype=float)
    delta = mean - incumbent - 0.01
    z = delta / np.maximum(sigma, 1e-12)
    return np.where(
        sigma > 1e-12,
        np.maximum(delta * norm.cdf(z) + sigma * norm.pdf(z), 0.0),
        np.maximum(delta, 0.0)
    )


def _standardized_observations(revealed):
    means = np.mean(revealed, axis=1)
    location = float(np.mean(means))
    scale = max(float(np.std(means)), 1e-8)
    standardized = (means - location) / scale
    if not np.isfinite(standardized).all():
        raise SelectionContractError("INVALID_OBSERVED_MEAN_STANDARDIZATION")
    return means, standardized, scale


def _gp_ard_expected_improvement(X, selected, revealed, available):
    means, standardized, scale = _standardized_observations(revealed)
    # Sample variance of selected triplicates / 3, in standardized mean units.
    # An exploratory diagonal noise PLUG-IN; NOT calibrated physical uncertainty.
    empirical_alpha = np.var(revealed, axis=1, ddof=1) / (REPLICATES * scale * scale)
    alpha = np.clip(empirical_alpha, 1e-3, 1.0)
    kernel = ConstantKernel(1.0, constant_value_bounds=(0.1, 10.0)) * Matern(
        length_scale=np.ones(X.shape[1]), length_scale_bounds=(0.1, 10.0), nu=2.5
    )
    model = GaussianProcessRegressor(
        kernel=kernel, alpha=alpha, optimizer="fmin_l_bfgs_b",
        n_restarts_optimizer=0, normalize_y=False, random_state=0
    )
    model.fit(X[selected], standardized)
    mu, sd = model.predict(X[available], return_std=True)
    return _ei(mu, sd, float(np.max(standardized)))


def _rf_ucb(X, selected, revealed, available, seed):
    _, standardized, _ = _standardized_observations(revealed)
    model = RandomForestRegressor(
        n_estimators=RF_TREES,
        min_samples_leaf=2,
        max_features=1.0,
        bootstrap=True,
        n_jobs=1,
        random_state=int(seed),
    )
    model.fit(X[selected], standardized)
    predictions = np.stack(
        [tree.predict(X[available]) for tree in model.estimators_], axis=0
    )
    # Tree-ensemble spread is a selection HEURISTIC, not calibrated uncertainty.
    return np.mean(predictions, axis=0) + np.std(predictions, axis=0)


def select_next(policy, candidate_features, acquired_ids, acquired_triplicates, *, seed, step):
    """Only this bounded view is passed to the four competing policies.

    The method has no access to full historical labels, remaining triplicates,
    source-specific global optimum, or the retrospective evaluator.
    """
    if policy not in POLICIES:
        raise SelectionContractError("UNKNOWN_POLICY")
    if (type(seed) is not int or type(step) is not int or step < 0):
        raise SelectionContractError("INVALID_DEVELOPMENT_SEED_OR_STEP")
    require_development_seeds((seed,))
    X, chosen, revealed = check_acquisition_view(
        candidate_features, acquired_ids, acquired_triplicates)
    available = np.setdiff1d(np.arange(len(X)), chosen, assume_unique=True)
    if not len(available):
        raise SelectionContractError("NO_UNOBSERVED_DESIGNS")
    rng = np.random.default_rng(seed + 1009 * (step + 1))
    if policy == "random":
        next_id = int(rng.choice(available))
    elif policy == "bhs_v5_kernel_portfolio_ei":
        # The prior fixed v5 statistical kernel portfolio is reused without
        # changing its models, weighting, EI or selected-observation interface.
        acquired_means = np.mean(revealed, axis=1)
        next_id = int(existing_bhs_v5_selector(
            X, chosen.tolist(), acquired_means, "kernel_portfolio_ei", rng
        ))
    else:
        if policy == "gp_ard_ei":
            scores = _gp_ard_expected_improvement(X, chosen, revealed, available)
        elif policy == "rf_ucb":
            scores = _rf_ucb(X, chosen, revealed, available, seed + 1009 * step)
        else:
            raise AssertionError("Unexpected policy")
        if (scores.shape != (len(available),) or
                not np.isfinite(scores).all()):
            raise SelectionContractError("NONFINITE_POLICY_ACQUISITION")
        # Deterministic tie-break by canonical geometry ID.
        next_id = int(available[int(np.argmax(scores))])
    if next_id not in available:
        raise SelectionContractError("RESELECTED_OR_UNAVAILABLE_GEOMETRY")
    return next_id


def initial_geometries(pool_size, seed):
    require_development_seeds((seed,))
    if pool_size < INITIAL + ADDITIONAL:
        raise SelectionContractError("POOL_SMALLER_THAN_PREDECLARED_BUDGET")
    return tuple(
        int(i) for i in np.random.default_rng(seed).choice(
            pool_size, size=INITIAL, replace=False)
    )


def run_campaign(candidate_features, oracle_triplicates, policy, seed,
                 *, acquisitions=ADDITIONAL):
    """Evaluator privately holds historical labels and reveals only chosen triples."""
    require_development_seeds((seed,))
    if policy not in POLICIES or type(acquisitions) is not int or acquisitions < 0 or acquisitions > ADDITIONAL:
        raise SelectionContractError("UNEXPECTED_POLICY_OR_BUDGET")
    X = np.asarray(candidate_features, dtype=float)
    hidden = np.asarray(oracle_triplicates, dtype=float)
    if hidden.shape != (len(X), REPLICATES) or not np.isfinite(hidden).all():
        raise SelectionContractError("INVALID_PRIVATE_ORACLE")
    if len(X) < INITIAL + ADDITIONAL:
        raise SelectionContractError("SOURCE_CANDIDATE_POOL_TOO_SMALL")
    selected = list(initial_geometries(len(X), seed))
    for step in range(acquisitions):
        # The public policy receives copies of selected triplicates ONLY.
        acquired = hidden[selected].copy()
        candidate = select_next(policy, X, selected, acquired, seed=seed, step=step)
        if candidate in selected:
            raise AssertionError("Duplicate physical design acquisition")
        selected.append(candidate)
    # PRIVATE EVALUATOR ONLY. None of these full-data statistics enter select_next.
    historical_mean = np.mean(hidden, axis=1)
    optimum = float(np.max(historical_mean))
    best_acquired = float(np.max(historical_mean[selected]))
    regret = max(0.0, optimum - best_acquired)
    denom = float(np.ptp(historical_mean))
    threshold = float(np.quantile(historical_mean, 0.90))
    return {
        "seed": int(seed),
        "policy": policy,
        "initial_geometries": INITIAL,
        "additional_geometries": int(acquisitions),
        "total_distinct_designs_acquired": len(selected),
        "historical_measured_rows_revealed": len(selected) * REPLICATES,
        "triplicate_group_integrity": len(selected) == len(set(selected)),
        "final_empirical_best_mean_toughness_j": best_acquired,
        "final_simple_regret_against_noisy_pool_best_j": float(regret),
        "normalized_final_simple_regret": (regret / denom if denom else 0.0),
        "any_acquired_geometry_in_noisy_pool_top_decile": bool(best_acquired >= threshold),
        "global_optimum_used_by_policy": False,
        "unobserved_replicates_used_by_policy": False,
    }


def run_development(features, hidden_triplicates, seeds=SEEDS):
    require_development_seeds(seeds)
    if tuple(seeds) != SEEDS:
        raise SelectionContractError("ONLY_FROZEN_FIVE_SEED_PROTOCOL_CAN_BE_REPORTED")
    X = np.asarray(features, dtype=float)
    hidden = np.asarray(hidden_triplicates, dtype=float)
    if X.shape != (600, 4) or hidden.shape != (600, REPLICATES):
        raise SelectionContractError("SOURCE_SHAPE_CHANGED")
    rows = [
        run_campaign(X, hidden, policy, int(seed))
        for seed in seeds for policy in POLICIES
    ]
    summary = {}
    for policy in POLICIES:
        subset = [r for r in rows if r["policy"] == policy]
        summary[policy] = {
            "development_campaigns": len(subset),
            "mean_final_simple_regret_j": float(np.mean(
                [r["final_simple_regret_against_noisy_pool_best_j"] for r in subset])),
            "mean_normalized_final_simple_regret": float(np.mean(
                [r["normalized_final_simple_regret"] for r in subset])),
            "mean_empirical_best_toughness_j": float(np.mean(
                [r["final_empirical_best_mean_toughness_j"] for r in subset])),
            "fraction_with_any_noisy_top_decile_design": float(np.mean(
                [r["any_acquired_geometry_in_noisy_pool_top_decile"] for r in subset])),
            "total_historical_physical_measurement_rows_exposed": int(sum(
                r["historical_measured_rows_revealed"] for r in subset)),
        }
    paired_against_gp = {
        policy: [
            float(next(r["final_simple_regret_against_noisy_pool_best_j"]
                       for r in rows if r["seed"] == seed and r["policy"] == policy)
                  - next(r["final_simple_regret_against_noisy_pool_best_j"]
                         for r in rows if r["seed"] == seed and r["policy"] == "gp_ard_ei"))
            for seed in seeds
        ]
        for policy in POLICIES if policy != "gp_ard_ei"
    }
    return rows, summary, paired_against_gp


def build_report(raw):
    X, y, group = parse_source(raw)
    features, hidden_triplicates = group_source(X, y, group)
    results, summary, paired = run_development(features, hidden_triplicates)
    return {
        "study": "BHS v11 replicate-aware retrospective sequential geometry search",
        "source": {
            "repository": "PV-Lab/Benchmarking",
            "pin_commit": SOURCE_COMMIT,
            "source_blob_sha1": SOURCE_BLOB_SHA1,
            "raw_source_sha256": hashlib.sha256(raw).hexdigest(),
            "benchmark_doi": "10.1038/s41524-021-00656-9",
            "original_experimental_doi": "10.1126/sciadv.aaz1708",
            "raw_measurements_redistributed": False,
            "original_lab_collected_measurements": True,
            "bhs_conducted_new_physical_experiments": False,
        },
        "frozen_protocol": {
            "seeds": list(SEEDS),
            "policies": list(POLICIES),
            "initial_unique_geometries": INITIAL,
            "additional_geometry_acquisitions": ADDITIONAL,
            "per_geometry_historical_replicates": REPLICATES,
            "historical_measurements_revealed_per_campaign": (INITIAL+ADDITIONAL)*REPLICATES,
            "descriptors_known_for_all_pool_before_selection": True,
            "pool_standardization_from_unlabelled_features_only": True,
            "acquired_means_only_for_v5_kernel_portfolio": True,
            "gp_ard_uses_acquired_replicate_mean_variance_plugin": True,
            "rf_uncertainty_is_heuristic": True,
            "policy_action_interface_excludes_all_hidden_labels": True,
            "global_optimum_evaluator_only": True,
            "empirical_noisy_pool_best_not_latent_physical_truth": True,
            "source_outcome_availability_defines_historical_pool": True,
        },
        "outcomes_by_development_seed": results,
        "aggregates": summary,
        "paired_simple_regret_j_minus_gp_ard": paired,
        "decision": {
            "status": "EXPLORATORY_REPLICATE_AWARE_SELECTION_COMPARISON_ONLY",
            "algorithmic_superiority_proven": False,
            "scientific_hypotheses_physically_discriminated": False,
            "independent_experiment_required": True,
            "automatic_laboratory_action_authorized": False,
        },
        "hard_gates": {
            "development_only": True,
            "scored_validation_allowed": False,
            "independent_holdout_used": False,
            "physical_validation_by_bhs": False,
            "causal_identification": False,
            "claim_of_superiority": False,
            "real_savings_measured": False,
            "reserved_nist_seeds_used": False,
        },
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--execute", action="store_true",
                   help="Fetch source-locked historical measurements and run development only.")
    p.add_argument("--out", default="runs/bhs_replicate_pool_v11.json")
    args = p.parse_args(argv)
    if not args.execute:
        print("Protocol only; no source retrieval or historical label evaluation.")
        return 0
    raw = fetch_pinned_source()
    result = build_report(raw)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_checksum": result["source"]["raw_source_sha256"],
        "results": result["aggregates"],
        "decision": result["decision"]["status"],
        "development_only": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
