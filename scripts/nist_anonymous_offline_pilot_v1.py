"""BHS anonymous-coordinate *development-only* offline replay on pinned NIST data.

No chemical element attribution, no independent holdout, no noise calibration,
no live laboratory experiment and no algorithm superiority claim.
This replays already measured historical labels only AFTER each acquisition.
Do not commit or upload raw sample rows, selected indices, or per-step labels.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import random
from pathlib import Path

import numpy as np
from scipy.io import loadmat
from scipy.special import ndtr
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF

from scripts.nist_dataset_inspection_v1 import fetch_source, validate_source
from scripts.nist_composition_mapping_v1 import normalize_composition_axis, target_vector
from scripts.multivariate_hypotheses_v1 import MultivariateBelief, MODELS

STATUS = 'NIST_ANONYMOUS_COORDINATE_OFFLINE_DEV_REPLAY_NOT_VALIDATED'
POLICIES = ('random', 'gp_ei', 'gp_ucb', 'bhs_bma_ei')
SEEDS = (7, 13, 23)  # NEVER BHS independent holdout seeds 10000..10099
INITIAL = 3
BUDGET = 15
NOISE_ASSUMED = 0.15  # after observed-initial normalization, NOT instrument-measured
GP_LENGTHSCALE_ASSUMED = 0.22  # relative simplex-coordinate units, NOT tuned evidence
GP_ALPHA_ASSUMED = NOISE_ASSUMED ** 2


def finite_pilot_pool(arrays):
    """Construct a retrospective eligible candidate pool, no chemistry names.

    The *evaluator* uses finite label availability to define an offline dataset.
    This means this is not a prospective missing-measurement selection benchmark.
    """
    if not isinstance(arrays, dict) or set(arrays) != {'C', 'Coer', 'Kerr', 'XRD', 'TTH'}:
        raise ValueError('unexpected NIST data fields')
    c, _ = normalize_composition_axis(arrays['C'])
    n = c.shape[0]
    y = target_vector(arrays['Kerr'], n, 'Kerr')
    finite_c = np.isfinite(c).all(axis=1)
    nonnegative = np.all(c >= 0, axis=1)
    sums = c.sum(axis=1)
    near_one = np.isclose(sums, 1.0, atol=.02, rtol=0)
    near_hundred = np.isclose(sums, 100.0, atol=2.0, rtol=0)
    plausible = finite_c & nonnegative & (near_one | near_hundred)
    eligible = plausible & np.isfinite(y)
    if np.count_nonzero(eligible) < 20:
        raise ValueError('insufficient eligible samples; do not silently expand criteria')
    raw = c[eligible].astype(float)
    # Only relative anonymous coordinates, not certified atomic-fraction semantics.
    scaled = raw / raw.sum(axis=1, keepdims=True)
    if np.any(~np.isfinite(scaled)) or np.any(scaled < 0) or np.any(scaled > 1):
        raise ValueError('invalid normalized composition')
    return scaled, y[eligible].copy(), {
        'total_source_samples': int(n),
        'eligible_samples': int(eligible.sum()),
        'excluded_rows': int((~eligible).sum()),
        'missing_kerr_rows': int((~np.isfinite(y)).sum()),
        'invalid_or_unresolved_coordinate_rows': int((~plausible).sum()),
        'distinct_anonymous_coordinates': int(np.unique(scaled, axis=0).shape[0]),
        'element_order_verified': False,
        'coordinate_scale_source_verified': False,
        'candidate_eligibility_defined_using_retrospective_target_availability': True,
    }


def expected_improvement(mu, sd, incumbent):
    """Standard Gaussian EI for maximization; handles degenerate variance."""
    mu, sd = np.broadcast_arrays(np.asarray(mu, dtype=float), np.asarray(sd, dtype=float))
    if (not np.isfinite(mu).all() or not np.isfinite(sd).all()
            or np.any(sd < 0) or not math.isfinite(float(incumbent))):
        raise ValueError('invalid EI input')
    delta = mu - float(incumbent)
    z = np.divide(delta, sd, out=np.zeros_like(delta), where=sd > 1e-12)
    ei = np.where(sd > 1e-12, delta*ndtr(z) + sd*np.exp(-.5*z*z)/math.sqrt(2*math.pi),
                  np.maximum(delta, 0))
    return np.maximum(ei, 0)


def normalize_observed_initial(y_initial):
    """Use ONLY common, already observed initial measurements."""
    y_initial = np.asarray(y_initial, dtype=float)
    if y_initial.ndim != 1 or y_initial.size < 2 or not np.isfinite(y_initial).all():
        raise ValueError('invalid initial observations')
    center = float(y_initial.mean())
    std = float(y_initial.std())
    if std < 1e-8:
        std = max(abs(center), 1.0)
    return center, std


def gp_predict(candidates, selected, observed_z):
    """Fixed-hyperparameter GP reference; NOT an optimized literature reproduction."""
    xy = np.asarray(candidates, dtype=float)[:, :2]
    training_x = xy[list(selected)]
    observed_z = np.asarray(observed_z, dtype=float)
    if len(training_x) != len(observed_z) or not np.isfinite(observed_z).all():
        raise ValueError('observed-only GP contract violated')
    kernel = ConstantKernel(1.0, constant_value_bounds='fixed') * RBF(
        length_scale=GP_LENGTHSCALE_ASSUMED, length_scale_bounds='fixed')
    model = GaussianProcessRegressor(kernel=kernel, alpha=GP_ALPHA_ASSUMED,
                                     normalize_y=False, optimizer=None)
    model.fit(training_x, observed_z)
    mu, sd = model.predict(xy, return_std=True)
    if not (np.isfinite(mu).all() and np.isfinite(sd).all()):
        raise ValueError('GP returned nonfinite prediction')
    return mu, sd


def bhs_ei(candidates, selected, observed_z):
    """Posterior-weighted EI for generic functional forms in anonymous coordinates.

    The existing implementation calls a term 'fe_co_interaction' internally;
    here it is ONLY opaque coordinate_0*coordinate_1, NOT a Fe-Co assignment.
    """
    belief = MultivariateBelief(prior_variance=0.5)
    for idx, z in zip(selected, observed_z):
        belief.observe(np.asarray(candidates[idx], dtype=float), float(z), NOISE_ASSUMED)
    weights = belief.probabilities()
    best = float(np.max(observed_z))
    scores = np.zeros(len(candidates), dtype=float)
    for model_name in MODELS:
        mu = np.empty(len(candidates))
        latent_sd = np.empty(len(candidates))
        for i, c in enumerate(candidates):
            pred_mean, pred_variance = belief.predictive(model_name, c, NOISE_ASSUMED)
            mu[i] = pred_mean
            latent_sd[i] = math.sqrt(max(pred_variance - NOISE_ASSUMED**2, 0.))
        scores += weights[model_name] * expected_improvement(mu, latent_sd, best)
    return scores


def choose_next(policy, candidates, selected, observed_z, rng):
    """POLICY API has no hidden labels, global optimum, or oracle access."""
    candidates = np.asarray(candidates, dtype=float)
    if policy not in POLICIES or len(selected) != len(observed_z):
        raise ValueError('invalid policy or observations')
    remaining = np.ones(len(candidates), dtype=bool)
    remaining[np.asarray(selected, dtype=int)] = False
    available = np.flatnonzero(remaining)
    if len(available) == 0:
        raise ValueError('candidate pool exhausted')
    if policy == 'random':
        return int(available[rng.randrange(len(available))])
    if policy == 'bhs_bma_ei':
        scores = bhs_ei(candidates, selected, observed_z)
    else:
        mu, sd = gp_predict(candidates, selected, observed_z)
        if policy == 'gp_ei':
            scores = expected_improvement(mu, sd, np.max(observed_z))
        elif policy == 'gp_ucb':
            scores = mu + 2.0 * sd
        else:
            raise ValueError('unsupported policy')
    if len(scores) != len(candidates) or not np.isfinite(scores[available]).all():
        raise ValueError('invalid policy acquisition scores')
    return int(available[np.argmax(scores[available])])


def campaign(candidates, hidden_labels, policy, seed, budget=BUDGET):
    """Evaluator discloses a label ONLY for chosen indices; no samples exported."""
    x = np.asarray(candidates, dtype=float)
    y = np.asarray(hidden_labels, dtype=float)
    if (x.ndim != 2 or x.shape[1] != 3 or y.shape != (len(x),)
            or not np.isfinite(x).all() or not np.isfinite(y).all()
            or policy not in POLICIES or budget < INITIAL + 1 or budget > len(x)
            or not isinstance(seed, int) or seed in range(10000,10100)):
        raise ValueError('invalid campaign, data, or reserved independent seed')
    rng = random.Random(seed)
    selected = rng.sample(range(len(x)), INITIAL)
    revealed_y = [float(y[i]) for i in selected]
    center, scale = normalize_observed_initial(revealed_y)
    best_history = [max(revealed_y)]
    for _ in range(INITIAL, budget):
        observed_z = (np.asarray(revealed_y) - center) / scale
        next_idx = choose_next(policy, x, selected, observed_z, rng)
        if next_idx in selected:
            raise AssertionError('policy proposed a previously observed sample')
        selected.append(next_idx)
        revealed_y.append(float(y[next_idx]))
        best_history.append(max(revealed_y))
    # Retrospective evaluator metric ONLY after selection loop ends.
    # No global best/hidden labels are passed to any selection policy.
    rng_y = float(np.ptp(y))
    if rng_y <= 0:
        raise ValueError('constant objective has undefined normalized regret')
    gap = max(0., (float(np.max(y)) - max(revealed_y)) / rng_y)
    return {'final_normalized_simple_regret':gap,
            'n_distinct_samples_acquired':len(set(selected)),
            'n_total_acquired':len(selected),
            'n_initial_acquired':INITIAL}


def evaluate_development(candidates, hidden_labels, seeds=SEEDS, budget=BUDGET):
    if not seeds or any(not isinstance(s,int) or s in range(10000,10100) for s in seeds):
        raise ValueError('independent holdout seeds prohibited')
    stats = {}
    for policy in POLICIES:
        rs = [campaign(candidates, hidden_labels, policy, s, budget) for s in seeds]
        vals = [v['final_normalized_simple_regret'] for v in rs]
        stats[policy] = {
            'mean_final_normalized_simple_regret_exploratory':float(np.mean(vals)),
            'min_final_normalized_simple_regret_exploratory':float(np.min(vals)),
            'max_final_normalized_simple_regret_exploratory':float(np.max(vals)),
            'replicate_count':len(rs),
        }
    return stats


def run_pinned_bytes(raw, seeds=SEEDS, budget=BUDGET):
    digest = validate_source(raw)
    arrays = {k:v for k,v in loadmat(io.BytesIO(raw)).items() if not k.startswith('__')}
    x, y, summary = finite_pilot_pool(arrays)
    stats = evaluate_development(x, y, seeds, budget)
    return {
        'status':STATUS,
        'target':'Kerr', 'unit':'mrad',
        'task':'retrospective property optimization (NOT causal mechanism identification)',
        'source_sha256':digest,
        'source_description':'NIST pinned REMI Fe-Co-Ni data',
        'anonymous_coordinates': ['source_col_0','source_col_1','source_col_2'],
        'source_column_to_element_order_verified':False,
        'pilot_pool_summary':summary,
        'policies':stats,
        'configuration':{'seeds':list(seeds),'initial_observations':INITIAL,
                         'total_budget_per_campaign':budget,
                         'fixed_gp_lengthscale_assumption':GP_LENGTHSCALE_ASSUMED,
                         'fixed_nominal_noise_std_after_initial_normalization':NOISE_ASSUMED,
                         'gaussian_noise_std_measured':False,
                         'costs_assumed_equal_not_measured':True,
                         'gp_hyperparameters_tuned':False},
        'development_exploratory_metrics_only':True,
        'policy_labels_hidden_until_selected':True,
        'physical_validation':False,
        'independent_holdout_used':False,
        'scored_validation_allowed':False,
        'claim_of_superiority':False,
        'dataset_ready_for_physical_bhs':False,
        'authoritative_element_mapping_resolved':False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--fetch',action='store_true')
    p.add_argument('--out-dir',type=Path,default=Path('runs/nist_anonymous_offline_pilot_v1'))
    a=p.parse_args()
    if not a.fetch:
        p.error('explicit --fetch required; no automatic network access')
    report=run_pinned_bytes(fetch_source())
    a.out_dir.mkdir(parents=True,exist_ok=True)
    payload=(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    (a.out_dir/'aggregate_dev_report.json').write_bytes(payload)
    (a.out_dir/'aggregate_dev_report.sha256').write_text(
        hashlib.sha256(payload).hexdigest()+'  aggregate_dev_report.json\n')
    print(json.dumps({'status':STATUS,'eligible_samples':report['pilot_pool_summary']['eligible_samples'],
                      'policies':list(POLICIES),'development_only':True,
                      'scored_validation_allowed':False},sort_keys=True))


if __name__ == '__main__':
    main()
