"""Sequential rival predictive-model inference on explicitly public design inputs.

SYNTHETIC DEVELOPMENT COMPONENT. Not a full scientific hypothesis engine,
not verified physical likelihoods, not physical mechanism identification,
not observation-contingent MCTS, not an empirical comparison.
"""
from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import math
from pathlib import Path

import numpy as np
from numpy.polynomial.hermite import hermgauss


HYPOTHESES = ("H_ADD", "H_TWIST_THICKNESS")
FEATURES = ("n", "theta_deg", "r_mm", "t_mm")
MODEL_PRIORS = (0.5, 0.5)
COEFF_PRIOR_SD_J = 10.0
ASSUMED_NOISE_SD_J = 5.0
QUADRATURE_POINTS = 16
EIG_NEGATIVE_TOLERANCE = 1e-8
NO_GO = {
    "development_only": True,
    "synthetic_protocol_only": True,
    "scored_validation_allowed": False,
    "physical_mechanisms_identified": False,
    "scientific_likelihood_calibrated": False,
    "full_bhs_fair_comparison_ready": False,
    "independent_holdout_used": False,
    "claim_of_superiority": False,
    "real_savings_measured": False,
    "laboratory_action_allowed": False,
}


class HypothesisContractError(ValueError):
    pass


def normalize_design(design: dict) -> np.ndarray:
    """Predeclared dimensionless geometric inputs; no outcome-derived scaler."""
    if type(design) is not dict or set(design) != set(FEATURES):
        raise HypothesisContractError("EXACT_PUBLIC_DESIGN_FIELDS_REQUIRED")
    n = design["n"]
    if type(n) is not int or n < 1 or n > 100:
        raise HypothesisContractError("INVALID_COLUMN_COUNT")
    nums = {}
    for field in ("theta_deg", "r_mm", "t_mm"):
        value = design[field]
        if type(value) not in (int, float) or not math.isfinite(float(value)):
            raise HypothesisContractError("INVALID_PUBLIC_GEOMETRY")
        nums[field] = float(value)
    theta = nums["theta_deg"]
    radius = nums["r_mm"]
    thickness = nums["t_mm"]
    if not (0 <= theta <= 180 and 0 < thickness <= radius <= 1000.0):
        raise HypothesisContractError("NONPHYSICAL_PUBLIC_DESIGN")
    return np.asarray([
        n / 12.0 - 1.0,
        theta / 90.0 - 1.0,
        radius / 2.5 - 1.0,
        thickness - 1.0,
    ], dtype=float)


def _features(base: np.ndarray, hypothesis: str) -> np.ndarray:
    common = np.concatenate(([1.0], base))
    if hypothesis == "H_ADD":
        return common
    if hypothesis == "H_TWIST_THICKNESS":
        return np.append(common, base[1] * base[3])
    raise HypothesisContractError("UNKNOWN_HYPOTHESIS")


def check_public_and_observations(
    public: dict, observations: list | tuple
) -> tuple[dict[str, np.ndarray], list[tuple[str, float]]]:
    """The only policy-time view: public pool plus prior acquired responses."""
    if type(public) is not dict or not public or len(public) > 5000:
        raise HypothesisContractError("INVALID_CANDIDATE_POOL")
    computed = {}
    for cid, design in public.items():
        if type(cid) is not str or not cid.strip() or len(cid) > 128:
            raise HypothesisContractError("INVALID_CANDIDATE_ID")
        computed[cid] = normalize_design(design)
    if not isinstance(observations, (list, tuple)) or len(observations) > len(computed):
        raise HypothesisContractError("INVALID_OBSERVATION_HISTORY")
    history = []
    seen = set()
    for entry in observations:
        if not isinstance(entry, (list, tuple)) or len(entry) != 2:
            raise HypothesisContractError("MALFORMED_REVEALED_OBSERVATION")
        cid, value = entry
        if (type(cid) is not str or cid not in computed or cid in seen
                or type(value) not in (int, float) or not math.isfinite(float(value))
                or float(value) < 0):
            raise HypothesisContractError("UNKNOWN_DUPLICATE_OR_INVALID_OBSERVATION")
        seen.add(cid)
        history.append((cid, float(value)))
    return computed, history


@dataclass
class ConditionalLinearModel:
    hypothesis: str
    mean: np.ndarray
    cov: np.ndarray
    log_evidence: float = 0.0

    @classmethod
    def initial(cls, hypothesis: str) -> "ConditionalLinearModel":
        dimension = 5 if hypothesis == "H_ADD" else 6
        if hypothesis not in HYPOTHESES:
            raise HypothesisContractError("UNKNOWN_HYPOTHESIS")
        return cls(
            hypothesis,
            np.zeros(dimension, dtype=float),
            np.eye(dimension, dtype=float) * COEFF_PRIOR_SD_J ** 2,
        )

    def predict(self, base: np.ndarray) -> tuple[float, float]:
        x = _features(base, self.hypothesis)
        mu = float(x @ self.mean)
        variance = float(ASSUMED_NOISE_SD_J ** 2 + x @ self.cov @ x)
        if not math.isfinite(mu) or not math.isfinite(variance) or variance <= 0:
            raise HypothesisContractError("NONFINITE_PREDICTIVE_DISTRIBUTION")
        return mu, variance

    def reveal(self, base: np.ndarray, y: float) -> None:
        """Exact sequential conjugate Gaussian update; mutate only after validation."""
        mu, variance = self.predict(base)
        residual = y - mu
        log_pdf = -0.5 * (math.log(2 * math.pi * variance)
                          + residual ** 2 / variance)
        if not math.isfinite(log_pdf):
            raise HypothesisContractError("NONFINITE_MODEL_EVIDENCE")
        x = _features(base, self.hypothesis)
        cross = self.cov @ x
        gain = cross / variance
        proposed_mean = self.mean + gain * residual
        proposed_cov = self.cov - np.outer(cross, cross) / variance
        proposed_cov = (proposed_cov + proposed_cov.T) * 0.5
        if not (np.isfinite(proposed_mean).all()
                and np.isfinite(proposed_cov).all()
                and float(np.linalg.eigvalsh(proposed_cov).min()) > -1e-8):
            raise HypothesisContractError("INVALID_POSTERIOR_COVARIANCE")
        self.mean, self.cov = proposed_mean, proposed_cov
        self.log_evidence += log_pdf


def _model_probabilities(models: tuple[ConditionalLinearModel, ...]) -> dict:
    logs = np.asarray([math.log(p) + m.log_evidence
                       for p, m in zip(MODEL_PRIORS, models)], dtype=float)
    if not np.isfinite(logs).all():
        raise HypothesisContractError("NONFINITE_MODEL_WEIGHTS")
    weights = np.exp(logs - logs.max())
    weights /= weights.sum()
    return {model.hypothesis: float(weight)
            for model, weight in zip(models, weights)}


def fit_from_visible_history(
    public: dict, observations: list | tuple
) -> tuple[dict[str, np.ndarray], list[tuple[str, float]],
           tuple[ConditionalLinearModel, ...], dict]:
    normalized, observed = check_public_and_observations(public, observations)
    models = tuple(ConditionalLinearModel.initial(h) for h in HYPOTHESES)
    for cid, y in observed:
        for model in models:
            model.reveal(normalized[cid], y)
    return normalized, observed, models, _model_probabilities(models)


def _entropy(p: np.ndarray) -> float:
    return -float(np.sum(np.where(p > 0, p * np.log(np.maximum(p, 1e-300)), 0.0)))


def _normal_logpdf(y: float, mean: float, variance: float) -> float:
    return -0.5 * (math.log(2.0 * math.pi * variance)
                   + (y - mean) ** 2 / variance)


def expected_model_information_gain(
    base: np.ndarray, models: tuple[ConditionalLinearModel, ...],
    weights: dict, quadrature_points: int = QUADRATURE_POINTS
) -> float:
    """One-step model-ID information only; integration under current mixture."""
    if type(quadrature_points) is not int or quadrature_points != QUADRATURE_POINTS:
        raise HypothesisContractError("QUADRATURE_RULE_FROZEN")
    components = [m.predict(base) for m in models]
    probabilities = np.asarray([weights[m.hypothesis] for m in models])
    if not np.isfinite(probabilities).all() or min(probabilities) <= 0:
        raise HypothesisContractError("INVALID_MODEL_PROBABILITY")
    nodes, gauss_weights = hermgauss(quadrature_points)
    prior_entropy = _entropy(probabilities)
    expected_entropy = 0.0
    for which, (mean, variance) in enumerate(components):
        for node, weight in zip(nodes, gauss_weights):
            hypothetical_y = mean + math.sqrt(2.0 * variance) * float(node)
            updated_logs = np.asarray([
                math.log(p) + _normal_logpdf(hypothetical_y, mu, v)
                for p, (mu, v) in zip(probabilities, components)
            ])
            updated = np.exp(updated_logs - updated_logs.max())
            updated /= updated.sum()
            expected_entropy += (
                float(probabilities[which])
                * float(weight) / math.sqrt(math.pi)
                * _entropy(updated)
            )
    gain = prior_entropy - expected_entropy
    if not math.isfinite(gain) or gain < -EIG_NEGATIVE_TOLERANCE:
        raise HypothesisContractError("INVALID_QUADRATURE_INFORMATION_GAIN")
    return max(0.0, float(gain))


def choose_next(public: dict, observations: list | tuple) -> dict:
    """Caller supplies only public designs and previously revealed outcomes."""
    normalized, observed, models, weights = fit_from_visible_history(
        public, observations)
    seen = {cid for cid, _ in observed}
    remaining = sorted(set(normalized) - seen)
    if not remaining:
        raise HypothesisContractError("NO_UNOBSERVED_CANDIDATES")
    gains = {
        cid: expected_model_information_gain(normalized[cid], models, weights)
        for cid in remaining
    }
    selected = min(remaining, key=lambda cid: (-gains[cid], cid))
    return {
        "status": "SYNTHETIC_ONLY_RIVAL_PREDICTION_POLICY",
        "selected_candidate_id": selected,
        "model_probabilities": weights,
        "model_predictive_distributions_at_selection": {
            m.hypothesis: {
                "mean_assumed_j": m.predict(normalized[selected])[0],
                "variance_assumed_j2": m.predict(normalized[selected])[1],
            } for m in models
        },
        "candidate_information_gain_nats": gains,
        "selection_information_gain_nats": gains[selected],
        "previously_revealed_count": len(observed),
        "selection_objective": "ONE_STEP_MODEL_ID_INFORMATION_GAIN_NOT_TOUGHNESS_OPTIMIZATION",
        "hypotheses_are_physical_mechanisms": False,
        "decision_chronology_authenticated": False,
        "real_response_cost_verified": False,
        **NO_GO,
    }


def main() -> None:
    """Small visibly manufactured logic example; NEVER load scientific datasets."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    candidates = {
        "fabricated-a": {"n": 12, "theta_deg": 90, "r_mm": 2.5, "t_mm": 1.0},
        "fabricated-b": {"n": 12, "theta_deg": 120, "r_mm": 2.5, "t_mm": 1.3},
        "fabricated-c": {"n": 8, "theta_deg": 60, "r_mm": 2.2, "t_mm": 0.7},
        "fabricated-d": {"n": 10, "theta_deg": 100, "r_mm": 2.8, "t_mm": 0.9},
    }
    initial = choose_next(candidates, [])
    synthetic_observation = (initial["selected_candidate_id"], 12.0)
    second = choose_next(candidates, [synthetic_observation])
    report = {
        "schema": "BHS-V12.18-SYNTHETIC-DUAL-PREDICTIVE-HYPOTHESES",
        "fabricated_fixture_only": True,
        "original_source_measurements_read": False,
        "first_choice": initial,
        "manufactured_response_j": 12.0,
        "second_choice_after_only_manufactured_revealed_response": second,
        "scored_benchmark": False,
        **NO_GO,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print("Math-only hypotheses:", HYPOTHESES)
    print("Synthetic second posterior:", second["model_probabilities"])
    print("Real scientific performance: NOT TESTED")


if __name__ == "__main__":
    main()
