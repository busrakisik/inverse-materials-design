"""Post-hoc NIST Kerr prequential miscalibration decomposition (development only).

The original NIST sample labels remain hidden from selector and forecaster until
selection and forecasting are complete. Coordinates are ANONYMOUS; no physical
Fe/Co/Ni attribution, material discovery, or independent holdout is attempted.

This is a descriptive decomposition, NOT causal root-cause identification or a
validated recalibration. Discrepancy-variance additions are hindsight sensitivity
scenarios that must not be selected as a deployment policy using these outcomes.
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

from scripts.nist_dataset_inspection_v1 import fetch_source, validate_source
from scripts.nist_anonymous_offline_pilot_v1 import (
    INITIAL, BUDGET, finite_pilot_pool, normalize_observed_initial, choose_next,
)
from scripts.nist_model_adequacy_v3 import (
    DEV_SEEDS, SELECTION_POLICIES, forecast_components,
    score_observation, validate_protocol, PREDICTOR_CFG,
)

STATUS = 'NIST_KERR_MISCALIBRATION_DECOMPOSITION_POSTHOC_NOT_VALIDATED'
PREDICTORS = ('gp_length_0p22', 'bhs_bma_sigma_0p15',
              'bhs_interaction_sigma_0p15')
DISTANCE_BOUNDS = (0.08, 0.20)  # arbitrary fixed coordinate-distance bins, not physical distances
TIME_SPLIT = 6                 # first 6 versus last 6 prequential forecasts
EXTRA_DISCREPANCY_SD = (0.0, 0.5, 1.0, 2.0)  # hypothetical standardized units; NO FITTING
V3_RUN_ID = 41992614426
V3_ARTIFACT_ID = 13397919991
# Frozen values independently extracted from the completed v3 CI artifact.
# They are ONLY regression/parity checks, NEVER a new holdout or fitting target.
V3_PARITY = {
    'random': {
        'gp_length_0p22': (57.62850656054312, 0.4333333333333333),
        'bhs_bma_sigma_0p15': (242.95496540970558, 0.2833333333333333),
        'bhs_interaction_sigma_0p15': (237.85272015355213, 0.2833333333333333),
    },
    'gp_ei': {
        'gp_length_0p22': (47.56135897837278, 0.4333333333333333),
        'bhs_bma_sigma_0p15': (232.04785248383763, 0.16666666666666669),
        'bhs_interaction_sigma_0p15': (231.62864121909152, 0.18333333333333332),
    },
    'bhs_bma_ei': {
        'gp_length_0p22': (14.577593840089719, 0.4833333333333333),
        'bhs_bma_sigma_0p15': (67.78601055269294, 0.33333333333333337),
        'bhs_interaction_sigma_0p15': (88.7260891034517, 0.3166666666666667),
    },
}


def predictive_variance_components(predictor, weights, means, variances):
    """Total variance = nominal noise + within + between mixture components.

    GP is a one-component normal; its `within` is latent conditional GP
    variance. For BHS, within is weighted parameter-posterior variance.
    The between term measures disagreement between *chosen functional forms*,
    not physical scientific mechanisms.
    """
    if predictor not in PREDICTORS:
        raise ValueError('unsupported predictor')
    w = np.asarray(weights, dtype=float)
    mu = np.asarray(means, dtype=float)
    var = np.asarray(variances, dtype=float)
    if (w.ndim != 1 or w.size == 0 or mu.shape != w.shape or var.shape != w.shape
            or not np.isfinite(w).all() or not np.isfinite(mu).all()
            or not np.isfinite(var).all() or np.any(w < 0.)
            or not np.isclose(w.sum(), 1., atol=1e-10, rtol=0)
            or np.any(var <= 0.)):
        raise ValueError('invalid predictive mixture')
    _, assumed_sigma = PREDICTOR_CFG[predictor]
    sigma = 0.15 if predictor.startswith('gp_') else float(assumed_sigma)
    noise_var = sigma ** 2
    if np.any(var < noise_var - 1e-10):
        raise ValueError('predictive variance below nominal observation noise')
    center = float(np.sum(w * mu))
    within = float(np.sum(w * np.maximum(0., var - noise_var)))
    between = float(np.sum(w * (mu - center) ** 2))
    total = noise_var + within + between
    direct = float(np.sum(w * (var + (mu - center) ** 2)))
    if not (math.isfinite(total) and total > 0 and abs(total - direct) < 1e-8):
        raise ValueError('variance decomposition discrepancy')
    return {'predictive_mean': center, 'assumed_noise_variance': noise_var,
            'within_family_variance': within, 'between_family_variance': between,
            'total_predictive_variance': total}


def candidate_novelty(candidates, selected, new_index):
    """Distance in anonymous 3-coordinate simplex; uses NO observed targets."""
    x = np.asarray(candidates, dtype=float)
    if (x.ndim != 2 or x.shape[1] != 3 or not np.isfinite(x).all()
            or not selected or new_index in selected or new_index < 0
            or new_index >= len(x) or any(i < 0 or i >= len(x) for i in selected)):
        raise ValueError('invalid candidate novelty query')
    return float(np.min(np.linalg.norm(x[np.asarray(selected, dtype=int)] - x[new_index], axis=1)))


def distance_category(distance):
    if not math.isfinite(float(distance)) or distance < 0:
        raise ValueError('nonfinite or negative coordinate distance')
    if distance < DISTANCE_BOUNDS[0]:
        return 'near'
    if distance < DISTANCE_BOUNDS[1]:
        return 'middle'
    return 'far'


def diagnose_after_reveal(predictor, observed_z, components, nearest_distance, forecast_ordinal):
    """Called ONLY after a previously unobserved target is revealed.

    This function is not called by the selector, nor by forecast_components.
    """
    if (predictor not in PREDICTORS or type(forecast_ordinal) is not int
            or forecast_ordinal < 1 or forecast_ordinal > BUDGET-INITIAL):
        raise ValueError('invalid diagnostic timing/predictor')
    w, mu, var = components
    parts = predictive_variance_components(predictor, w, mu, var)
    original = score_observation(float(observed_z), w, mu, var)
    residual = float(observed_z - parts['predictive_mean'])
    total = parts['total_predictive_variance']
    sd_sensitivity = {}
    for s in EXTRA_DISCREPANCY_SD:
        altered = score_observation(float(observed_z), w, mu, np.asarray(var, dtype=float) + s*s)
        sd_sensitivity[str(s)] = {'covered_90':altered['covered_90'],
                                  'nlpd':altered['nlpd'],
                                  'width_90':altered['interval_width_90']}
    return {
        'residual': residual, 'squared_error': residual**2,
        'squared_standardized_error': residual**2 / total,
        'nlpd': original['nlpd'], 'covered_90':original['covered_90'],
        'interval_width_90':original['interval_width_90'],
        'assumed_noise_variance':parts['assumed_noise_variance'],
        'within_family_variance':parts['within_family_variance'],
        'between_family_variance':parts['between_family_variance'],
        'total_predictive_variance':total,
        'distance_category':distance_category(nearest_distance),
        'time_category':'early' if forecast_ordinal <= TIME_SPLIT else 'late',
        'discrepancy_sensitivity':sd_sensitivity,
    }


def run_trajectory(candidates, hidden_labels, selection_policy, seed):
    """One retrospective adaptive development campaign, ephemeral diagnostics.

    Do not serialize this function's output. It contains prequential residuals.
    Only summarize_all() may emit aggregate-only results to a report.
    """
    validate_protocol((seed,), BUDGET)
    if selection_policy not in SELECTION_POLICIES:
        raise ValueError('unknown selection policy')
    x = np.asarray(candidates, dtype=float)
    y = np.asarray(hidden_labels, dtype=float)
    if (x.ndim != 2 or x.shape[1] != 3 or y.shape != (len(x),)
            or len(x) < BUDGET or not np.isfinite(x).all() or not np.isfinite(y).all()
            or np.any(x < 0) or np.any(x > 1)
            or not np.allclose(x.sum(axis=1), 1., atol=1e-8, rtol=0)):
        raise ValueError('invalid evaluator candidate pool')
    rng = random.Random(seed)
    selected = rng.sample(range(len(x)), INITIAL)
    revealed = [float(y[i]) for i in selected]
    center, scale = normalize_observed_initial(revealed)
    outcomes = {p:[] for p in PREDICTORS}
    for ordinal in range(1, BUDGET - INITIAL + 1):
        z = (np.asarray(revealed, dtype=float) - center) / scale
        idx = choose_next(selection_policy, x, selected, z, rng)
        if idx in selected:
            raise ValueError('duplicate acquisition')
        novelty = candidate_novelty(x, selected, idx)
        pre_reveal = {p:forecast_components(p, x, selected, z, idx) for p in PREDICTORS}
        observed_z = (float(y[idx]) - center) / scale  # FIRST disclosure of this label
        for predictor, components in pre_reveal.items():
            outcomes[predictor].append(diagnose_after_reveal(
                predictor, observed_z, components, novelty, ordinal))
        selected.append(idx)
        revealed.append(float(y[idx]))
    return outcomes


def _aggregate(records):
    """Aggregate; do not expose per-sample or per-trajectory diagnostic rows."""
    if not records:
        return {'count':0,'mean_signed_residual':None,'mean_90pct_coverage':None,
                'mean_squared_standardized_error':None,'mean_total_variance':None}
    def mean(field): return float(np.mean([r[field] for r in records]))
    return {'count':len(records), 'mean_signed_residual':mean('residual'),
            'mean_90pct_coverage':mean('covered_90'),
            'mean_squared_standardized_error':mean('squared_standardized_error'),
            'mean_squared_error':mean('squared_error'),
            'mean_total_variance':mean('total_predictive_variance'),
            'mean_nlpd':mean('nlpd')}


def summarize_all(traces_by_policy):
    """Only aggregate outputs, never selected indices or individual observations."""
    result={}
    for policy, seed_traces in traces_by_policy.items():
        if not seed_traces:
            raise ValueError('no development trajectories')
        policy_summaries={}
        for predictor in PREDICTORS:
            flat=[r for t in seed_traces for r in t[predictor]]
            if len(flat)!=len(seed_traces)*(BUDGET-INITIAL):
                raise ValueError('incomplete forecast count')
            s=_aggregate(flat)
            s.update({
                'development_seed_count':len(seed_traces),
                'mean_assumed_noise_variance':float(np.mean([r['assumed_noise_variance'] for r in flat])),
                'mean_within_family_variance':float(np.mean([r['within_family_variance'] for r in flat])),
                'mean_between_family_variance':float(np.mean([r['between_family_variance'] for r in flat])),
                'empirical_mse_to_mean_predicted_variance_ratio':float(np.mean([r['squared_error'] for r in flat])/np.mean([r['total_predictive_variance'] for r in flat])),
                'by_nearest_coordinate_distance':{g:_aggregate([r for r in flat if r['distance_category']==g]) for g in ('near','middle','far')},
                'by_acquisition_phase':{g:_aggregate([r for r in flat if r['time_category']==g]) for g in ('early','late')},
                'posthoc_additive_discrepancy_sd_sensitivity':{
                    str(sd):{
                        'mean_90pct_coverage':float(np.mean([r['discrepancy_sensitivity'][str(sd)]['covered_90'] for r in flat])),
                        'mean_nlpd':float(np.mean([r['discrepancy_sensitivity'][str(sd)]['nlpd'] for r in flat])),
                        'mean_interval_width':float(np.mean([r['discrepancy_sensitivity'][str(sd)]['width_90'] for r in flat])),
                    } for sd in EXTRA_DISCREPANCY_SD},
            })
            policy_summaries[predictor]=s
        result[policy]=policy_summaries
    return result


def verify_v3_reproduction(report, tolerance=1e-7):
    """Fail if unchanged v3 forecast NLPD/coverage fails to reproduce."""
    for policy, pairs in V3_PARITY.items():
        for predictor, (nlpd, coverage) in pairs.items():
            actual=report['selection_trajectories'][policy][predictor]
            if (abs(actual['mean_nlpd']-nlpd)>tolerance or
                    abs(actual['mean_90pct_coverage']-coverage)>tolerance):
                raise ValueError('v3 aggregate parity failed: '+policy+'/'+predictor)
    return True


def evaluate_development(x,y,seeds=DEV_SEEDS):
    validate_protocol(seeds, BUDGET)
    traces = {p:[run_trajectory(x,y,p,s) for s in seeds] for p in SELECTION_POLICIES}
    return summarize_all(traces)


def run_pinned_bytes(raw):
    sha=validate_source(raw)
    arrays={k:v for k,v in loadmat(io.BytesIO(raw)).items() if not k.startswith('__')}
    x,y,pool=finite_pilot_pool(arrays)
    report={
        'status':STATUS, 'target':'Kerr', 'unit':'mrad',
        'source_sha256':sha, 'pool':pool,
        'selection_trajectories':evaluate_development(x,y),
        'protocol':{
            'seeds':list(DEV_SEEDS), 'selection_policies':list(SELECTION_POLICIES),
            'predictors':list(PREDICTORS),'initial_observations':INITIAL,
            'total_budget':BUDGET, 'prequential_forecasts_per_campaign':BUDGET-INITIAL,
            'distance_bins_anonymous_coordinate_units':{'near_less_than':DISTANCE_BOUNDS[0],
                                                         'middle_less_than':DISTANCE_BOUNDS[1]},
            'early_forecasts':TIME_SPLIT,
            'hypothetical_additional_discrepancy_sd':list(EXTRA_DISCREPANCY_SD),
            'all_seeds_previously_used_for_development':True,
            'predictive_variance_decomposition_not_identification_of_error_cause':True,
            'sensitivity_scenarios_posthoc_not_deployment_calibration':True,
            'nominal_sigmas_not_instrument_measured':True,
            'physical_element_order_unverified':True,
        },
        'prior_v3_reference':{'run_id':V3_RUN_ID,'artifact_id':V3_ARTIFACT_ID,
                              'frozen_reference_metrics_are_development_only':True},
        'source_column_to_element_order_verified':False,
        'post_hoc_and_not_pre_registered':True,
        'development_only':True,
        'real_lab_experiment_executed':False,
        'independent_holdout_used':False,
        'scored_validation_allowed':False,
        'physical_validation':False,
        'claim_of_superiority':False,
    }
    verify_v3_reproduction(report)
    return report


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--fetch',action='store_true')
    ap.add_argument('--out-dir',type=Path,default=Path('runs/nist_miscalibration_rootcause_v4'))
    a=ap.parse_args()
    if not a.fetch:
        ap.error('explicit --fetch required; no raw NIST source/labels in artifacts')
    report=run_pinned_bytes(fetch_source())
    a.out_dir.mkdir(parents=True,exist_ok=True)
    name='aggregated_rootcause_diagnostics.json'
    payload=(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    (a.out_dir/name).write_bytes(payload)
    (a.out_dir/'aggregated_rootcause_diagnostics.sha256').write_text(
        hashlib.sha256(payload).hexdigest()+'  '+name+'\n')
    print(json.dumps({'status':STATUS, 'eligible_samples':report['pool']['eligible_samples'],
                      'selector_count':len(SELECTION_POLICIES),'predictor_count':len(PREDICTORS),
                      'development_only':True,'scored_validation_allowed':False},sort_keys=True))

if __name__=='__main__':main()
