"""Exploratory synthetic paired pilot. NOT physical validation or preregistered primary test."""
from __future__ import annotations
import argparse, hashlib, json, math, random, statistics, time
from pathlib import Path
from scripts.scientific_benchmark_contract_v1 import make_task, MeteredEvaluator, UniformWithoutReplacement, DescriptorGreedy
from scripts.bayesian_only_policy_v1 import BayesianOnlyPolicyV1

SCENARIOS=('smooth','multimodal','uninformative','mismatched','duplicates')
BUDGETS=(1,2,5,10)
STATUS='SYNTHETIC_ONLY_EXPLORATORY_PILOT_NOT_PHYSICAL_NOT_CONFIRMATORY'

def policy_factory(name,seed):
    if name=='random':return UniformWithoutReplacement(seed)
    if name=='greedy':return DescriptorGreedy()
    if name=='bayesian_only':return BayesianOnlyPolicyV1(seed)
    raise ValueError('unknown policy')

def evaluate(seed,scenario,budget,policy):
    task=make_task(scenario,seed,n=20)
    # Distinct policy random seed; shared scenario task seed for paired comparison.
    policy_seed=int.from_bytes(hashlib.sha256(f'policy:{seed}:{scenario}:{policy}'.encode()).digest()[:8],'big')
    start=time.perf_counter()
    result=MeteredEvaluator(task,budget).run(policy_factory(policy,policy_seed))
    elapsed=time.perf_counter()-start
    trace=result['trace']
    if len(trace)!=budget or len({r['candidate_id'] for r in trace})!=budget:
        raise RuntimeError('query-count/uniqueness mismatch')
    values=[float(r['value']) for r in trace]
    if not all(math.isfinite(v) for v in values):raise RuntimeError('non-finite utility')
    # Evaluator-only oracle access: NEVER passed to policy.
    optimum=max(task._labels.values())
    best=max(values)
    regret=optimum-best
    if regret < -1e-10:raise RuntimeError('negative regret')
    return {'scenario':scenario,'seed':seed,'budget':budget,'policy':policy,'best_utility':best,
            'simple_regret':max(0.0,regret),'queries':len(trace),'wall_seconds':elapsed,
            'task_public_sha256':task.fingerprint(),'trace':trace,'status':STATUS}

def build_pilot(seeds=range(30)):
    seeds=tuple(seeds)
    if not seeds or any(isinstance(s,bool) or not isinstance(s,int) for s in seeds) or len(set(seeds))!=len(seeds):
        raise ValueError('invalid paired seeds')
    rows=[]
    for scenario in SCENARIOS:
        for seed in seeds:
            for budget in BUDGETS:
                for policy in ('random','greedy','bayesian_only'):
                    rows.append(evaluate(seed,scenario,budget,policy))
    return rows

def summarize(rows):
    out=[]
    for scenario in SCENARIOS:
        for budget in BUDGETS:
            subset=[r for r in rows if r['scenario']==scenario and r['budget']==budget]
            by_seed={}
            for r in subset:
                by_seed.setdefault(r['seed'],{})[r['policy']]=r
            if not by_seed or any(set(d)!= {'random','greedy','bayesian_only'} for d in by_seed.values()):
                raise ValueError('unpaired results')
            for policy in ('greedy','bayesian_only'):
                diffs=[d[policy]['best_utility']-d['random']['best_utility'] for _,d in sorted(by_seed.items())]
                out.append({'scenario':scenario,'budget':budget,'comparison':f'{policy}-random',
                            'n_paired':len(diffs),'mean_difference':statistics.mean(diffs),
                            'median_difference':statistics.median(diffs),'status':STATUS})
    return out

def write_outputs(outdir, rows, summary):
    target=Path(outdir);target.mkdir(parents=True,exist_ok=True)
    for name,records in [('pilot_raw.jsonl',rows),('pilot_summary.jsonl',summary)]:
        with (target/name).open('w',encoding='utf-8') as f:
            for record in records:f.write(json.dumps(record,sort_keys=True,allow_nan=False)+'\n')
    manifest={'status':STATUS,'synthetic_only':True,'confirmatory':False,'scenarios':list(SCENARIOS),
              'budgets':list(BUDGETS),'policies':['random','greedy','bayesian_only'],
              'n_rows':len(rows),'n_pairs':len(set(r['seed'] for r in rows)),
              'no_real_labels':True,'interpretation':'Exploratory synthetic pilot; no material discoveries or physical validation.'}
    (target/'pilot_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return manifest

def main():
    p=argparse.ArgumentParser();p.add_argument('--out-dir',default='runs/paired_pilot_v1');p.add_argument('--seeds',type=int,default=30)
    a=p.parse_args()
    if a.seeds<1:raise SystemExit('seeds must be positive')
    rows=build_pilot(range(a.seeds));manifest=write_outputs(a.out_dir,rows,summarize(rows))
    print(json.dumps(manifest,sort_keys=True))
if __name__=='__main__':main()
