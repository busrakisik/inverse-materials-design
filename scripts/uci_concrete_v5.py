"""UCI concrete 28-day retrospective development; never an independent evaluation.

Source: Yeh (1998), UCI dataset 165, DOI 10.24432/C5PK67, CC BY 4.0.
The model-family portfolio is statistical, not a set of physical mechanisms.
No raw source observations are redistributed or stored by this module.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

import numpy as np
from scipy.special import logsumexp
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, RBF, ConstantKernel

DATASET_ID = 165
DEVELOPMENT_SEEDS = (7, 13, 23)
POLICIES = ("random", "gp_ei", "kernel_portfolio_ei")
INITIAL_OBSERVATIONS = 6
ADDITIONAL_ACQUISITIONS = 10
RESERVED_RANGE = range(10000, 10100)


def require_development_seeds(seeds: Sequence[int]) -> None:
    if not seeds or any(
        not isinstance(seed, (int, np.integer)) or isinstance(seed, bool)
        or seed < 0 or seed in RESERVED_RANGE for seed in seeds
    ):
        raise ValueError("Only nonnegative development seeds outside 10000..10099 are permitted.")


def select_28_day_pool(features, targets, columns):
    """Choose one row per identical 28-day feature profile, without inspecting labels."""
    X = np.asarray(features, dtype=float)
    y = np.asarray(targets, dtype=float).reshape(-1)
    if X.ndim != 2 or X.shape[1] != 8 or y.shape != (X.shape[0],):
        raise ValueError("Expected 8 predictors and exactly one target per observation.")
    if X.shape[0] != 1030:
        raise ValueError("UCI concrete accession must have 1030 original observations.")
    if not (np.isfinite(X).all() and np.isfinite(y).all()):
        raise ValueError("Dataset must have no missing or nonfinite predictors or labels.")
    age_columns = [i for i, col in enumerate(columns) if str(col).lower().startswith("age")]
    if len(age_columns) != 1:
        raise ValueError("Cannot verify the concrete age feature.")
    mask = np.isclose(X[:, age_columns[0]], 28.0, atol=1e-9, rtol=0.0)
    filtered = X[mask]
    filtered_y = y[mask]
    if len(filtered) < 50:
        raise ValueError("Too few 28-day observations; verify source and schema.")
    # Exact feature-duplicate selection is deterministic and LABEL-BLIND.
    seen = set()
    indices = []
    for i, row in enumerate(filtered):
        key = tuple(row.tolist())
        if key not in seen:
            indices.append(i)
            seen.add(key)
    if len(indices) < INITIAL_OBSERVATIONS + ADDITIONAL_ACQUISITIONS + 2:
        raise ValueError("Too few distinct candidate profiles.")
    return filtered[indices], filtered_y[indices], {
        "source_rows": int(X.shape[0]),
        "rows_age_28": int(len(filtered)),
        "unique_profiles_age_28": int(len(indices)),
        "repeat_profile_rows_excluded_by_features_only": int(len(filtered) - len(indices)),
        "repeated_targets_averaged": False,
    }


def scale_candidates(X):
    """Unlabelled candidate inputs may be standardized without viewing response values."""
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or not np.isfinite(X).all() or X.shape[0] < 2:
        raise ValueError("Candidate matrix must be finite with at least two rows.")
    center = X.mean(axis=0)
    scale = X.std(axis=0)
    scale[scale < 1e-12] = 1.0
    return (X - center) / scale


def _ei(mu, std, incumbent):
    std = np.maximum(std, 1e-12)
    delta = mu - incumbent - 0.01
    z = delta / std
    return delta * norm.cdf(z) + std * norm.pdf(z)


def _fit_predict(kernel, X_obs, y_obs, X_candidates):
    # Fit is performed only on previously acquired labels.
    model = GaussianProcessRegressor(
        kernel=ConstantKernel(1.0, constant_value_bounds="fixed") * kernel,
        alpha=0.05,
        optimizer=None,
        normalize_y=False,
    )
    model.fit(X_obs, y_obs)
    mean, std = model.predict(X_candidates, return_std=True)
    return mean, std, float(model.log_marginal_likelihood_value_)


def choose_next(X_unlabelled, observed_indices, observed_labels, policy, rng):
    """A label-isolated policy: the full target vector is NEVER an argument."""
    X = np.asarray(X_unlabelled, dtype=float)
    observed = [int(i) for i in observed_indices]
    labels = np.asarray(observed_labels, dtype=float)
    if len(set(observed)) != len(observed) or labels.shape != (len(observed),):
        raise ValueError("Observed labels must match unique observed candidate IDs.")
    if not np.isfinite(labels).all() or not np.isfinite(X).all():
        raise ValueError("Only finite observations and candidate features are allowed.")
    if policy not in POLICIES:
        raise ValueError("Unsupported policy.")
    available = np.setdiff1d(np.arange(len(X)), observed)
    if len(available) == 0:
        raise ValueError("No unobserved candidates.")
    if policy == "random":
        return int(rng.choice(available))

    label_center = float(labels.mean())
    label_std = max(float(labels.std()), 1e-8)
    standardized_y = (labels - label_center) / label_std
    incumbent = float(np.max(standardized_y))
    observed_X = X[observed]
    available_X = X[available]

    if policy == "gp_ei":
        mu, sd, _ = _fit_predict(
            Matern(length_scale=3.0, length_scale_bounds="fixed", nu=2.5),
            observed_X, standardized_y, available_X,
        )
        score = _ei(mu, sd, incumbent)
    else:
        kernels = (
            Matern(length_scale=2.5, length_scale_bounds="fixed", nu=1.5),
            RBF(length_scale=3.5, length_scale_bounds="fixed"),
        )
        predictions = [
            _fit_predict(kernel, observed_X, standardized_y, available_X)
            for kernel in kernels
        ]
        log_weights = np.array([p[2] for p in predictions], dtype=float)
        weights = np.exp(log_weights - logsumexp(log_weights))
        score = sum(
            float(w) * _ei(mu, sd, incumbent)
            for w, (mu, sd, _) in zip(weights, predictions)
        )
    # Deterministic tie-breaking by candidate index.
    return int(available[int(np.argmax(score))])


def run_campaign(X_unlabelled, hidden_targets, seed, policy):
    """Evaluator is the only code path able to index unrevealed target values."""
    require_development_seeds((seed,))
    if policy not in POLICIES:
        raise ValueError("Unrecognized policy.")
    X = np.asarray(X_unlabelled, dtype=float)
    hidden = np.asarray(hidden_targets, dtype=float).reshape(-1)
    if hidden.shape != (len(X),) or not np.isfinite(hidden).all():
        raise ValueError("Evaluator target shape or finiteness mismatch.")
    rng = np.random.default_rng(int(seed) + (0 if policy == "random" else 100 + POLICIES.index(policy)))
    initial_rng = np.random.default_rng(int(seed))
    selected = [int(i) for i in initial_rng.choice(len(X), size=INITIAL_OBSERVATIONS, replace=False)]
    for _ in range(ADDITIONAL_ACQUISITIONS):
        acquired_labels = hidden[selected].copy()  # oracle reveals ONLY these
        next_index = choose_next(X, selected, acquired_labels, policy, rng)
        if next_index in selected:
            raise AssertionError("A selected candidate was acquired twice.")
        selected.append(next_index)
    best_observed = float(np.max(hidden[selected]))
    full_best = float(np.max(hidden))  # evaluator-only, AFTER policy execution
    full_range = float(np.ptp(hidden))
    regret = max(0.0, full_best - best_observed)
    return {
        "seed": int(seed),
        "policy": policy,
        "initial_observations": INITIAL_OBSERVATIONS,
        "additional_acquisitions": ADDITIONAL_ACQUISITIONS,
        "final_simple_regret_mpa": regret,
        "normalized_final_simple_regret": regret / full_range if full_range else 0.0,
        "unique_observations": len(set(selected)),
    }


def evaluate_development(X, y, seeds=DEVELOPMENT_SEEDS):
    require_development_seeds(seeds)
    X_std = scale_candidates(X)
    outcomes = [run_campaign(X_std, y, seed, policy)
                for seed in seeds for policy in POLICIES]
    aggregates = {}
    for policy in POLICIES:
        rows = [r for r in outcomes if r["policy"] == policy]
        aggregates[policy] = {
            "mean_normalized_final_regret": float(np.mean([r["normalized_final_simple_regret"] for r in rows])),
            "mean_final_regret_mpa": float(np.mean([r["final_simple_regret_mpa"] for r in rows])),
            "development_campaigns": len(rows),
        }
    return outcomes, aggregates


def fetch_source():
    # Source data are acquired only with explicit --execute; no automatic raw-data export.
    from ucimlrepo import fetch_ucirepo
    dataset = fetch_ucirepo(id=DATASET_ID)
    features = dataset.data.features
    target = dataset.data.targets
    if features is None or target is None:
        raise RuntimeError("UCI source did not return predictor and response tables.")
    X = features.to_numpy(dtype=float)
    y = target.to_numpy(dtype=float).reshape(-1)
    columns = list(features.columns)
    # Fingerprint describes the parsed numerical table, NOT the original .xls file.
    sha = hashlib.sha256()
    sha.update(json.dumps(columns, separators=(",", ":")).encode())
    sha.update(np.ascontiguousarray(X, dtype="<f8").tobytes())
    sha.update(np.ascontiguousarray(y, dtype="<f8").tobytes())
    return X, y, columns, sha.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Fetch source data and run development only.")
    parser.add_argument("--out", default="runs/uci_concrete_development_v5.json")
    args = parser.parse_args(argv)
    if not args.execute:
        print("Protocol only; source download and evaluation disabled. Pass --execute for development.")
        return 0

    X, y, names, fingerprint = fetch_source()
    pool_X, pool_y, pool_info = select_28_day_pool(X, y, names)
    outcomes, aggregates = evaluate_development(pool_X, pool_y)
    summary = {
        "study": "BHS external concrete property-optimization development v5",
        "source": "UCI Concrete Compressive Strength, I-Cheng Yeh",
        "source_dataset_id": DATASET_ID,
        "source_doi": "10.24432/C5PK67",
        "source_license": "CC BY 4.0",
        "source_url": "https://archive.ics.uci.edu/dataset/165/concrete-compressive-strength",
        "parsed_numeric_table_sha256": fingerprint,
        "original_xls_sha256_verified": False,
        "source_feature_columns": [str(x) for x in names],
        "pool": pool_info,
        "target": "28-day concrete compressive strength (MPa)",
        "development_only": True,
        "independent_holdout_used": False,
        "scored_validation_allowed": False,
        "physical_validation": False,
        "physical_hypotheses_tested": False,
        "real_cost_measured": False,
        "claimed_superiority": False,
        "reserved_seeds_used": False,
        "development_seeds": list(DEVELOPMENT_SEEDS),
        "selector_protocol": {
            "initial_observations": INITIAL_OBSERVATIONS,
            "additional_acquisitions": ADDITIONAL_ACQUISITIONS,
            "policy_classes": list(POLICIES),
            "statistical_model_portfolio_is_not_physical_hypotheses": True,
            "one_representative_per_exact_duplicate_feature_profile": True,
            "label_visibility": "observed_indices_only",
            "actual_instrument_costs": "unknown; uniform acquisition count only",
        },
        "aggregates": aggregates,
        "development_campaign_results": outcomes,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"source_rows": pool_info["source_rows"],
        "age_28_unique_profiles": pool_info["unique_profiles_age_28"],
        "aggregates": aggregates, "development_only": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
