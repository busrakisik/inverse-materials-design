"""Synthetic-only Bayesian linear-regression Thompson policy; NOT physical BHS validation.

Public scalar descriptor x; observations contain only previously queried (candidate, value).
Conjugate Gaussian model: w ~ N(0, prior_variance), y | x,w ~ N(w*x, noise_variance).
The model is knowingly misspecified for some preregistered scenarios. No MCTS.
"""
from __future__ import annotations
import hashlib
import math
import random

STATUS = 'SYNTHETIC_BAYESIAN_ONLY_NOT_SCORED_NOT_PHYSICAL'


class BayesianOnlyPolicyV1:
    def __init__(self, seed: int, prior_variance: float = 1.0, noise_variance: float = 0.1,
                 exploration_scale: float = 1.0):
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError('seed must be integer')
        for name, val in [('prior_variance', prior_variance), ('noise_variance', noise_variance),
                          ('exploration_scale', exploration_scale)]:
            if isinstance(val, bool) or not isinstance(val, (float, int)) or not math.isfinite(val):
                raise ValueError('invalid ' + name)
        if prior_variance <= 0 or noise_variance <= 0 or exploration_scale < 0:
            raise ValueError('invalid hyperparameters')
        self._rng = random.Random(seed)
        self.prior_variance = float(prior_variance)
        self.noise_variance = float(noise_variance)
        self.exploration_scale = float(exploration_scale)

    def posterior(self, public, observations):
        if not isinstance(public, dict) or not public:
            raise ValueError('invalid public descriptors')
        xs = {}
        for cid, descriptor in public.items():
            if not isinstance(cid, str) or not cid or not isinstance(descriptor, (tuple, list)) or len(descriptor) != 1:
                raise ValueError('invalid descriptor')
            x = descriptor[0]
            if isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x):
                raise ValueError('invalid public feature')
            xs[cid] = float(x)
        seen = set()
        precision = 1.0 / self.prior_variance
        weighted = 0.0
        for row in observations:
            if not isinstance(row, (tuple, list)) or len(row) != 2:
                raise ValueError('invalid observation')
            cid, value = row
            if cid not in xs or cid in seen or isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
                raise ValueError('unknown, duplicate, or invalid observation')
            seen.add(cid)
            x = xs[cid]
            precision += x*x / self.noise_variance
            weighted += x*float(value) / self.noise_variance
        variance = 1.0 / precision
        mean = variance * weighted
        if not math.isfinite(mean) or not math.isfinite(variance):
            raise ValueError('numerical failure')
        return mean, variance, xs, seen

    def choose(self, public, observations):
        mean, variance, xs, seen = self.posterior(public, observations)
        remaining = sorted(set(xs) - seen)
        if not remaining:
            raise ValueError('pool exhausted')
        sampled_weight = self._rng.gauss(mean, math.sqrt(variance)*self.exploration_scale)
        return min(remaining, key=lambda cid: (-sampled_weight*xs[cid], cid))
