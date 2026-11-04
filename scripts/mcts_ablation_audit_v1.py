"""Audit the pinned, already-executed MCTS development artifact; never generate tasks.

Evidence: GitHub Actions run 41810700077, artifact 13312032670.
Exploratory, pilot-informed results only. No holdout or real material evaluations.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import zipfile

ARTIFACT_ID = 13312032670
PINNED_ARCHIVE_SHA256 = '1fac21e3768e183ab702766d6f7fe05d9425a4248840d7ecb9b604488c4bf26c'
PREFIX = 'runs/mcts_development_benchmark_v1/'
SCENARIOS = ('smooth','multimodal','uninformative','mismatched','duplicates')
BUDGETS = (1,5,10)
VARIANTS = ('random','greedy','bayesian_only','mcts_32_h1','mcts_32_h3','mcts_96_h3')
SEEDS = tuple(range(5))
STATUS = 'MCTS_EXISTING_DEVELOPMENT_ABLATION_AUDITED_NOT_CONFIRMATORY'
MAX_ARCHIVE = 2_000_000
MAX_MEMBER = 2_000_000


def sha256(blob):
    return hashlib.sha256(blob).hexdigest()


def unpack_pinned_archive(blob):
    if not isinstance(blob, bytes) or len(blob)>MAX_ARCHIVE or sha256(blob)!=PINNED_ARCHIVE_SHA256:
        raise ValueError('unexpected artifact bytes or sha256 mismatch')
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        entries = z.infolist()
        names = [i.filename for i in entries]
        if len(entries)>30 or len(set(names))!=len(names):
            raise ValueError('ambiguous archive entries')
        for i in entries:
            if i.flag_bits & 1 or i.file_size>MAX_MEMBER or i.filename.startswith('/') or '..' in Path(i.filename).parts:
                raise ValueError('unsafe archive entry')
        expected = [PREFIX+'development_raw.jsonl', PREFIX+'development_manifest.json',
                    PREFIX+'development_manifest.sha256']
        if any(name not in names for name in expected):
            raise ValueError('missing expected artifact member')
        manifest_bytes = z.read(expected[1])
        sha_text = z.read(expected[2]).decode('utf-8').strip().split()
        if len(sha_text)!=2 or sha_text != [sha256(manifest_bytes), 'development_manifest.json']:
            raise ValueError('artifact manifest SHA mismatch')
        manifest = json.loads(manifest_bytes)
        rows = [json.loads(line) for line in z.read(expected[0]).splitlines() if line.strip()]
    return manifest,rows


def validate_rows(manifest, rows):
    if manifest.get('development_seeds')!=list(SEEDS) or manifest.get('variants')!=list(VARIANTS):
        raise ValueError('manifest configuration mismatch')
    if manifest.get('scenarios')!=list(SCENARIOS) or manifest.get('budgets')!=list(BUDGETS):
        raise ValueError('unexpected scenarios or budgets')
    if (manifest.get('confirmatory') is not False or manifest.get('pilot_informed') is not True or
        manifest.get('synthetic_only') is not True or manifest.get('scored_validation_allowed') is not False or
        manifest.get('n_rows')!=450 or len(rows)!=450):
        raise ValueError('invalid exploratory contract or row count')
    grouped=defaultdict(dict)
    for r in rows:
        if not isinstance(r,dict) or r.get('status')!='EXPLORATORY_DEVELOPMENT_MCTS_COMPARISON_NO_HOLDOUT':
            raise ValueError('invalid row status')
        scenario,seed,budget,variant=(r.get(k) for k in ('scenario','seed','budget','variant'))
        if scenario not in SCENARIOS or type(seed) is not int or seed not in SEEDS or type(budget) is not int or budget not in BUDGETS or variant not in VARIANTS:
            raise ValueError('unexpected task or policy')
        if r.get('scored_validation_allowed') is not False or type(r.get('queries')) is not int or r['queries']!=budget:
            raise ValueError('unexpected validation flag or query budget')
        if any(type(r.get(k)) not in (int,float) or not math.isfinite(r[k]) for k in ('best_utility','simple_regret','wall_seconds')):
            raise ValueError('missing or nonfinite metric')
        if r['simple_regret']<0 or r['wall_seconds']<0:
            raise ValueError('negative regret or duration')
        ids=r.get('selected_ids')
        if not isinstance(ids,list) or len(ids)!=budget or any(type(i) is not str for i in ids) or len(set(ids))!=budget:
            raise ValueError('invalid selected candidate IDs')
        taskhash=r.get('task_public_sha256')
        if type(taskhash) is not str or len(taskhash)!=64 or any(c not in '0123456789abcdef' for c in taskhash):
            raise ValueError('invalid task digest')
        key=(scenario,seed,budget)
        if variant in grouped[key]:
            raise ValueError('duplicate task-policy pair')
        grouped[key][variant]=r
    if len(grouped)!=len(SCENARIOS)*len(SEEDS)*len(BUDGETS):
        raise ValueError('incomplete task grid')
    for pair in grouped.values():
        if set(pair)!=set(VARIANTS) or len({r['task_public_sha256'] for r in pair.values()})!=1:
            raise ValueError('unpaired or mismatched task fingerprints')
    return grouped


def paired_analysis(grouped):
    contrasts=[('mcts_32_h3','bayesian_only','PUCT-versus-Bayesian'),
               ('mcts_32_h3','greedy','PUCT-versus-Greedy'),
               ('mcts_32_h3','mcts_32_h1','horizon-ablation-same-simulations'),
               ('mcts_96_h3','mcts_32_h3','simulation-ablation-same-horizon'),
               ('mcts_96_h3','bayesian_only','96-versus-Bayesian'),
               ('mcts_96_h3','greedy','96-versus-Greedy')]
    report=[]
    for scenario in SCENARIOS:
        for budget in BUDGETS:
            groups=[grouped[(scenario,seed,budget)] for seed in SEEDS]
            for a,b,label in contrasts:
                diffs=[pair[a]['best_utility']-pair[b]['best_utility'] for pair in groups]
                ta=[pair[a]['wall_seconds'] for pair in groups]
                tb=[pair[b]['wall_seconds'] for pair in groups]
                report.append({'scenario':scenario,'budget':budget,'contrast':label,
                     'variant':a,'comparator':b,'n_paired':len(diffs),
                     'mean_difference':statistics.mean(diffs),
                     'median_difference':statistics.median(diffs),
                     'wins':sum(d>1e-12 for d in diffs),
                     'ties':sum(abs(d)<=1e-12 for d in diffs),
                     'losses':sum(d< -1e-12 for d in diffs),
                     'mean_variant_wall_seconds':statistics.mean(ta),
                     'mean_comparator_wall_seconds':statistics.mean(tb)})
    return report


def report_from_bytes(blob):
    manifest,rows=unpack_pinned_archive(blob)
    groups=validate_rows(manifest,rows)
    return {'status':STATUS,'source_run_id':41810700077,'artifact_id':ARTIFACT_ID,
      'artifact_sha256':PINNED_ARCHIVE_SHA256,'n_rows_verified':len(rows),
      'development_seed_count':len(SEEDS),'paired_tasks':len(groups),
      'contrasts':paired_analysis(groups),'no_new_tasks_executed':True,
      'independent_holdout_seeds_accessed':False,'synthetic_only':True,
      'confirmatory':False,'scored_validation_allowed':False,
      'limitations':['Descriptive exploratory reanalysis of 5 previously used seeds, not independent confirmation.',
       'The 450 rows derive from a single GitHub CI run; timer durations are machine-dependent.',
       'More simulations or deeper horizons do not guarantee better decisions.',
       'This analysis does not test a new Bayesian belief-state tree or real materials.']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--archive',type=Path,required=True,help='Existing GitHub Actions artifact ZIP; never generate tasks')
    p.add_argument('--out-dir',type=Path,default=Path('runs/mcts_ablation_audit_v1'))
    args=p.parse_args()
    report=report_from_bytes(args.archive.read_bytes())
    args.out_dir.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    (args.out_dir/'ablation_report.json').write_bytes(data)
    (args.out_dir/'ablation_report.sha256').write_text(sha256(data)+'  ablation_report.json\n')
    with (args.out_dir/'ablation_summary.md').open('w',encoding='utf-8') as f:
        f.write('# BHS MCTS exploratory ablation audit\n\n')
        f.write('Development-only; n=5 paired seeds per cell; no holdout, no physical conclusions.\n\n')
        f.write('| Scenario | Budget | Contrast | Mean Δ utility | W / T / L |\n|---|---:|---|---:|---|\n')
        for row in report['contrasts']:
            f.write(f"| {row['scenario']} | {row['budget']} | {row['contrast']} | {row['mean_difference']:+.5f} | {row['wins']} / {row['ties']} / {row['losses']} |\n")
    print(json.dumps({'status':STATUS,'records':len(report['contrasts']),
         'verified_rows':report['n_rows_verified'],'scored_validation_allowed':False},sort_keys=True))

if __name__=='__main__':main()
