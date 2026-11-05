"""BHS multivariate composition-response hypothesis prototype (synthetic only).

Three *phenomenological response-shape* families on a Fe/Co/Ni simplex.
These are NOT established physical mechanisms, NIST-fitted models or validated
experiment-selection policies. Known per-observation Gaussian std is assumed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np

STATUS = 'BHS_MULTIVARIATE_COMPOSITION_HYPOTHESES_DEV_ONLY'
MODELS = ('linear', 'fe_co_interaction', 'localized_response')
PRIOR_VARIANCE = 0.5


def composition(values):
    """Validate ordered (Fe,Co,Ni) fractions; do not infer NIST column order."""
    if not isinstance(values, (tuple, list, np.ndarray)) or len(values) != 3:
        raise ValueError('composition must be three ordered fractions')
    try:
        v = np.asarray(values, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError('invalid composition') from exc
    if v.shape != (3,) or not np.all(np.isfinite(v)) or np.any(v < 0) or np.any(v > 1):
        raise ValueError('composition values outside finite [0,1]')
    if not np.isclose(float(v.sum()), 1.0, rtol=0.0, atol=1e-8):
        raise ValueError('composition does not sum to one')
    return v


def features(model, fractions):
    fe, co, ni = composition(fractions)
    basic = [1.0, float(fe), float(co)]  # Ni omitted to avoid exact collinearity
    if model == 'linear':
        return np.asarray(basic, dtype=float)
    if model == 'fe_co_interaction':
        return np.asarray(basic + [float(fe * co)], dtype=float)
    if model == 'localized_response':
        radius2 = float((fe-1/3)**2 + (co-1/3)**2 + (ni-1/3)**2)
        bump = math.exp(-radius2 / (2 * 0.18**2))
        return np.asarray(basic + [bump], dtype=float)
    raise ValueError('unknown hypothesis family')


def _positive(x):
    if isinstance(x, (bool, np.bool_)) or not isinstance(x, (float, int, np.floating, np.integer)) or not math.isfinite(float(x)) or float(x) <= 0:
        raise ValueError('expected positive finite real')
    return float(x)


class MultivariateBelief:
    """Independent Bayesian linear regressions with posterior model evidence.

    beta_m ~ N(0, prior_variance I); y|beta,m ~ N(phi_m @ beta_m, sigma**2).
    Model probabilities update from pre-observation *marginal* predictive pdf.
    """
    def __init__(self, prior_variance=PRIOR_VARIANCE):
        prior_variance = _positive(prior_variance)
        self.models = {}
        for model in MODELS:
            d = len(features(model, (1., 0., 0.)))
            self.models[model] = {
                'mean': np.zeros(d),
                'covariance': np.eye(d) * prior_variance,
                'log_evidence': -math.log(len(MODELS)),
            }
        self.n = 0

    def probabilities(self):
        logs = np.array([self.models[m]['log_evidence'] for m in MODELS])
        z = float(logs.max())
        w = np.exp(logs - z)
        return dict(zip(MODELS, (w / w.sum()).tolist()))

    def predictive(self, model, fractions, std):
        if model not in self.models:
            raise ValueError('unknown model')
        sigma = _positive(std)
        phi = features(model, fractions)
        state = self.models[model]
        mean = float(phi @ state['mean'])
        variance = float(sigma**2 + phi @ state['covariance'] @ phi)
        if variance <= 0 or not math.isfinite(variance) or not math.isfinite(mean):
            raise ValueError('invalid predictive distribution')
        return mean, variance

    def observe(self, fractions, measured_y, std):
        c = composition(fractions)
        if isinstance(measured_y, bool) or not isinstance(measured_y, (int, float, np.number)) or not math.isfinite(float(measured_y)):
            raise ValueError('measurement must be finite')
        sigma = _positive(std)
        y = float(measured_y)
        # All forecasts and marginal likelihoods are computed before updates.
        pending = {}
        for model in MODELS:
            phi = features(model, c)
            state = self.models[model]
            mu, variance = self.predictive(model, c, sigma)
            cov_phi = state['covariance'] @ phi
            gain = cov_phi / variance
            updated_mean = state['mean'] + gain * (y - mu)
            updated_cov = state['covariance'] - np.outer(cov_phi, cov_phi) / variance
            updated_cov = 0.5 * (updated_cov + updated_cov.T)
            logpdf = -.5 * (math.log(2 * math.pi * variance) + (y-mu)**2 / variance)
            if not (np.isfinite(updated_mean).all() and np.isfinite(updated_cov).all() and math.isfinite(logpdf)):
                raise ValueError('numerical Bayesian failure')
            pending[model] = (updated_mean, updated_cov, state['log_evidence'] + logpdf)
        for model, (mean, covariance, weight) in pending.items():
            self.models[model] = {'mean': mean, 'covariance': covariance, 'log_evidence': weight}
        self.n += 1
        return self.probabilities()


def batch_reference(model, observations, prior_variance=PRIOR_VARIANCE):
    """Independent conjugate batch solution using precision-matrix algebra."""
    prior_variance = _positive(prior_variance)
    if model not in MODELS:
        raise ValueError('unknown model')
    d = len(features(model, (1., 0., 0.)))
    precision = np.eye(d) / prior_variance
    rhs = np.zeros(d)
    for row in observations:
        if not isinstance(row, (list, tuple)) or len(row) != 3:
            raise ValueError('observation must be (composition,y,std)')
        c, y, std = row
        phi = features(model, c)
        sigma = _positive(std)
        if isinstance(y, bool) or not isinstance(y, (int, float, np.number)) or not math.isfinite(float(y)):
            raise ValueError('invalid observed value')
        precision += np.outer(phi, phi) / sigma**2
        rhs += phi * float(y) / sigma**2
    covariance = np.linalg.inv(precision)
    return covariance @ rhs, covariance


def demo():
    rng = random.Random(23)
    points = []
    for i in range(12):
        weights = [rng.gammavariate(2., 1.) for _ in range(3)]
        c = tuple(v / sum(weights) for v in weights)
        points.append(c)
    model = MultivariateBelief()
    observations = []
    trace = []
    for i, c in enumerate(points[:6]):
        # Synthetic fixed response shape; not an identified NIST physical model.
        response = 0.3 + 0.4*c[0] - 0.2*c[1] + 1.2*c[0]*c[1]
        y = response + rng.gauss(0, .08)
        before = model.probabilities()
        after = model.observe(c, y, .08)
        observations.append((c, y, .08))
        trace.append({'step': i+1, 'posterior_before': before, 'posterior_after': after})
    discrepancies = {}
    for family in MODELS:
        bm, bc = batch_reference(family, observations)
        st = model.models[family]
        discrepancies[family] = {'mean_max_abs_error': float(np.max(np.abs(st['mean']-bm))),
                                 'covariance_max_abs_error': float(np.max(np.abs(st['covariance']-bc)))}
    return {'status': STATUS, 'n_synthetic_observations': len(observations),
            'hypothesis_families': list(MODELS), 'posterior_model_probabilities': model.probabilities(),
            'batch_reference_discrepancies': discrepancies, 'trace': trace,
            'composition_element_order_verified_for_nist': False,
            'scientific_mechanisms_validated': False, 'measurement_uncertainty_calibrated': False,
            'nist_data_used': False, 'real_data_experiment_executed': False,
            'independent_holdout_used': False, 'physical_validation': False,
            'scored_validation_allowed': False, 'claim_of_superiority': False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out-dir', default='runs/multivariate_hypotheses_v1')
    args = p.parse_args()
    report = demo()
    folder = Path(args.out_dir)
    folder.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()
    (folder / 'synthetic_multivariate_report.json').write_bytes(raw)
    (folder / 'synthetic_multivariate_report.sha256').write_text(hashlib.sha256(raw).hexdigest() + '  synthetic_multivariate_report.json\n')
    print(json.dumps({'status': STATUS, 'n_synthetic_observations': report['n_synthetic_observations'],
                      'scored_validation_allowed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
