"""NIST Kerr exploratory prequential model adequacy on anonymous coordinates.

All forecasts precede acquisition-label reveal. Scoring is adaptive retrospective
DEVELOPMENT on ALREADY-EXPLORED seeds. No independent holdout, no physics claims.
No material rows, revealed labels or chosen indices are written to reports.
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
from scipy.special import ndtr, logsumexp
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF

from scripts.nist_dataset_inspection_v1 import fetch_source, validate_source
from scripts.nist_anonymous_offline_pilot_v1 import (
    INITIAL, BUDGET, NOISE_ASSUMED, GP_LENGTHSCALE_ASSUMED,
    finite_pilot_pool, normalize_observed_initial, choose_next,
)
from scripts.multivariate_hypotheses_v1 import MultivariateBelief, MODELS

STATUS = 'NIST_KERR_PREQUENTIAL_ADEQUACY_DEV_ONLY_NOT_VALIDATED'
DEV_SEEDS = (7, 13, 23, 31, 41)  # ALL ALREADY EXPLORED IN v2
SELECTION_POLICIES = ('random', 'gp_ei', 'bhs_bma_ei')
PREDICTORS = (
    'gp_length_0p22',          # unchanged fixed-parameter v1 reference
    'gp_length_0p40_posthoc',  # post-hoc v2 lengthscale, NOT validated
    'bhs_bma_sigma_0p15',     # unchanged v1 BHS configuration
    'bhs_interaction_sigma_0p15',  # post-hoc v2 response-family ablation
    'bhs_bma_sigma_0p05_posthoc', # post-hoc v2 assumed noise variant
)
PREDICTOR_CFG = {
    'gp_length_0p22': ('gp', 0.22),
    'gp_length_0p40_posthoc': ('gp', 0.40),
    'bhs_bma_sigma_0p15': ('bma', 0.15),
    'bhs_interaction_sigma_0p15': ('fe_co_interaction', 0.15),
    'bhs_bma_sigma_0p05_posthoc': ('bma', 0.05),
}
COVERAGE = 0.90
STD_NOMINAL = NOISE_ASSUMED


def validate_protocol(seeds=DEV_SEEDS, budget=BUDGET):
    if (not isinstance(seeds, (tuple, list)) or not seeds
            or any(type(s) is not int or s < 0 or 10000 <= s <= 10099 for s in seeds)
            or len(seeds) != len(set(seeds)) or type(budget) is not int or budget != 15):
        raise ValueError('invalid protocol or forbidden independent holdout seed')
    return True


def _normal_logpdf(y, mu, var):
    if not all(math.isfinite(float(v)) for v in (y, mu, var)) or var <= 0:
        raise ValueError('invalid predictive normal')
    return -0.5 * (math.log(2 * math.pi * var) + (float(y)-float(mu))**2/var)


def gaussian_mixture(weights, means, variances):
    """Validate and return fixed predictive mixture. All components observational."""
    w = np.asarray(weights, dtype=float)
    mu = np.asarray(means, dtype=float)
    var = np.asarray(variances, dtype=float)
    if (w.ndim != 1 or w.size == 0 or mu.shape != w.shape
            or var.shape != w.shape or not np.isfinite(w).all()
            or not np.isfinite(mu).all() or not np.isfinite(var).all()
            or np.any(w < 0) or np.any(var <= 0)
            or not np.isclose(w.sum(), 1., atol=1e-10, rtol=0)):
        raise ValueError('invalid mixture weights, means, or observation variances')
    return w, mu, var


def mixture_cdf(y, w, mu, var):
    return float(np.sum(w * ndtr((float(y)-mu)/np.sqrt(var))))


def mixture_quantile(p, w, mu, var):
    """Bisection of a Gaussian mixture CDF; never approximate by a Gaussian interval."""
    if not 0. < p < 1.:
        raise ValueError('invalid quantile level')
    sd = np.sqrt(var)
    lo = float(np.min(mu-14.*sd))
    hi = float(np.max(mu+14.*sd))
    for _ in range(52):
        mid = (lo+hi)/2.
        if mixture_cdf(mid, w, mu, var) < p:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2.


def forecast_components(predictor, candidates, selected, observed_z, candidate_index):
    """No oracle, no unobserved outcomes, no scores, no target-dependent tuning."""
    if predictor not in PREDICTORS:
        raise ValueError('unknown diagnostic predictor')
    x = np.asarray(candidates, dtype=float)
    z = np.asarray(observed_z, dtype=float)
    if (x.ndim != 2 or x.shape[1] != 3 or len(selected) < INITIAL
            or z.ndim != 1 or z.size != len(selected) or not np.isfinite(z).all()
            or not np.isfinite(x).all() or np.any(x < 0) or np.any(x > 1)
            or not np.allclose(x.sum(axis=1), 1., atol=1e-8, rtol=0)
            or any(type(i) not in (int,np.int64) or i < 0 or i >= len(x) for i in selected)
            or len(set(selected)) != len(selected)
            or type(candidate_index) not in (int, np.int64)
            or candidate_index < 0 or candidate_index >= len(x)
            or candidate_index in selected):
        raise ValueError('invalid observed-only forecast inputs')
    kind, param = PREDICTOR_CFG[predictor]
    if kind == 'gp':
        kernel = ConstantKernel(1., constant_value_bounds='fixed') * RBF(
            length_scale=param, length_scale_bounds='fixed')
        model = GaussianProcessRegressor(kernel=kernel,
                alpha=STD_NOMINAL**2, normalize_y=False, optimizer=None)
        model.fit(x[np.asarray(selected, dtype=int), :2], z)
        m, std_latent = model.predict(x[candidate_index:candidate_index+1, :2], return_std=True)
        return gaussian_mixture([1.], [float(m[0])], [float(std_latent[0]**2 + STD_NOMINAL**2)])
    belief = MultivariateBelief(prior_variance=0.5)
    for i, response in zip(selected, z):
        belief.observe(x[i], float(response), float(param))
    families = MODELS if kind == 'bma' else (kind,)
    weights = belief.probabilities()
    means, variances = [], []
    for family in families:
        m, v = belief.predictive(family, x[candidate_index], float(param))
        means.append(m)
        variances.append(v)
    return gaussian_mixture([weights[m] if kind == 'bma' else 1. for m in families],
                            means, variances)


def score_observation(y_standardized, w, mu, var):
    """Probability and interval diagnostics, computed from *pre-reveal* mixture."""
    if not math.isfinite(float(y_standardized)):
        raise ValueError('non-finite revealed observation')
    w, mu, var = gaussian_mixture(w, mu, var)
    pred_mean = float(np.sum(w*mu))
    marginal_var = float(np.sum(w*(var+(mu-pred_mean)**2)))
    log_weights = np.array([math.log(float(v)) if v > 0 else -math.inf for v in w])
    log_densities = np.array([_normal_logpdf(y_standardized, m, v)
                              for m, v in zip(mu, var)])
    nlpd = -float(logsumexp(log_weights + log_densities))
    low = mixture_quantile((1.-COVERAGE)/2., w, mu, var)
    high = mixture_quantile((1.+COVERAGE)/2., w, mu, var)
    pit = mixture_cdf(y_standardized, w, mu, var)
    return {'squared_error': float((float(y_standardized)-pred_mean)**2),
            'absolute_error':float(abs(float(y_standardized)-pred_mean)),
            'nlpd':float(nlpd), 'covered_90':bool(low <= y_standardized <= high),
            'interval_width_90':float(high-low),
            'pit':float(pit),
            'outside_two_sd':bool(abs(float(y_standardized)-pred_mean)>2.*math.sqrt(marginal_var))}


def trajectory(candidates, hidden_labels, selection_policy, seed, budget=BUDGET):
    """Only evaluator can reveal labels. Predictor/selector see observed labels only.

    Returns ephemeral per-step diagnostics for *aggregation inside evaluator*.
    Never save or log this return object or its chosen indices/measurements.
    """
    validate_protocol((seed,), budget)
    if selection_policy not in SELECTION_POLICIES:
        raise ValueError('unknown selection policy')
    x = np.asarray(candidates, dtype=float)
    y = np.asarray(hidden_labels, dtype=float)
    if (x.ndim != 2 or x.shape[1] != 3 or y.shape != (len(x),)
            or len(x) < budget or not np.isfinite(x).all() or not np.isfinite(y).all()
            or np.any(x < 0) or np.any(x > 1)
            or not np.allclose(x.sum(axis=1),1.,atol=1e-8,rtol=0)):
        raise ValueError('invalid historical evaluator pool')
    rng = random.Random(seed)
    selected = rng.sample(range(len(x)), INITIAL)
    revealed = [float(y[i]) for i in selected]
    center, scale = normalize_observed_initial(revealed)
    metrics = {pred:[] for pred in PREDICTORS}
    for _ in range(INITIAL, budget):
        z = (np.asarray(revealed, dtype=float)-center)/scale
        idx = choose_next(selection_policy, x, selected, z, rng)
        if idx in selected:
            raise AssertionError('selector proposed a repeat')
        # EVERY predictor forecast happens before the measurement is revealed.
        forecasts = {pred:forecast_components(pred,x,selected,z,idx) for pred in PREDICTORS}
        observed_new = float(y[idx])  # the ONLY per-step label disclosure
        observed_new_z = (observed_new-center)/scale
        for pred, components in forecasts.items():
            metrics[pred].append(score_observation(observed_new_z,*components))
        selected.append(idx)
        revealed.append(observed_new)
    return metrics


def summarize_trajectories(rows):
    """Aggregate same-trajectory predictor scores, paired by seed; no raw rows."""
    if len(rows) == 0:
        raise ValueError('no trajectories')
    result = {}
    reference = 'gp_length_0p22'
    for pred in PREDICTORS:
        per_seed = []
        for seed_metrics in rows:
            seq = seed_metrics[pred]
            if not seq:
                raise ValueError('empty prequential trajectory')
            def avg(key): return float(np.mean([q[key] for q in seq]))
            per_seed.append({'nlpd':avg('nlpd'), 'squared_error':avg('squared_error'),
                             'abs_error':avg('absolute_error'),
                             'coverage':avg('covered_90'),
                             'width':avg('interval_width_90'),
                             'outside_two_sd':avg('outside_two_sd'),
                             'pit_values':[q['pit'] for q in seq]})
        diffs = np.asarray([v['nlpd']-float(np.mean([z['nlpd'] for z in row[reference]]))
                            for v,row in zip(per_seed,rows)], dtype=float)
        pittest = np.asarray([p for v in per_seed for p in v['pit_values']],dtype=float)
        bins = np.histogram(pittest,bins=np.linspace(0,1,6))[0]
        result[pred] = {
            'development_seed_count':len(rows),
            'prequential_forecast_count':int(len(pittest)),
            'mean_nlpd_standardized_response':float(np.mean([v['nlpd'] for v in per_seed])),
            'mean_rmse_standardized_response':float(np.mean([math.sqrt(v['squared_error']) for v in per_seed])),
            'mean_mae_standardized_response':float(np.mean([v['abs_error'] for v in per_seed])),
            'mean_90pct_interval_coverage':float(np.mean([v['coverage'] for v in per_seed])),
            'mean_90pct_interval_width_standardized_response':float(np.mean([v['width'] for v in per_seed])),
            'mean_outside_two_predictive_sd_fraction':float(np.mean([v['outside_two_sd'] for v in per_seed])),
            'pit_bin_counts_5':bins.tolist(),
            'mean_paired_nlpd_minus_gp_length_0p22':float(np.mean(diffs)),
            'paired_nlpd_better_tie_worse_vs_gp_length_0p22':{
                'better':int(np.sum(diffs < -1e-10)),
                'tie':int(np.sum(abs(diffs) <= 1e-10)),
                'worse':int(np.sum(diffs > 1e-10)),
            },
        }
    return result


def evaluate_prequential(x, y, seeds=DEV_SEEDS):
    validate_protocol(seeds)
    return {policy:summarize_trajectories([trajectory(x,y,policy,s) for s in seeds])
            for policy in SELECTION_POLICIES}


def run_pinned_bytes(raw):
    sha=validate_source(raw)
    arrays={k:v for k,v in loadmat(io.BytesIO(raw)).items() if not k.startswith('__')}
    x,y,pool=finite_pilot_pool(arrays)
    results=evaluate_prequential(x,y)
    return {
        'status':STATUS,'source_sha256':sha,'target':'Kerr',
        'unit':'mrad', 'target_transformation':'standardized using initial three observed responses only',
        'pool':pool,'selection_trajectories':results,
        'protocol':{'development_seeds':list(DEV_SEEDS), 'initial_observations':INITIAL,
                    'total_budget':BUDGET,'prequential_forecasts_per_campaign':BUDGET-INITIAL,
                    'selector_policies':list(SELECTION_POLICIES),
                    'forecast_models':list(PREDICTORS),
                    'interval_nominal_coverage':COVERAGE,
                    'gp_default_nominal_noise_std':STD_NOMINAL,
                    'gp_0p40_and_bhs_sigma_0p05_and_single_family_are_posthoc':True,
                    'all_seeds_already_used_in_prior_development':True,
                    'measurements_have_no_verified_per_row_instrument_sigma':True,
                    'prequential_scoring_conditions_on_adaptive_acquisition':True},
        'claim_of_superiority':False,
        'source_element_column_order_verified':False,
        'development_only':True,
        'post_hoc_and_not_pre_registered':True,
        'physical_validation':False,
        'real_lab_experiment_executed':False,
        'independent_holdout_used':False,
        'scored_validation_allowed':False,
        'dataset_ready_for_physical_bhs':False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--fetch',action='store_true')
    ap.add_argument('--out-dir',type=Path,default=Path('runs/nist_model_adequacy_v3'))
    a=ap.parse_args()
    if not a.fetch:
        ap.error('explicit --fetch required: no raw NIST data shipped or logged')
    report=run_pinned_bytes(fetch_source())
    a.out_dir.mkdir(parents=True,exist_ok=True)
    payload=(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n').encode('utf-8')
    filename='aggregated_prequential_adequacy.json'
    (a.out_dir/filename).write_bytes(payload)
    (a.out_dir/'aggregated_prequential_adequacy.sha256').write_text(
        hashlib.sha256(payload).hexdigest()+'  '+filename+'\n')
    print(json.dumps({'status':STATUS,'eligible_samples':report['pool']['eligible_samples'],
                      'selection_trajectories':len(SELECTION_POLICIES),
                      'forecast_models':len(PREDICTORS),
                      'scored_validation_allowed':False,'development_only':True},sort_keys=True))

if __name__=='__main__':
    main()
