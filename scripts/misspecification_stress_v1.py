"""Transparent synthetic stress diagnostics for the BHS prequential model.

DEVELOPMENT ONLY. No independent holdout, material measurements or formal detector.
The assumed observation std is supplied to the model; actual synthetic noise may
intentionally differ. No post-hoc calibration thresholds are inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

from scripts.predictive_calibration_audit_v1 import prequential_audit

STATUS = 'SYNTHETIC_MODEL_MISSPECIFICATION_STRESS_EXPLORATORY_NO_HOLDOUT'
SCENARIOS = ('in_family', 'underreported_noise', 'systematic_bias',
             'gradual_drift', 'out_of_family_step', 'heavy_tailed_noise')
N = 24
DECLARED_STD = 0.12
# The fixed local generator is not the benchmark's make_task and does not use
# proposed independent holdout task seed IDs 10000..10099.
DEVELOPMENT_RNG = 41


def validate_scenarios(scenarios):
    if type(scenarios) not in (tuple, list) or not scenarios or len(scenarios) != len(set(scenarios)):
        raise ValueError('invalid scenarios')
    if any(type(s) is not str or s not in SCENARIOS for s in scenarios):
        raise ValueError('unknown scenario')
    return tuple(scenarios)


def make_fixed_stress_streams(scenarios=SCENARIOS):
    """Deterministic illustrative *developer* streams, not benchmark tasks.

    Exactly the same public candidate order is shared across mechanisms.
    Separate seeded noise streams prevent adaptive tuning or hidden task access.
    """
    scenarios = validate_scenarios(scenarios)
    xs = [round(-0.96 + i * (1.92 / (N - 1)), 8) for i in range(N)]
    public = {f'dev_{i:02d}': (x,) for i, x in enumerate(xs)}
    result = {}
    for scenario in scenarios:
        rng = random.Random('BHS-misspec-dev-v1:' + scenario + ':' + str(DEVELOPMENT_RNG))
        stream = []
        for i, x in enumerate(xs):
            baseline = 0.8*x*x
            if scenario == 'in_family':
                y = baseline + rng.gauss(0, DECLARED_STD)
            elif scenario == 'underreported_noise':
                y = baseline + rng.gauss(0, DECLARED_STD*3)
            elif scenario == 'systematic_bias':
                y = baseline + 0.65 + rng.gauss(0, DECLARED_STD)
            elif scenario == 'gradual_drift':
                y = baseline + 0.8*i/(N-1) + rng.gauss(0, DECLARED_STD)
            elif scenario == 'out_of_family_step':
                y = (1.0 if x >= 0 else -1.0) + rng.gauss(0, DECLARED_STD)
            else:
                # Fixed scale-mixture contamination: 1 out of 6 observations
                # receives larger Gaussian noise, not a claimed Student-t law.
                sigma = DECLARED_STD*6 if i % 6 == 0 else DECLARED_STD
                y = baseline + rng.gauss(0, sigma)
            stream.append((f'dev_{i:02d}', y, DECLARED_STD))
        result[scenario] = tuple(stream)
    return public, result


def summarize_records(audit):
    records = audit['records']
    if not records or audit['count'] != len(records):
        raise ValueError('invalid prequential records')
    n = len(records)
    covered = [int(row['covered']) for row in records]
    scores = [row['negative_log_predictive_density'] for row in records]
    pits = [row['pit'] for row in records]
    if not all(math.isfinite(v) for v in scores+pits):
        raise ValueError('nonfinite diagnostics')
    half = n//2
    return {
        'count': n,
        'nominal_coverage': audit['nominal_coverage'],
        'empirical_coverage': sum(covered)/n,
        'coverage_gap': sum(covered)/n - audit['nominal_coverage'],
        'mean_negative_log_predictive_density': sum(scores)/n,
        'mean_pit': sum(pits)/n,
        'extreme_pit_fraction': sum(p < .05 or p > .95 for p in pits)/n,
        'first_half_coverage': sum(covered[:half])/half,
        'second_half_coverage': sum(covered[half:])/(n-half),
        'first_half_mean_log_score': sum(scores[:half])/half,
        'second_half_mean_log_score': sum(scores[half:])/(n-half),
        'final_max_model_probability': audit['final_max_model_probability'],
    }


def run_stress(scenarios=SCENARIOS):
    scenarios = validate_scenarios(scenarios)
    public, streams = make_fixed_stress_streams(scenarios)
    summaries = {}
    for scenario in scenarios:
        audited = prequential_audit(public, streams[scenario], level=.90)
        summaries[scenario] = summarize_records(audited)
    return {
        'status': STATUS,
        'scenarios': summaries,
        'n_scenarios': len(summaries),
        'observations_per_scenario': N,
        'declared_observation_std': DECLARED_STD,
        'generating_mechanisms_are_developer_chosen': True,
        'predict_before_update': True,
        'formal_out_of_family_detector': False,
        'calibration_certified': False,
        'statistical_significance_test_performed': False,
        'automatic_warning_thresholds_enabled': False,
        'material_measurements_used': False,
        'benchmark_task_generator_called': False,
        'independent_holdout_used': False,
        'scored_validation_allowed': False,
        'interpretation': 'Descriptive, fixed synthetic stress examples; not sensitivity/specificity evidence.'
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', default='runs/misspecification_stress_v1')
    args = parser.parse_args()
    result = run_stress()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')
    (out/'stress_report.json').write_bytes(raw)
    (out/'stress_report.sha256').write_text(hashlib.sha256(raw).hexdigest()+'  stress_report.json\n', encoding='utf-8')
    print(json.dumps({'status': STATUS, 'scenarios': result['n_scenarios'],
                      'observations_total': N*len(result['scenarios']),
                      'scored_validation_allowed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
