"""Paired, fixed DEVELOPMENT-only cost-budget model-identification comparisons.

No private benchmark oracle, no holdout, no material validation. Deterministic
candidate-level outcomes are generated ONCE by a trusted local simulator and
only exposed to each policy after that candidate is selected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

from scripts.competing_hypotheses_v2 import MODELS, basis, fit_belief, information_gain
from scripts.reliability_gated_design_v1 import ReliabilityGatedCostPolicyV1

STATUS = 'BHS_PAIRED_RESEARCH_TO_VALUE_DEVELOPMENT_ONLY'
VARIANTS = ('random', 'cheapest', 'eig', 'eig_per_cost')
COST_PROFILES = ('flat', 'heterogeneous')
NOISE_PROFILES = ('low', 'moderate')
TRUE_MODELS = MODELS
BUDGET = 8.0
N_CANDIDATES = 13
REPEATS = (0, 1)


def task(model, costs, noise, repeat):
    if model not in TRUE_MODELS or costs not in COST_PROFILES or noise not in NOISE_PROFILES or type(repeat) is not int or repeat not in REPEATS:
        raise ValueError('only the fixed published development grid is permitted')
    public = {f'candidate_{i:02d}': (round(-1+i/6, 6),) for i in range(N_CANDIDATES)}
    plan = {}
    for i, cid in enumerate(public):
        plan[cid] = {
            'measurement_std': (.12 if noise == 'low' else .24) * (1 if i%2 == 0 else 1.2),
            'cost': 1.0 if costs == 'flat' else (1.0 if i%3 != 0 else 3.0),
            'provenance': 'instrument_calibrated_synthetic',
        }
    # IMPORTANT: a common candidate-specific noisy observation across variants;
    # not sequential global RNG calls depending on policy choices.
    outcome = {}
    for cid, desc in public.items():
        material = f'BHS-development-grid-v1:{model}:{costs}:{noise}:{repeat}:{cid}'
        key = int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], 'big')
        rng = random.Random(key)
        outcome[cid] = .8*basis(model, desc[0]) + rng.gauss(0, plan[cid]['measurement_std'])
    return public, plan, outcome


def policy_action(variant, public, plan, history, affordable, *, key):
    if variant not in VARIANTS or not affordable:
        raise ValueError('unknown policy or no available action')
    if variant == 'random':
        # Each selection is generated from a deterministic policy state, not outcome.
        material = repr((key, tuple(cid for cid, _, _, _ in history)))
        seed = int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], 'big')
        return random.Random(seed).choice(sorted(affordable))
    if variant == 'cheapest':
        return min(affordable, key=lambda cid: (plan[cid]['cost'], cid))
    # Rank only affordable actions. Existing policy produces EIG scores for all
    # available actions, so the feasible top-ranking action is chosen here.
    selector = ReliabilityGatedCostPolicyV1(objective=variant, quantiles=16)
    selector.choose(public, history, plan)
    scores = selector.last_diagnostics['selection_score']
    return min(affordable, key=lambda cid: (-scores[cid], cid))


def run_one(model, costs, noise, repeat, variant):
    if variant not in VARIANTS:
        raise ValueError('unknown variant')
    public, plan, trusted_outcomes = task(model, costs, noise, repeat)
    budget_remaining = BUDGET
    history, ids = [], []
    for _ in range(N_CANDIDATES):
        seen = {cid for cid, _, _, _ in history}
        affordable = [cid for cid in sorted(public) if cid not in seen and plan[cid]['cost'] <= budget_remaining + 1e-10]
        if not affordable:
            break
        selected = policy_action(variant, public, plan, history, affordable, key=(model,costs,noise,repeat,variant))
        if selected not in affordable:
            raise RuntimeError('policy selected infeasible action')
        budget_remaining -= plan[selected]['cost']
        ids.append(selected)
        # Trusted local experiment simulator reveals exactly one outcome here.
        history.append((selected, trusted_outcomes[selected], plan[selected]['measurement_std'], plan[selected]['provenance']))
    clean = [(cid, y, std) for cid,y,std,_ in history]
    posterior, _, _ = fit_belief(public, clean)
    p_true = posterior.probabilities()[MODELS.index(model)]
    # Safe log score; zero underflow is possible but not expected on fixed grid.
    logloss = -math.log(max(p_true, 1e-300))
    spent = BUDGET - budget_remaining
    if spent > BUDGET + 1e-10 or len(ids) != len(set(ids)):
        raise RuntimeError('budget or distinct-candidate invariant failed')
    return {'status':STATUS, 'true_model':model, 'cost_profile':costs,
            'noise_profile':noise, 'development_repeat':repeat, 'variant':variant,
            'budget_units':BUDGET, 'spent_units':round(spent, 9), 'n_observations':len(ids),
            'selected_ids':ids, 'true_model_probability':p_true,
            'true_model_log_loss':logloss, 'posterior_entropy_nats':posterior.entropy(),
            'scored_validation_allowed':False, 'independent_holdout_used':False,
            'real_materials_used':False}


def run_grid():
    rows = [run_one(model, cost, noise, rep, variant)
            for model in TRUE_MODELS for cost in COST_PROFILES
            for noise in NOISE_PROFILES for rep in REPEATS for variant in VARIANTS]
    groups = {}
    for row in rows:
        key = (row['true_model'],row['cost_profile'],row['noise_profile'],row['development_repeat'])
        groups.setdefault(key,{})[row['variant']] = row
    assert len(groups) == len(TRUE_MODELS)*len(COST_PROFILES)*len(NOISE_PROFILES)*len(REPEATS)
    if any(set(g) != set(VARIANTS) for g in groups.values()):
        raise RuntimeError('incomplete paired comparison')
    paired = []
    for key,g in sorted(groups.items()):
        baseline = g['eig']
        for variant in ('random','cheapest','eig_per_cost'):
            row = g[variant]
            paired.append({'true_model':key[0], 'cost_profile':key[1],
                           'noise_profile':key[2], 'development_repeat':key[3],
                           'variant':variant, 'comparator':'eig',
                           'log_loss_difference_vs_eig':row['true_model_log_loss']-baseline['true_model_log_loss'],
                           'spend_difference_vs_eig':row['spent_units']-baseline['spent_units'],
                           'query_difference_vs_eig':row['n_observations']-baseline['n_observations'],
                           'scored_validation_allowed':False})
    summary=[]
    for variant in VARIANTS:
        entries=[r for r in rows if r['variant']==variant]
        summary.append({'variant':variant,'n_development_cases':len(entries),
                        'mean_true_model_log_loss':sum(r['true_model_log_loss'] for r in entries)/len(entries),
                        'mean_spent_units':sum(r['spent_units'] for r in entries)/len(entries),
                        'mean_observations':sum(r['n_observations'] for r in entries)/len(entries),
                        'descriptive_only':True})
    return {'manifest':{'status':STATUS,'fixed_development_cases':len(groups),'policy_variants':list(VARIANTS),
                        'n_rows':len(rows),'n_paired_comparisons':len(paired),
                        'spent_budget_cap':BUDGET,'outcome_coupling':'fixed candidate-specific outcomes',
                        'hypothesis_identification_not_material_utility':True,
                        'post_selection_development_not_independent':True,
                        'scored_validation_allowed':False, 'independent_holdout_used':False,
                        'claim_of_superiority':False},'rows':rows,'paired':paired,'summary':summary}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out-dir',default='runs/bhs_research_to_value_v1')
    args=parser.parse_args()
    result=run_grid()
    path=Path(args.out_dir)
    path.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    (path/'development_comparison.json').write_bytes(raw)
    (path/'development_comparison.sha256').write_text(hashlib.sha256(raw).hexdigest()+'  development_comparison.json\n')
    print(json.dumps(result['manifest'],sort_keys=True))


if __name__ == '__main__':main()
