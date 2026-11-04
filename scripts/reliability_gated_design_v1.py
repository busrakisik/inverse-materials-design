"""Development-only reliability-GATED cost-aware hypothesis experiment selection.

Measurement standard deviations are assumed known; audit results are descriptive,
NOT a calibrated reliability certification. Unverified provenance FAILS CLOSED.
This policy does not access private evaluator labels or held-out tasks.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
from pathlib import Path

from scripts.competing_hypotheses_v2 import (Belief, MODELS, fit_belief,
                                               information_gain, validate_public)
from scripts.predictive_calibration_audit_v1 import prequential_audit

STATUS = 'RELIABILITY_GATED_COST_AWARE_HYPOTHESIS_DESIGN_DEVELOPMENT_ONLY'
ALLOWED_PROVENANCE = ('instrument_calibrated_synthetic',)


def positive(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError('expected finite strictly positive quantity')
    return float(value)


def validate_protocol(public, plan):
    """Fail closed unless every experiment declares a calibrated source, cost and std.

    synthetic provenance asserts a development-only convention, not verification
    of an actual device. No confidence is inferred from a user-provided string.
    """
    xs = validate_public(public)
    if type(plan) is not dict or set(plan) != set(xs):
        raise ValueError('metadata must cover exactly the public candidate set')
    sanitized = {}
    for cid in sorted(xs):
        row = plan[cid]
        if type(row) is not dict or set(row) != {'measurement_std', 'cost', 'provenance'}:
            raise ValueError('invalid experiment metadata schema')
        if row['provenance'] not in ALLOWED_PROVENANCE:
            raise ValueError('missing or unapproved measurement provenance')
        sanitized[cid] = {'measurement_std':positive(row['measurement_std']),
                          'cost':positive(row['cost']),
                          'provenance':row['provenance']}
    return xs, sanitized


def validate_history(xs, plan, observations):
    """History rows carry (candidate_id, y, observed_std, provenance).

    A noise parameter may not be silently overwritten by a different planned
    value; this contract currently assumes the declared noise is immutable.
    """
    used, clean = set(), []
    for row in observations:
        if type(row) not in (tuple, list) or len(row) != 4:
            raise ValueError('invalid history row')
        cid, y, std, provenance = row
        if type(cid) is not str or cid not in xs or cid in used:
            raise ValueError('unknown or duplicate observation')
        if type(y) not in (int, float) or not math.isfinite(y):
            raise ValueError('invalid observation value')
        std = positive(std)
        if provenance != plan[cid]['provenance'] or std != plan[cid]['measurement_std']:
            raise ValueError('observed measurement contract disagrees with protocol')
        used.add(cid)
        clean.append((cid, float(y), std))
    return clean, used


class ReliabilityGatedCostPolicyV1:
    """One-step EIG per declared cost. Reliability is a provenance gate, not a bonus.

    `objective='eig'` provides a same-model comparator. The gate does not prove
    the declared measurement std is calibrated. EIG/cost is a heuristic and not
    a generally optimal budgeted experimental design policy.
    """
    def __init__(self, *, objective='eig_per_cost', quantiles=32,
                 prior_parameter_variance=.25):
        if objective not in ('eig_per_cost', 'eig'):
            raise ValueError('unsupported objective')
        if type(quantiles) is not int or not 8 <= quantiles <= 128:
            raise ValueError('invalid quadrature')
        self.objective = objective
        self.quantiles = quantiles
        self.prior_parameter_variance = positive(prior_parameter_variance)
        self.last_diagnostics = None

    def choose(self, public, observations, plan):
        xs, protocol = validate_protocol(public, plan)
        clean, used = validate_history(xs, protocol, observations)
        remaining = sorted(set(xs) - used)
        if not remaining:
            raise ValueError('candidate pool exhausted')
        belief, _, _ = fit_belief(public, clean,
                                 prior_parameter_variance=self.prior_parameter_variance)
        eig = {cid: information_gain(belief, xs[cid],
                                  protocol[cid]['measurement_std'], self.quantiles)
               for cid in remaining}
        utility = {cid: eig[cid]/protocol[cid]['cost'] if self.objective == 'eig_per_cost'
                   else eig[cid] for cid in remaining}
        chosen = min(remaining, key=lambda cid: (-utility[cid], cid))
        self.last_diagnostics = {
            'status': STATUS, 'objective': self.objective, 'chosen': chosen,
            'model_probabilities': dict(zip(MODELS, belief.probabilities())),
            'information_gain_nats': eig, 'selection_score': utility,
            'cost_units_unspecified': True,
            'measurement_std_assumed_calibrated_not_verified': True,
            'reliability_provenance_gate_enforced': True,
            'validated_reliability_detector': False,
            'scientific_optimality_established': False,
            'physical_validation': False, 'scored_validation_allowed': False,
        }
        return chosen


def retrospective_diagnostics(public, observations, plan):
    """Prequential summary computed ONLY from past realized observations.

    Never use these descriptive metrics as a validated accept/reject threshold.
    """
    xs, protocol = validate_protocol(public, plan)
    clean, _ = validate_history(xs, protocol, observations)
    if not clean:
        return None
    audit = prequential_audit(public, clean)
    return {'count': audit['count'],
            'empirical_coverage': audit['empirical_coverage'],
            'nominal_coverage': audit['nominal_coverage'],
            'mean_negative_log_predictive_density': audit['mean_negative_log_predictive_density'],
            'validated_detector': False, 'formal_calibration_established': False}


def development_demo():
    # Fixed public synthetic task; explicitly no benchmark generator/holdout.
    public = {f'dev_{i:02d}': (round(-1+i/6, 6),) for i in range(13)}
    plan = {cid: {'measurement_std':(.10 if i%2 == 0 else .25),
                  'cost':(1.0 if i%3 else 3.0),
                  'provenance':'instrument_calibrated_synthetic'}
            for i, cid in enumerate(public)}
    policy = ReliabilityGatedCostPolicyV1(quantiles=32)
    comparator = ReliabilityGatedCostPolicyV1(objective='eig', quantiles=32)
    rng = random.Random(41)
    history, trace = [], []
    for step in range(5):
        candidate = policy.choose(public, history, plan)
        comparator_candidate = comparator.choose(public, history, plan)
        x = public[candidate][0]
        sigma = plan[candidate]['measurement_std']
        # Hidden generating response is accessed only in trusted demo, AFTER choose.
        y = .8*x*x+rng.gauss(0,sigma)
        trace.append({'step':step+1,'selected':candidate,
                      'eig_only_candidate_same_history':comparator_candidate,
                      'observed_y':y,'declared_std':sigma,
                      'cost':plan[candidate]['cost'],
                      'information_gain_at_choice':policy.last_diagnostics['information_gain_nats'][candidate]})
        history.append((candidate,y,sigma,plan[candidate]['provenance']))
    return {'status':STATUS, 'fixed_synthetic_generating_model':'quadratic amplitude 0.8',
            'trace':trace, 'retrospective_diagnostics':retrospective_diagnostics(public,history,plan),
            'cost_objective_is_heuristic':True,'assumed_measurement_calibration_not_verified':True,
            'independent_holdout_used':False, 'scored_validation_allowed':False}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out-dir',default='runs/reliability_gated_design_v1')
    opts=parser.parse_args()
    result=development_demo()
    out=Path(opts.out_dir)
    out.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    (out/'development_report.json').write_bytes(raw)
    (out/'development_report.sha256').write_text(
        hashlib.sha256(raw).hexdigest()+'  development_report.json\n')
    print(json.dumps({'status':STATUS,'queries':len(result['trace']),
                      'scored_validation_allowed':False},sort_keys=True))

if __name__=='__main__':
    main()
