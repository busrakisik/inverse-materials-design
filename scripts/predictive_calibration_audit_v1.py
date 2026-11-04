"""Prequential predictive checks for the fixed development-only hypothesis model.

Forecast each observation before incorporating it. Synthetic examples only;
no seed-derived benchmark tasks, held-out evaluation, or validation approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path
from statistics import NormalDist

from scripts.competing_hypotheses_v2 import Belief, MODELS, basis, predictive_log_score

STATUS = 'EXPLORATORY_PREQUENTIAL_PREDICTIVE_AUDIT_NO_HOLDOUT'
NORMAL = NormalDist()
COVERAGE = .90


def finite(v):
    if type(v) not in (int, float) or not math.isfinite(v):
        raise ValueError('nonfinite real')
    return float(v)


def mixture_cdf(belief: Belief, x: float, y: float, std: float) -> float:
    y = finite(y)
    return sum(p * NORMAL.cdf((y - mu) / math.sqrt(var)) for p, (mu, var) in zip(
        belief.probabilities(), (belief.predictive(i, x, std) for i in range(len(MODELS)))))


def mixture_interval(belief: Belief, x: float, std: float, level: float = COVERAGE):
    """Central equal-tailed interval from the full Bayesian mixture predictive."""
    if type(level) not in (float, int) or not 0 < level < 1 or not math.isfinite(level):
        raise ValueError('invalid interval level')
    components = [belief.predictive(i, x, std) for i in range(len(MODELS))]
    lo = min(mu - 12*math.sqrt(var) for mu, var in components)
    hi = max(mu + 12*math.sqrt(var) for mu, var in components)
    def quantile(p):
        left, right = lo, hi
        for _ in range(70):
            mid = (left+right)/2
            if mixture_cdf(belief, x, mid, std) < p:
                left = mid
            else:
                right = mid
        return (left+right)/2
    alpha = (1-level)/2
    return quantile(alpha), quantile(1-alpha)


def prequential_audit(public, stream, *, level=COVERAGE, prior_parameter_variance=.25):
    """Stream rows: (candidate, measured_y, declared_known_std).

    Observations must be chronologically ordered. Crucially the predictive
    score and coverage are computed BEFORE updating on the current row.
    """
    from scripts.competing_hypotheses_v2 import validate_public
    xs = validate_public(public)
    belief = Belief.initial(prior_parameter_variance)
    used = set()
    records = []
    for row in stream:
        if type(row) not in (list, tuple) or len(row) != 3:
            raise ValueError('invalid stream row')
        cid, y, std = row
        if type(cid) is not str or cid not in xs or cid in used:
            raise ValueError('unknown or duplicate candidate')
        y, std = finite(y), finite(std)
        if std <= 0:
            raise ValueError('nonpositive known measurement std')
        x = xs[cid]
        probs_before = belief.probabilities()
        lo, hi = mixture_interval(belief, x, std, level)
        pit = mixture_cdf(belief, x, y, std)
        log_score = predictive_log_score(belief, x, y, std)
        if not all(math.isfinite(v) for v in (lo, hi, pit, log_score)):
            raise ValueError('invalid predictive diagnostic')
        records.append({'step': len(records)+1, 'candidate_id': cid,
                        'covered': lo <= y <= hi, 'lower': lo, 'upper': hi,
                        'pit': pit, 'negative_log_predictive_density': log_score,
                        'max_model_probability_before': max(probs_before)})
        belief = belief.update(x, y, std)
        used.add(cid)
    if not records:
        raise ValueError('no prequential observations')
    n = len(records)
    # Diagnostics only: these finite sequences are too small to certify calibration.
    return {'status': STATUS, 'records': records, 'count': n,
            'nominal_coverage': level, 'empirical_coverage': sum(r['covered'] for r in records)/n,
            'mean_negative_log_predictive_density': sum(r['negative_log_predictive_density'] for r in records)/n,
            'mean_pit': sum(r['pit'] for r in records)/n,
            'final_max_model_probability': max(belief.probabilities()),
            'formal_calibration_established': False, 'out_of_family_detection_certified': False,
            'scored_validation_allowed': False, 'independent_holdout_used': False}


def development_streams():
    """Two transparent fixed teaching mechanisms; not held-out benchmark seeds."""
    xs = [round(-.95 + .1*i, 6) for i in range(20)]
    public = {'dev_%02d'%i: (x,) for i,x in enumerate(xs)}
    # Same measurement SD and independent reproducible demo noise in both streams.
    a, b = random.Random(19), random.Random(19)
    in_family, out_family = [], []
    for i,x in enumerate(xs):
        cid = 'dev_%02d'%i
        in_family.append((cid, .8*x*x + a.gauss(0,.12), .12))
        # Discontinuous jump not represented by the three smooth basis families.
        out_family.append((cid, (1. if x >= 0 else -1.) + b.gauss(0,.12), .12))
    return public, tuple(in_family), tuple(out_family)


def run_fixed_demo():
    public, in_family, out_family = development_streams()
    inside = prequential_audit(public, in_family)
    outside = prequential_audit(public, out_family)
    # No automatic hypothesis acceptance/rejection or alarm threshold: first
    # characterize these diagnostics and verify them against external baselines.
    return {'status': STATUS, 'in_family': inside, 'out_of_family': outside,
            'mechanisms': {'in_family':'quadratic amplitude 0.8',
                           'out_of_family':'discontinuous sign step'},
            'no_independent_holdout': True, 'scored_validation_allowed': False,
            'claims': 'Diagnostic demonstration, not calibrated model-checking or certified detection'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out-dir', default='runs/predictive_calibration_audit_v1')
    args = p.parse_args()
    report = run_fixed_demo()
    path = Path(args.out_dir)
    path.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(report, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
    (path/'prequential_diagnostics.json').write_bytes(raw)
    (path/'prequential_diagnostics.sha256').write_text(hashlib.sha256(raw).hexdigest()+'  prequential_diagnostics.json\n')
    print(json.dumps({'status': STATUS, 'in_family_records': report['in_family']['count'],
                      'out_of_family_records': report['out_of_family']['count'],
                      'scored_validation_allowed': False}, sort_keys=True))

if __name__ == '__main__':
    main()
