"""Finite fixed-mechanism Bayesian model discrimination; synthetic DEV ONLY.

This module has no materials backend, no seed-derived benchmark tasks, and no
access to private evaluator labels. Fixed functional forms have NO fitted
parameters: this is a correctness/reference baseline, not a new algorithm claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path
from statistics import NormalDist

STATUS = 'FIXED_COMPETING_HYPOTHESES_INFORMATION_GAIN_DEV_ONLY'
MODELS = ('linear', 'quadratic', 'oscillatory')
ROOT2PI = math.sqrt(2.0 * math.pi)


def prediction(model: str, x: float) -> float:
    if model not in MODELS or type(x) not in (float, int) or not math.isfinite(x) or abs(x) > 1.0:
        raise ValueError('model or public scalar descriptor invalid')
    if model == 'linear':
        return float(x)
    if model == 'quadratic':
        return x * x
    return math.sin(3.0 * x)


def normalize_log_weights(log_weights: tuple[float, ...]) -> tuple[float, ...]:
    if len(log_weights) != len(MODELS) or any(type(v) not in (float, int) or not math.isfinite(v) for v in log_weights):
        raise ValueError('invalid log weights')
    offset = max(log_weights)
    weights = [math.exp(v - offset) for v in log_weights]
    z = sum(weights)
    return tuple(v / z for v in weights)


def validate_public(public: dict) -> dict[str, float]:
    if not isinstance(public, dict) or not public:
        raise ValueError('public candidates missing')
    result = {}
    for cid, desc in public.items():
        if type(cid) is not str or not cid or type(desc) not in (list, tuple) or len(desc) != 1:
            raise ValueError('malformed public candidate')
        x = desc[0]
        if type(x) not in (float, int) or not math.isfinite(x) or abs(x) > 1:
            raise ValueError('public feature out of domain')
        result[cid] = float(x)
    return result


def posterior(public: dict, observations, *, noise_std: float = 0.15,
              prior=(1/3, 1/3, 1/3)) -> tuple[float, ...]:
    xs = validate_public(public)
    if type(noise_std) not in (float, int) or not math.isfinite(noise_std) or noise_std <= 0:
        raise ValueError('invalid noise scale')
    if len(prior) != len(MODELS) or any(type(p) not in (int, float) or not math.isfinite(p) or p <= 0 for p in prior):
        raise ValueError('invalid strictly positive priors')
    total = sum(prior)
    logs = [math.log(p / total) for p in prior]
    seen = set()
    for row in observations:
        if type(row) not in (tuple, list) or len(row) != 2:
            raise ValueError('malformed observation')
        cid, y = row
        if cid not in xs or cid in seen or type(y) not in (int, float) or not math.isfinite(y):
            raise ValueError('unknown/repeated/nonfinite observation')
        seen.add(cid)
        for i, model in enumerate(MODELS):
            residual = (y - prediction(model, xs[cid])) / noise_std
            logs[i] -= 0.5 * residual * residual
    return normalize_log_weights(tuple(logs))


def entropy(probs) -> float:
    if len(probs) != len(MODELS) or any(type(p) not in (float, int) or not math.isfinite(p) or p < 0 for p in probs) or abs(sum(probs) - 1) > 1e-9:
        raise ValueError('invalid probability vector')
    return -sum(p * math.log(p) for p in probs if p > 0)


def update_probs(probs, x, y, noise_std):
    """Single-observation Bayes update; model index has a finite prior."""
    entropy(probs)
    if type(y) not in (int, float) or not math.isfinite(y):
        raise ValueError('invalid synthetic observation')
    if type(noise_std) not in (int, float) or not math.isfinite(noise_std) or noise_std <= 0:
        raise ValueError('invalid likelihood width')
    # A zero probability stays zero, useful in extreme cases of concentrated priors.
    logs = [(math.log(p) - 0.5 * ((y - prediction(model, x)) / noise_std) ** 2) if p else -1e300
            for p, model in zip(probs, MODELS)]
    return normalize_log_weights(tuple(logs))


def expected_information_gain(probs, x: float, noise_std: float = 0.15, quantiles: int = 64) -> float:
    """Deterministic midpoint-normal quadrature of E[KL(post || prior)].

    This is an approximation; quadrature resolution, likelihood calibration, and
    fixed-model assumptions require later independent sensitivity analysis.
    """
    entropy(probs)
    prediction('linear', x)
    if type(quantiles) is not int or not 8 <= quantiles <= 1024:
        raise ValueError('invalid quadrature resolution')
    if type(noise_std) not in (float, int) or not math.isfinite(noise_std) or noise_std <= 0:
        raise ValueError('invalid noise scale')
    start = entropy(probs)
    normal = NormalDist()
    expectation = 0.0
    for p, model in zip(probs, MODELS):
        if not p:
            continue
        mu = prediction(model, x)
        for k in range(quantiles):
            z = normal.inv_cdf((k + 0.5) / quantiles)
            y = mu + noise_std * z
            expectation += p * entropy(update_probs(probs, x, y, noise_std)) / quantiles
    # Sampling quadrature can produce tiny negative deviations from exact MI >= 0.
    return max(0.0, start - expectation)


class CompetingHypothesesPolicyV1:
    def __init__(self, *, noise_std=0.15, quantiles=64):
        if type(noise_std) not in (float, int) or not math.isfinite(noise_std) or noise_std <= 0:
            raise ValueError('invalid noise std')
        if type(quantiles) is not int or not 8 <= quantiles <= 1024:
            raise ValueError('invalid quadrature')
        self.noise_std = float(noise_std)
        self.quantiles = quantiles
        self.last_diagnostics = None

    def choose(self, public, observations):
        xs = validate_public(public)
        observed = [row[0] for row in observations]
        probs = posterior(public, observations, noise_std=self.noise_std)
        remaining = sorted(set(xs).difference(observed))
        if not remaining:
            raise ValueError('candidate pool exhausted')
        scores = {cid: expected_information_gain(probs, xs[cid], self.noise_std, self.quantiles)
                  for cid in remaining}
        choice = min(remaining, key=lambda cid: (-scores[cid], cid))
        self.last_diagnostics = {
            'status': STATUS, 'posterior': dict(zip(MODELS, probs)),
            'entropy_nats': entropy(probs), 'information_gain_nats': scores,
            'chosen': choice, 'fixed_models_only': True,
            'information_gain_approximate': True, 'scored_validation_allowed': False,
            'materials_discovery_validated': False,
        }
        return choice


def fixed_development_demo():
    """No benchmark task generation; fixed deterministic demonstration only."""
    public = {f'dev_{i:02d}': (round(-1 + i / 6, 6),) for i in range(13)}
    rng = random.Random(17)
    policy = CompetingHypothesesPolicyV1(quantiles=64)
    obs = []
    records = []
    for step in range(5):
        cid = policy.choose(public, tuple(obs))
        x = public[cid][0]
        # Demonstration's synthetic generating model never enters choose().
        y = prediction('quadratic', x) + rng.gauss(0, 0.15)
        records.append({'step': step + 1, 'selected': cid, 'x': x,
                        'synthetic_y': y, 'prior_to_observation': policy.last_diagnostics['posterior']})
        obs.append((cid, y))
    return {'status': STATUS, 'synthetic_generating_model': 'quadratic',
            'observations': records, 'final_model_probabilities': dict(zip(MODELS, posterior(public, obs))),
            'scored_validation_allowed': False, 'independent_holdout_used': False,
            'physical_validation': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', default='runs/competing_hypotheses_v1')
    args = parser.parse_args()
    report = fixed_development_demo()
    folder = Path(args.out_dir)
    folder.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    (folder / 'fixed_demo.json').write_bytes(raw)
    (folder / 'fixed_demo.sha256').write_text(hashlib.sha256(raw).hexdigest() + '  fixed_demo.json\n')
    print(json.dumps({'status': STATUS, 'queries': len(report['observations']),
                      'scored_validation_allowed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
