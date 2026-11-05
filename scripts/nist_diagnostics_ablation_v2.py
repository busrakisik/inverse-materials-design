"""NIST Kerr *exploratory development* ablations; never an independent benchmark.

This module reuses a pinned-source, anonymous-coordinate retrospective oracle.
Selected labels are revealed only AFTER selection; data are not redistributed.
The ablation candidates are DEVELOPMENT choices, informed by v1 results, and
must not be interpreted as pre-registered validation or physics hypotheses.
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
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF

from scripts.nist_dataset_inspection_v1 import fetch_source, validate_source
from scripts.nist_anonymous_offline_pilot_v1 import (
    INITIAL, BUDGET, NOISE_ASSUMED, GP_LENGTHSCALE_ASSUMED,
    finite_pilot_pool, normalize_observed_initial, expected_improvement,
    gp_predict, choose_next as choose_next_v1,
)
from scripts.multivariate_hypotheses_v1 import MultivariateBelief, MODELS, features

STATUS = 'NIST_KERR_REAL_DATA_ABLATION_EXPLORATORY_NOT_VALIDATED'
DEV_SEEDS = (7, 13, 23, 31, 41)  # 7/13/23 previously explored; NOT an independent sample.
REPORT_BUDGETS = (5, 10, 15)
POLICIES = (
    'random', 'gp_ei', 'gp_ucb', 'bhs_bma_ei',
    'bhs_linear_ei', 'bhs_interaction_ei', 'bhs_localized_ei',
    'bhs_bma_sigma_0p05', 'bhs_bma_sigma_0p30',
    'gp_ei_length_0p12', 'gp_ei_length_0p40',
)
BHS_CONFIG = {
    'bhs_bma_ei': ('bma', NOISE_ASSUMED),
    'bhs_linear_ei': ('linear', NOISE_ASSUMED),
    'bhs_interaction_ei': ('fe_co_interaction', NOISE_ASSUMED),
    'bhs_localized_ei': ('localized_response', NOISE_ASSUMED),
    'bhs_bma_sigma_0p05': ('bma', 0.05),
    'bhs_bma_sigma_0p30': ('bma', 0.30),
}
V1_PRIOR_REPORTED_MEAN_REGRET = {
    'random': 0.19775608454202978,
    'gp_ei': 0.025001283117256388,
    'gp_ucb': 0.07450292037487553,
    'bhs_bma_ei': 0.13924593765076626,
}
# Source: NIST Anonymous Offline Pilot v1, Actions run 41977734103, artifact 13392975164.
# Reference numbers are already-explored DEVELOPMENT data, not validation targets.

GP_CONFIG = {
    'gp_ei_length_0p12': 0.12,
    'gp_ei_length_0p40': 0.40,
}


def validate_dev_protocol(seeds=DEV_SEEDS, budget=BUDGET):
    if not isinstance(seeds, (list, tuple)) or not seeds or len(set(seeds)) != len(seeds):
        raise ValueError('development seeds must be distinct and nonempty')
    if any(type(s) is not int or s < 0 or s in range(10000, 10100) for s in seeds):
        raise ValueError('reserved BHS independent seeds are forbidden')
    if type(budget) is not int or budget != BUDGET:
        raise ValueError('this exploratory ablation is defined for the fixed 15-sample budget')
    if not all(INITIAL <= b <= budget for b in REPORT_BUDGETS):
        raise ValueError('invalid diagnostic budgets')
    return True


def anonymous_features(model: str, candidates: np.ndarray) -> np.ndarray:
    """Vectorized copy of v1 *mathematical* bases; never attribute elements."""
    x = np.asarray(candidates, dtype=float)
    if (x.ndim != 2 or x.shape[1] != 3 or not np.isfinite(x).all()
            or np.any(x < 0) or np.any(x > 1)
            or not np.allclose(x.sum(axis=1), 1, atol=1e-8, rtol=0)):
        raise ValueError('expected finite anonymous N x 3 simplex coordinates')
    basic = np.column_stack([np.ones(len(x)), x[:, 0], x[:, 1]])
    if model == 'linear':
        return basic
    if model == 'fe_co_interaction':
        return np.column_stack([basic, x[:, 0] * x[:, 1]])
    if model == 'localized_response':
        bump = np.exp(-np.sum((x - 1/3)**2, axis=1) / (2 * 0.18**2))
        return np.column_stack([basic, bump])
    raise ValueError('unknown mathematical response family')


def bhs_ablation_scores(candidates, selected, observed_z, family='bma', sigma=NOISE_ASSUMED):
    """EI over latent response. sigma is an *assumed*, normalized scale."""
    x = np.asarray(candidates, dtype=float)
    selected = list(selected)
    zs = np.asarray(observed_z, dtype=float)
    if family != 'bma' and family not in MODELS:
        raise ValueError('unsupported family')
    if (not math.isfinite(float(sigma)) or float(sigma) <= 0
            or len(selected) != zs.size or zs.ndim != 1
            or not np.isfinite(zs).all() or not selected
            or any(type(i) not in (int, np.int64) or i < 0 or i >= len(x) for i in selected)
            or len(set(selected)) != len(selected)):
        raise ValueError('invalid observed-only BHS inputs')
    belief = MultivariateBelief(prior_variance=0.5)
    for idx, z in zip(selected, zs):
        belief.observe(x[idx], float(z), float(sigma))
    weights = belief.probabilities()
    used = MODELS if family == 'bma' else (family,)
    result = np.zeros(len(x), dtype=float)
    for mode in used:
        phi = anonymous_features(mode, x)
        st = belief.models[mode]
        mu = phi @ st['mean']
        var_latent = np.einsum('ni,ij,nj->n', phi, st['covariance'], phi)
        sd_latent = np.sqrt(np.maximum(var_latent, 0.))
        w = weights[mode] if family == 'bma' else 1.0
        result += w * expected_improvement(mu, sd_latent, float(np.max(zs)))
    if not np.isfinite(result).all():
        raise ValueError('nonfinite BHS EI')
    return result


def gp_scores_at_lengthscale(candidates, selected, observed_z, lengthscale):
    if not math.isfinite(lengthscale) or lengthscale <= 0:
        raise ValueError('GP lengthscale must be finite positive')
    if lengthscale == GP_LENGTHSCALE_ASSUMED:
        return gp_predict(candidates, selected, observed_z)
    x = np.asarray(candidates, dtype=float)[:, :2]
    kernel = ConstantKernel(1.0, constant_value_bounds='fixed') * RBF(
        length_scale=lengthscale, length_scale_bounds='fixed')
    gp = GaussianProcessRegressor(kernel=kernel, alpha=NOISE_ASSUMED**2,
                                  normalize_y=False, optimizer=None)
    gp.fit(x[list(selected)], observed_z)
    mean, sd = gp.predict(x, return_std=True)
    return mean, sd


def select_ablation(policy, candidates, selected, observed_z, rng):
    """Selection API explicitly has no access to undisclosed labels or optimum."""
    if policy not in POLICIES:
        raise ValueError('unknown ablation policy')
    x = np.asarray(candidates, dtype=float)
    if len(selected) != len(observed_z) or len(set(selected)) != len(selected):
        raise ValueError('selected/observations mismatch')
    if policy in ('random', 'gp_ei', 'gp_ucb', 'bhs_bma_ei'):
        return choose_next_v1(policy, x, selected, observed_z, rng)
    mask = np.ones(len(x), dtype=bool)
    mask[np.asarray(selected, dtype=int)] = False
    remaining = np.flatnonzero(mask)
    if remaining.size == 0:
        raise ValueError('no remaining candidates')
    if policy in BHS_CONFIG:
        family, sigma = BHS_CONFIG[policy]
        acquisition = bhs_ablation_scores(x, selected, observed_z, family, sigma)
    else:
        mean, sd = gp_scores_at_lengthscale(x, selected, observed_z, GP_CONFIG[policy])
        acquisition = expected_improvement(mean, sd, float(np.max(observed_z)))
    if acquisition.shape != (len(x),) or not np.isfinite(acquisition[remaining]).all():
        raise ValueError('nonfinite acquisition')
    return int(remaining[np.argmax(acquisition[remaining])])


def campaign_diagnostic(candidates, hidden_labels, policy, seed, budget=BUDGET):
    """Oracle reveals each label *after* choice; only aggregate metrics returned."""
    validate_dev_protocol((seed,), budget)
    x = np.asarray(candidates, dtype=float)
    y = np.asarray(hidden_labels, dtype=float)
    if (x.ndim != 2 or x.shape[1] != 3 or y.shape != (len(x),)
            or not np.isfinite(x).all() or not np.isfinite(y).all()
            or not np.allclose(x.sum(axis=1), 1., atol=1e-8, rtol=0)
            or np.any(x < 0) or np.any(x > 1)
            or len(x) < budget or policy not in POLICIES):
        raise ValueError('invalid candidate pool / hidden labels')
    r = random.Random(seed)
    selected = r.sample(range(len(x)), INITIAL)
    revealed = [float(y[i]) for i in selected]
    offset, scale = normalize_observed_initial(revealed)
    incumbent_by_budget = {INITIAL: float(np.max(revealed))}
    for step in range(INITIAL + 1, budget + 1):
        observed_z = (np.asarray(revealed, dtype=float) - offset) / scale
        idx = select_ablation(policy, x, selected, observed_z, r)
        if idx in selected:
            raise AssertionError('duplicate selection')
        selected.append(idx)
        revealed.append(float(y[idx]))
        incumbent_by_budget[step] = max(incumbent_by_budget[step-1], revealed[-1])
    width = float(np.ptp(y))
    if width <= 0:
        raise ValueError('cannot evaluate constant-valued target')
    optimum = float(y.max())  # evaluator only; never passed to selection
    regret = {str(b):max(0.,(optimum-incumbent_by_budget[b])/width)
              for b in REPORT_BUDGETS}
    output = {'regret_by_budget':regret, 'acquisitions':len(selected)}
    if policy in BHS_CONFIG:
        family, sigma = BHS_CONFIG[policy]
        belief = MultivariateBelief(prior_variance=0.5)
        for idx, value in zip(selected, revealed):
            belief.observe(x[idx], (value-offset)/scale, sigma)
        probs = belief.probabilities()
        entropy = -sum(p*math.log(p) for p in probs.values() if p > 0)
        output['final_posterior_effective_family_count'] = float(math.exp(entropy))
        if family == 'bma':
            output['final_model_weights'] = probs
    return output


def summarize_paired(results, baseline='gp_ei'):
    """Paired *descriptive* comparisons: no p-values and no new holdout."""
    if baseline not in results:
        raise ValueError('no paired baseline')
    base = results[baseline]
    n = len(base)
    summaries = {}
    for policy in POLICIES:
        rows = results[policy]
        if len(rows) != n:
            raise ValueError('campaigns must be paired')
        by_budget = {}
        for budget in REPORT_BUDGETS:
            key = str(budget)
            z = np.asarray([r['regret_by_budget'][key] for r in rows], dtype=float)
            by_budget[key] = {
                'mean': float(z.mean()), 'median': float(np.median(z)),
                'min': float(z.min()), 'max': float(z.max()),
                'std_population': float(z.std()),
            }
        deltas = np.asarray([r['regret_by_budget']['15'] - br['regret_by_budget']['15']
                             for r, br in zip(rows, base)], dtype=float)
        one = {
            'replicate_count':n, 'normalized_regret_by_budget':by_budget,
            'mean_paired_final_regret_minus_gp_ei': float(deltas.mean()),
            'paired_final_win_tie_loss_vs_gp_ei': {
                'better':int(np.sum(deltas < -1e-10)),
                'tie':int(np.sum(abs(deltas) <= 1e-10)),
                'worse':int(np.sum(deltas > 1e-10))},
        }
        if policy in BHS_CONFIG:
            one['mean_posterior_effective_family_count'] = float(np.mean(
                [r['final_posterior_effective_family_count'] for r in rows]))
            if policy in ('bhs_bma_ei','bhs_bma_sigma_0p05','bhs_bma_sigma_0p30'):
                one['mean_final_model_weights_diagnostic_not_physics'] = {
                    m:float(np.mean([r['final_model_weights'][m] for r in rows])) for m in MODELS}
        summaries[policy] = one
    return summaries


def evaluate_ablation(x, y, seeds=DEV_SEEDS, budget=BUDGET):
    validate_dev_protocol(seeds, budget)
    results = {}
    for policy in POLICIES:
        results[policy] = [campaign_diagnostic(x, y, policy, seed, budget) for seed in seeds]
    return summarize_paired(results)


def run_pinned_bytes(raw):
    source_sha = validate_source(raw)
    arrays = {k:v for k,v in loadmat(io.BytesIO(raw)).items() if not k.startswith('__')}
    x, y, pool = finite_pilot_pool(arrays)
    policy_summaries = evaluate_ablation(x, y)
    reproduction = {}
    for policy, expected in V1_PRIOR_REPORTED_MEAN_REGRET.items():
        observed = float(np.mean([campaign_diagnostic(x, y, policy, s)['regret_by_budget']['15']
                                  for s in (7, 13, 23)]))
        diff = abs(observed - expected)
        reproduction[policy] = {'observed_mean':observed, 'prior_v1_mean':expected,
                                'absolute_error':diff}
        if diff > 1e-9:
            raise ValueError('v1 reference campaign could not be reproduced for '+policy)
    return {
        'status':STATUS, 'target':'Kerr', 'target_units':'mrad',
        'task':'historical retrospective property optimization',
        'source_sha256':source_sha, 'source_column_to_element_order_verified':False,
        'coordinate_names':['source_col_0','source_col_1','source_col_2'],
        'pilot_pool_summary':pool,
        'configuration':{
            'seeds':list(DEV_SEEDS), 'preobserved_v1_development_seeds':[7,13,23],
            'initial_budget':INITIAL, 'total_budget':BUDGET,
            'regret_budget_checkpoints':list(REPORT_BUDGETS),
            'fixed_bhs_prior_parameter_variance':0.5,
            'bhs_nominal_sigma_variants':[0.05,0.15,0.30],
            'gp_fixed_lengthscale_variants':[0.12,0.22,0.40],
            'gp_hyperparameters_tuned':False,
            'measurement_noise_calibrated':False,
            'all_costs_equal_assumption_not_measured':True,
            'diagnostic_families_are_not_chemical_mechanisms':True,
            'candidate_eligibility_based_on_historical_label_availability':True,
        },
        'policies':policy_summaries,
        'prior_v1_reference_reproduction':reproduction,
        'prior_v1_reference_source':{
            'workflow_run_id':41977734103, 'artifact_id':13392975164,
            'reference_seeds':[7,13,23],
            'numbers_are_development_only':True},
        'reported_metrics_are_seed_aggregated_no_raw_rows':True,
        'policy_does_not_receive_unselected_labels':True,
        'development_only':True,
        'post_hoc_model_diagnostics_not_pre_registered':True,
        'independent_holdout_used':False,
        'scored_validation_allowed':False,
        'physical_validation':False,
        'claim_of_superiority':False,
        'real_lab_experiment_executed':False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--fetch',action='store_true')
    ap.add_argument('--out-dir',type=Path,default=Path('runs/nist_diagnostics_ablation_v2'))
    a=ap.parse_args()
    if not a.fetch:
        ap.error('explicit --fetch required: no automatic network or local raw data export')
    report = run_pinned_bytes(fetch_source())
    a.out_dir.mkdir(exist_ok=True,parents=True)
    payload=(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    report_path=a.out_dir/'aggregated_diagnostic_ablation.json'
    report_path.write_bytes(payload)
    (a.out_dir/'aggregated_diagnostic_ablation.sha256').write_text(
        hashlib.sha256(payload).hexdigest()+'  aggregated_diagnostic_ablation.json\n')
    print(json.dumps({
        'status':STATUS, 'eligible_samples':report['pilot_pool_summary']['eligible_samples'],
        'policy_count':len(report['policies']), 'replicate_count':len(DEV_SEEDS),
        'scored_validation_allowed':False, 'development_only':True},sort_keys=True))


if __name__=='__main__':
    main()
