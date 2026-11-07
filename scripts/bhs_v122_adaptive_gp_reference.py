"""V12.2: measured-response-budget adaptive GP reference policies.

Source-independent comparator implementation. Models only acquired finite response
values with a pooled, estimated observation-noise variance. No historical data
is fetched, no source measurements are bundled and no result is scored here.

Two predeclared scores: analytic GP integrated variance reduction (IVR) and
latent expected-improvement multiplied by a one-step variance reduction factor.
Both are heuristic one-step acquisition criteria; neither is a calibrated
physical decision risk, lookahead knowledge gradient, or full hetGP model.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern

from scripts.bhs_measurement_allocation_v12 import (
    INITIAL_GEOMETRIES,
    INITIAL_MEASUREMENTS,
    TOTAL_MEASUREMENTS,
    REPEATS,
    MAX_PENDING_GEOMETRIES,
    MeasurementContractError,
    initial_geometry_ids,
    require_development_seed,
)
from scripts.bhs_v121_order_contracts import canonical_revealed_state

REFERENCES = ("gp_pooled_noise_ivr", "gp_pooled_noise_ei")
NOISE_FLOOR = 1e-3  # in standardized response units, variance
NOISE_CEILING = 1.0  # intentionally clipped plug-in; not calibrated


@dataclass(frozen=True)
class GPReferenceDiagnostics:
    """Non-scoring model diagnostics, only from revealed source responses."""

    observed_unique_designs: int
    observed_measurements: int
    response_scale: float
    pooled_noise_variance_standardized: float
    alpha_min: float
    alpha_max: float


def _validated_state(candidate_features, observed, seed: int, step: int):
    require_development_seed(seed)
    if type(step) is not int or step < 0:
        raise MeasurementContractError("INVALID_MEASUREMENT_STEP")
    # Validate values and make their representation order-invariant.
    canonical = canonical_revealed_state(candidate_features, observed)
    X = np.asarray(candidate_features, dtype=float).copy()
    initial = initial_geometry_ids(len(X), seed)
    if any(i not in canonical or len(canonical[i]) != REPEATS for i in initial):
        raise MeasurementContractError("INITIAL_TRIPLICATES_NOT_COMPLETELY_REVEALED")
    total_seen = sum(len(v) for v in canonical.values())
    if total_seen != INITIAL_MEASUREMENTS + step:
        raise MeasurementContractError("MEASUREMENTS_AND_STEP_MISMATCH")
    if total_seen >= TOTAL_MEASUREMENTS:
        raise MeasurementContractError("MEASUREMENT_BUDGET_EXHAUSTED")
    pending = [i for i in canonical if len(canonical[i]) < REPEATS]
    if len(pending) > MAX_PENDING_GEOMETRIES:
        raise MeasurementContractError("TOO_MANY_PENDING_DESIGNS")
    return X, canonical, pending, total_seen


def pooled_noise_statistics(observed: Mapping[int, tuple[float, ...]]):
    """Pooled within-design measurement variance, not a noise calibration.

    Only already acquired replicates count toward degrees of freedom. Initial
    six full triplicates ensure a positive degree-of-freedom denominator.
    """
    means = np.asarray([np.mean(observed[k]) for k in observed], dtype=float)
    center = float(np.mean(means))
    scale = float(np.std(means))
    if not np.isfinite(center) or not np.isfinite(scale):
        raise MeasurementContractError("NUMERIC_RESPONSE_STANDARDIZATION_FAILED")
    scale = max(scale, 1e-8)
    pooled_squared_residuals = 0.0
    degrees = 0
    for i in observed:
        responses = np.asarray(observed[i], dtype=float)
        if responses.size >= 2:
            residuals = responses - np.mean(responses)
            pooled_squared_residuals += float(np.dot(residuals, residuals))
            degrees += responses.size - 1
    if degrees == 0:
        raise MeasurementContractError("NO_REPEATED_OBSERVATIONS_FOR_NOISE_MODEL")
    variance = (pooled_squared_residuals / degrees) / (scale * scale)
    if not np.isfinite(variance):
        raise MeasurementContractError("NONFINITE_POOLED_NOISE_VARIANCE")
    # Noise is per measurement; the mean over n measurements has alpha=noise/n.
    variance = float(np.clip(variance, NOISE_FLOOR, NOISE_CEILING))
    return center, scale, variance


def fit_revealed_gp(features, observed):
    """Fit to one mean per observed geometry; partial designs are included.

    All inputs are candidate descriptors or already revealed measurement values.
    This is a homoskedastic noise model with acquisition-count-dependent alpha.
    """
    keys = np.asarray(sorted(observed), dtype=int)
    counts = np.asarray([len(observed[i]) for i in keys], dtype=int)
    means = np.asarray([np.mean(observed[i]) for i in keys], dtype=float)
    center, scale, variance = pooled_noise_statistics(observed)
    standardized = (means - center) / scale
    alpha = variance / counts
    if (not np.isfinite(standardized).all() or
            not np.isfinite(alpha).all() or np.any(alpha <= 0)):
        raise MeasurementContractError("INVALID_GP_OBSERVATIONS_OR_NOISE")
    kernel = ConstantKernel(1.0, (0.1, 10.0)) * Matern(
        length_scale=np.ones(4), length_scale_bounds=(0.1, 10.0), nu=2.5
    )
    gp = GaussianProcessRegressor(
        kernel=kernel,
        alpha=alpha,
        optimizer="fmin_l_bfgs_b",
        n_restarts_optimizer=0,
        normalize_y=False,
        random_state=0,
    )
    try:
        gp.fit(features[keys], standardized)
    except (ValueError, np.linalg.LinAlgError, FloatingPointError) as exc:
        raise MeasurementContractError("REVEALED_GP_FIT_FAILED") from exc
    diag = GPReferenceDiagnostics(
        observed_unique_designs=len(keys),
        observed_measurements=int(counts.sum()),
        response_scale=scale,
        pooled_noise_variance_standardized=variance,
        alpha_min=float(alpha.min()),
        alpha_max=float(alpha.max()),
    )
    completed_max = max(float(np.mean(observed[i])) for i in observed
                        if len(observed[i]) == REPEATS)
    incumbent = (completed_max - center) / scale
    return gp, diag, incumbent


def _feasible_actions(n: int, observed, pending, already_seen: int):
    """Allow only actions that preserve enough budget to complete all pending.

    This deliberate stronger completion constraint can change policy outcomes;
    do not misinterpret differences as proof about repeat choices.
    """
    remaining = TOTAL_MEASUREMENTS - already_seen
    owed = sum(REPEATS - len(observed[i]) for i in pending)
    if owed > remaining:
        raise MeasurementContractError("UNFINISHABLE_PENDING_DESIGNS")
    actions = list(pending)
    may_start = (len(pending) < MAX_PENDING_GEOMETRIES and
                 remaining >= owed + REPEATS)
    if may_start:
        actions.extend(i for i in range(n) if i not in observed)
    if not actions:
        raise MeasurementContractError("NO_FEASIBLE_MEASUREMENT_ACTION")
    return np.asarray(sorted(actions), dtype=int)


def score_candidate_actions(gp, features, candidates, observed, noise_var, incumbent, reference):
    """One-step GP scores, where one action costs exactly one response.

    IVR exact (under fitted model): sum_x Cov(f_x,f_j)^2 /(Var(f_j)+noise)
    EI heuristic: EI_latent(j)*Var(f_j)/(Var(f_j)+noise)
    Both divided by measurements still required to complete design j.
    """
    if reference == "gp_pooled_noise_ivr":
        mu, cov = gp.predict(features, return_cov=True)
        covariance = cov[:, candidates]
        variance = np.clip(np.diag(cov)[candidates], 0.0, None)
        denom = np.maximum(variance + noise_var, 1e-12)
        raw = np.sum(covariance * covariance, axis=0) / denom
    elif reference == "gp_pooled_noise_ei":
        mu, sd = gp.predict(features[candidates], return_std=True)
        variance = np.square(np.asarray(sd, dtype=float))
        delta = mu - incumbent - 0.01
        z = delta / np.maximum(sd, 1e-12)
        ei = np.where(sd > 1e-12,
                      np.maximum(delta * norm.cdf(z) + sd * norm.pdf(z), 0.0),
                      np.maximum(delta, 0.0))
        raw = ei * variance / np.maximum(variance + noise_var, 1e-12)
    else:
        raise MeasurementContractError("UNKNOWN_ADAPTIVE_GP_REFERENCE")
    costs = np.asarray([REPEATS - len(observed.get(int(i), ())) for i in candidates], dtype=float)
    scores = raw / costs
    if scores.shape != candidates.shape or not np.isfinite(scores).all():
        raise MeasurementContractError("INVALID_ADAPTIVE_ACQUISITION_SCORES")
    # Stable canonical ID tie break is handled by sorted candidates / argmax.
    return scores


def select_gp_measurement(reference: str, candidate_features, observed, *, seed: int, step: int):
    """Return (geometry ID, 1-based next ordinal); no hidden-outcome interface."""
    if reference not in REFERENCES:
        raise MeasurementContractError("UNKNOWN_REFERENCE")
    X, seen, pending, taken = _validated_state(candidate_features, observed, seed, step)
    eligible = _feasible_actions(len(X), seen, pending, taken)
    gp, diag, incumbent = fit_revealed_gp(X, seen)
    scores = score_candidate_actions(
        gp, X, eligible, seen,
        diag.pooled_noise_variance_standardized,
        incumbent, reference,
    )
    index = int(eligible[int(np.argmax(scores))])
    ordinal = len(seen.get(index, ())) + 1
    if ordinal not in (1, 2, 3):
        raise MeasurementContractError("INVALID_NEXT_MEASUREMENT_ORDINAL")
    return index, ordinal


def main():
    print("V12.2 source-independent adaptive GP reference; no historical replay.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
