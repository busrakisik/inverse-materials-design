"""Parametric Bayesian model comparison with known per-observation noise.

EXPLORATORY synthetic mathematical prototype. Not a calibrated discovery model.
No benchmark generator or holdout access. Stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist

STATUS = "PARAMETRIC_COMPETING_HYPOTHESES_DEV_ONLY_NO_HOLDOUT"
MODELS = ("linear", "quadratic", "oscillatory")
LOG2PI = math.log(2.0 * math.pi)
NORMAL = NormalDist()


def _finite(value, *, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("expected finite real value")
    if positive and value <= 0:
        raise ValueError("expected strictly positive value")
    return float(value)


def basis(model, x):
    x = _finite(x)
    if abs(x) > 1 or model not in MODELS:
        raise ValueError("invalid model or public feature domain")
    return {"linear": lambda: x, "quadratic": lambda: x*x,
            "oscillatory": lambda: math.sin(3*x)}[model]()


def validate_public(public):
    if type(public) is not dict or not public:
        raise ValueError("empty public candidate set")
    xs = {}
    for cid, desc in public.items():
        if type(cid) is not str or not cid or type(desc) not in (tuple, list) or len(desc) != 1:
            raise ValueError("invalid public candidate")
        x = _finite(desc[0])
        if abs(x) > 1:
            raise ValueError("public descriptor outside [-1,1]")
        xs[cid] = x
    return xs


@dataclass(frozen=True)
class Belief:
    """Posterior over model index and each model's scalar parameter a.

    y_i = a_m * phi_m(x_i) + eps_i, eps_i ~ N(0, sigma_i**2)
    a_m ~ N(1, prior_parameter_variance), m prior initially uniform.
    """
    log_weights: tuple[float, ...]
    means: tuple[float, ...]
    variances: tuple[float, ...]

    @classmethod
    def initial(cls, prior_parameter_variance=0.25, priors=(1/3, 1/3, 1/3)):
        v = _finite(prior_parameter_variance, positive=True)
        if type(priors) not in (tuple, list) or len(priors) != len(MODELS):
            raise ValueError("invalid model prior")
        ps = [_finite(p, positive=True) for p in priors]
        total = sum(ps)
        if not math.isfinite(total) or total <= 0:
            raise ValueError("invalid prior normalization")
        return cls(tuple(math.log(p/total) for p in ps),
                   tuple(1.0 for _ in MODELS), tuple(v for _ in MODELS))

    def probabilities(self):
        if len(self.log_weights) != len(MODELS) or any(not math.isfinite(z) for z in self.log_weights):
            raise ValueError("invalid log evidence")
        high = max(self.log_weights)
        w = [math.exp(z-high) for z in self.log_weights]
        total = sum(w)
        return tuple(p/total for p in w)

    def entropy(self):
        return -sum(p*math.log(p) for p in self.probabilities() if p > 0)

    def predictive(self, model_index, x, observation_std):
        if type(model_index) is not int or not 0 <= model_index < len(MODELS):
            raise ValueError("invalid model index")
        x = _finite(x)
        s = _finite(observation_std, positive=True)
        feature = basis(MODELS[model_index], x)
        mu = feature*self.means[model_index]
        variance = s*s + feature*feature*self.variances[model_index]
        if not math.isfinite(variance) or variance <= 0:
            raise ValueError("predictive numerical failure")
        return mu, variance

    def update(self, x, y, observation_std):
        """Exact conjugate update and sequential *marginal* predictive evidence."""
        x = _finite(x)
        y = _finite(y)
        s = _finite(observation_std, positive=True)
        logs, means, vars_ = [], [], []
        for i, model in enumerate(MODELS):
            phi = basis(model, x)
            mu_y, predictive_var = self.predictive(i, x, s)
            delta = y-mu_y
            log_lik = -0.5*(LOG2PI + math.log(predictive_var) + delta*delta/predictive_var)
            gain = self.variances[i]*phi/predictive_var
            m_new = self.means[i] + gain*delta
            v_new = self.variances[i] * (s*s/predictive_var)
            if not all(math.isfinite(z) for z in (log_lik, m_new, v_new)) or v_new <= 0:
                raise ValueError("numerical Bayesian update failure")
            logs.append(self.log_weights[i]+log_lik)
            means.append(m_new)
            vars_.append(v_new)
        # Normalization is deferred to probabilities(); log evidence is retained.
        return Belief(tuple(logs), tuple(means), tuple(vars_))


def fit_belief(public, observations, *, prior_parameter_variance=0.25):
    xs = validate_public(public)
    belief = Belief.initial(prior_parameter_variance)
    seen = set()
    # Explicit observation-specific known standard deviation. Not a "trust" label:
    # actual uncertainty must come from calibrated measurement procedures.
    for row in observations:
        if type(row) not in (list, tuple) or len(row) != 3:
            raise ValueError("observation must be (candidate_id, measured_y, known_std)")
        cid, y, std = row
        if type(cid) is not str or cid not in xs or cid in seen:
            raise ValueError("unknown or duplicated observation")
        seen.add(cid)
        belief = belief.update(xs[cid], y, std)
    return belief, seen, xs


def information_gain(belief, x, planned_std, quantiles=32):
    """Deterministic quantile approximation to E[KL(p(H|y)||p(H))].

    Integrates model-marginal posterior predictive p(y|H,D), which includes
    parameter uncertainty (unlike plug-in parameter approaches).
    """
    x = _finite(x)
    _finite(planned_std, positive=True)
    if type(quantiles) is not int or not 8 <= quantiles <= 128:
        raise ValueError("invalid quadrature resolution")
    prior_probs = belief.probabilities()
    initial_entropy = belief.entropy()
    expected_entropy = 0.0
    for i, p in enumerate(prior_probs):
        if p == 0:
            continue
        mu, variance = belief.predictive(i, x, planned_std)
        std = math.sqrt(variance)
        for j in range(quantiles):
            z = NORMAL.inv_cdf((j+0.5)/quantiles)
            updated = belief.update(x, mu+std*z, planned_std)
            expected_entropy += p*updated.entropy()/quantiles
    # Non-negative exact MI; approximation can yield tiny errors.
    return max(0.0, initial_entropy - expected_entropy)


def predictive_log_score(belief, x, y, std):
    """Marginal -log p(y|x,D), useful as a predictive model-check diagnostic."""
    y = _finite(y)
    logs = []
    for i, p in enumerate(belief.probabilities()):
        if p == 0:
            continue
        mu, var = belief.predictive(i, x, std)
        logpdf = -0.5*(LOG2PI+math.log(var)+(y-mu)**2/var)
        logs.append(math.log(p)+logpdf)
    offset = max(logs)
    return -(offset+math.log(sum(math.exp(z-offset) for z in logs)))


class ParametricHypothesisPolicyV2:
    def __init__(self, *, prior_parameter_variance=0.25, planned_std=0.15, quantiles=32):
        self.prior_parameter_variance = _finite(prior_parameter_variance, positive=True)
        self.planned_std = _finite(planned_std, positive=True)
        if type(quantiles) is not int or not 8 <= quantiles <= 128:
            raise ValueError("invalid quadrature")
        self.quantiles = quantiles
        self.last_diagnostics = None

    def choose(self, public, observations, *, planned_stds=None):
        belief, seen, xs = fit_belief(public, observations,
                                     prior_parameter_variance=self.prior_parameter_variance)
        remaining = sorted(set(xs)-seen)
        if not remaining:
            raise ValueError("pool exhausted")
        if planned_stds is not None:
            if type(planned_stds) is not dict or set(planned_stds) != set(xs):
                raise ValueError("planned standard deviations must cover all public candidates")
            scale = {cid: _finite(v, positive=True) for cid, v in planned_stds.items()}
        else:
            scale = {cid: self.planned_std for cid in xs}
        scores = {cid: information_gain(belief, xs[cid], scale[cid], self.quantiles)
                  for cid in remaining}
        candidate = min(remaining, key=lambda cid: (-scores[cid], cid))
        self.last_diagnostics = {
            "status": STATUS, "model_probabilities": dict(zip(MODELS, belief.probabilities())),
            "parameter_posterior_mean": dict(zip(MODELS, belief.means)),
            "parameter_posterior_variance": dict(zip(MODELS, belief.variances)),
            "estimated_information_gain_nats": scores,
            "choice": candidate, "measurement_stds_explicit": True,
            "assumes_correct_family_and_known_gaussian_noise": True,
            "calibration_established": False, "physical_validation": False,
            "scored_validation_allowed": False
        }
        return candidate


def development_demo():
    public = {f"dev_{i:02d}": (round(-1 + i/6, 6),) for i in range(13)}
    # Known planned measurement noise, fixed in this demonstration.
    stds = {cid: (0.12 if i%2 == 0 else 0.24) for i, cid in enumerate(public)}
    rng = random.Random(17)
    policy = ParametricHypothesisPolicyV2(quantiles=32)
    obs, trace = [], []
    for step in range(5):
        candidate = policy.choose(public, obs, planned_stds=stds)
        x = public[candidate][0]
        y = 0.8*x*x + rng.gauss(0, stds[candidate])
        trace.append({"step": step+1, "candidate_id": candidate, "x": x,
                      "y": y, "known_std": stds[candidate]})
        obs.append((candidate, y, stds[candidate]))
    belief, _, _ = fit_belief(public, obs)
    return {"status": STATUS, "task": "fixed development-only quadratic demonstration",
            "generating_parameter": 0.8, "trace": trace,
            "posterior_probabilities": dict(zip(MODELS, belief.probabilities())),
            "parameter_means": dict(zip(MODELS, belief.means)),
            "independent_holdout_used": False, "physical_validation": False,
            "scored_validation_allowed": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="runs/competing_hypotheses_v2")
    args = parser.parse_args()
    result = development_demo()
    folder = Path(args.out_dir)
    folder.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+"\n").encode()
    (folder/"development_demo.json").write_bytes(raw)
    (folder/"development_demo.sha256").write_text(
        hashlib.sha256(raw).hexdigest()+"  development_demo.json\n")
    print(json.dumps({"status": STATUS, "queries": len(result["trace"]),
                      "scored_validation_allowed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
