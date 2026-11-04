"""Independent, closed-form checks of BHS scalar conjugate model and EIG.

Synthetic developer-known fixtures only. No benchmark tasks, holdout or materials.
Reference batch algebra deliberately does not invoke Belief.update or information_gain.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

from scripts.competing_hypotheses_v2 import Belief, MODELS, basis, information_gain, predictive_log_score

STATUS = 'BHS_INDEPENDENT_MATHEMATICAL_VERIFICATION_DEV_ONLY'
LOG2PI = math.log(2 * math.pi)


def _finite(z, *, positive=False):
    if type(z) not in (int, float) or not math.isfinite(z) or (positive and z <= 0):
        raise ValueError('expected finite real')
    return float(z)


def logsumexp(values):
    if not values:
        raise ValueError('empty list')
    top = max(values)
    return top + math.log(sum(math.exp(t - top) for t in values))


def batch_reference(observations, *, prior_mean=1.0, prior_variance=.25, model_priors=None):
    """Complete square in scalar a, separately for each model.

    The log evidence is computed from Gaussian integrals, not sequential
    predictive likelihoods or any Belief implementation.
    observations = chronological (x, y, declared sigma) triplets.
    """
    m0, v0 = _finite(prior_mean), _finite(prior_variance, positive=True)
    priors = tuple(1 / len(MODELS) for _ in MODELS) if model_priors is None else tuple(model_priors)
    if len(priors) != len(MODELS) or any(_finite(p, positive=True) <= 0 for p in priors):
        raise ValueError('invalid priors')
    z = sum(priors)
    clean = []
    for x, y, sd in observations:
        x, y, sd = _finite(x), _finite(y), _finite(sd, positive=True)
        if abs(x) > 1:
            raise ValueError('x outside domain')
        clean.append((x, y, sd))
    means, variances, log_evidences = [], [], []
    for model in MODELS:
        precision = 1 / v0
        linear = m0 / v0
        quad = m0 * m0 / v0
        log_norm = 0.0
        for x, y, sd in clean:
            phi = basis(model, x)
            precision += phi * phi / (sd * sd)
            linear += phi * y / (sd * sd)
            quad += y * y / (sd * sd)
            log_norm += LOG2PI + 2 * math.log(sd)
        variance = 1 / precision
        mean = linear / precision
        # p(y_1,...,y_n|m) from direct integration over a
        evidence = -.5 * (log_norm + math.log(v0 * precision) + quad - linear * linear / precision)
        means.append(mean)
        variances.append(variance)
        log_evidences.append(evidence)
    logs = [math.log(p / z) + v for p, v in zip(priors, log_evidences)]
    total = logsumexp(logs)
    weights = tuple(math.exp(v - total) for v in logs)
    return {'means': tuple(means), 'variances': tuple(variances),
            'log_model_evidence': tuple(log_evidences), 'probabilities': weights,
            'log_total_evidence': total}


def direct_mixture_logpdf(weights, mus, variances, y):
    return logsumexp([math.log(p) - .5*(LOG2PI + math.log(v) + (y-mu)**2/v)
                      for p, mu, v in zip(weights, mus, variances) if p > 0])


def direct_eig_grid(belief, x, std, *, grid_points=4001, tails=10.0):
    """Independent deterministic numeric integration of I(H;Y).

    Computes sum_m p(m) int p(y|m) log[p(y|m)/p(y)] dy by midpoint
    quadrature over a declared bounded interval. Does not call update or EIG.
    Tail truncation and grid resolution errors remain numerical limitations.
    """
    x, std = _finite(x), _finite(std, positive=True)
    if abs(x) > 1 or type(grid_points) is not int or not 1001 <= grid_points <= 20001:
        raise ValueError('invalid integration grid')
    if not 6 <= _finite(tails) <= 16:
        raise ValueError('invalid tail bound')
    weights = belief.probabilities()
    components = [belief.predictive(i, x, std) for i in range(len(MODELS))]
    left = min(mu - tails * math.sqrt(v) for mu, v in components)
    right = max(mu + tails * math.sqrt(v) for mu, v in components)
    delta = (right - left) / grid_points
    total = 0.0
    for i in range(grid_points):
        y = left + (i + .5)*delta
        individual = [- .5*(LOG2PI + math.log(v) + (y-mu)**2/v)
                      for mu, v in components]
        mix = logsumexp([math.log(p)+lik for p, lik in zip(weights, individual) if p > 0])
        for p, logpdf in zip(weights, individual):
            if p:
                total += p*math.exp(logpdf)*(logpdf-mix)*delta
    return total


def audit_fixtures():
    """Fewer than 10 transparent fixed design points, no benchmark seeds."""
    fixtures = (
        ((-.8, -.55, .17), (.3, .12, .22), (.9, .72, .14)),
        ((-.5, -.15, .26), (.6, .45, .19)),
        ((0., .2, .15),),
        (),
    )
    results = []
    for index, obs in enumerate(fixtures):
        ref = batch_reference(obs)
        b = Belief.initial()
        for x, y, std in obs:
            b = b.update(x, y, std)
        error_mean = max(abs(a-c) for a, c in zip(ref['means'], b.means))
        error_variance = max(abs(a-c) for a, c in zip(ref['variances'], b.variances))
        error_probability = max(abs(a-c) for a, c in zip(ref['probabilities'], b.probabilities()))
        results.append({'fixture': index, 'n':len(obs), 'max_mean_abs_error':error_mean,
                        'max_variance_abs_error':error_variance,
                        'max_model_probability_abs_error':error_probability})
    x, sd = -.8, .18
    b = Belief.initial()
    e_grid = direct_eig_grid(b, x, sd, grid_points=4001)
    e16, e64, e128 = [information_gain(b, x, sd, q) for q in (16, 64, 128)]
    # Reference midpoint numeric quadrature is not claimed to be exact.
    return {'status':STATUS, 'batch_checks':results,
            'eig_nats':{'midpoint_grid_4001':e_grid,'quantile_16':e16,
                        'quantile_64':e64,'quantile_128':e128,
                        'absolute_error_128_vs_grid':abs(e128-e_grid)},
            'formal_calibration_established':False,
            'physical_validation':False,'independent_holdout_used':False,
            'scored_validation_allowed':False,'claim_of_superiority':False}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out-dir',default='runs/independent_math_verification_v1')
    opt=parser.parse_args()
    report=audit_fixtures()
    path=Path(opt.out_dir); path.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(report, indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    (path/'mathematical_checks.json').write_bytes(raw)
    (path/'mathematical_checks.sha256').write_text(hashlib.sha256(raw).hexdigest()+'  mathematical_checks.json\n')
    print(json.dumps({'status':STATUS,'batch_cases':len(report['batch_checks']),
                      'scored_validation_allowed':False},sort_keys=True))

if __name__=='__main__':
    main()
