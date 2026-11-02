"""Fail-closed readiness assessment. Metadata only; NEVER generate/evaluate held-out tasks."""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess

FILES = [
    'scripts/scientific_benchmark_contract_v1.py',
    'scripts/bayesian_only_policy_v1.py',
    'scripts/paired_benchmark_pilot_v1.py',
    'scripts/validation_freeze_prepare_v1.py',
    'scripts/freeze_audit_v1.py',
    'research/VALIDATION_PROTOCOL.md',
    'research/FREEZE_DECISION_RECORD.md',
]
SEEDS = list(range(10000, 10100))
SCENARIOS = {'smooth','multimodal','uninformative','mismatched','duplicates'}
STATUS = 'READINESS_CHECK_ONLY_NO_HOLDOUT_EVALUATION'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def seed_digest(seeds):
    return digest((json.dumps(seeds, separators=(',', ':')) + '\n').encode())


def assess(root, approval):
    root = pathlib.Path(root)
    sha = subprocess.check_output(['git','rev-parse','HEAD'], cwd=root, text=True).strip()
    if not re.fullmatch('[0-9a-f]{40}', sha):
        raise ValueError('invalid Git SHA')
    hashes = {}
    for rel in FILES:
        f = root / rel
        if not f.is_file():
            raise FileNotFoundError(rel)
        hashes[rel] = digest(f.read_bytes())
    if not isinstance(approval, dict):
        raise ValueError('approval must be an object')
    if any(type(s) is not int for s in SEEDS) or len(SEEDS) != 100 or len(set(SEEDS)) != 100:
        raise ValueError('invalid seed set')
    conditions = {
        'all_historical_seeds_independently_audited': approval.get('all_historical_seeds_independently_audited') is True,
        'development_seed_inventory_sha256': bool(re.fullmatch('[0-9a-f]{64}', str(approval.get('development_seed_inventory_sha256', '')))),
        'primary_scenario_declared': approval.get('primary_scenario') in SCENARIOS,
        'pilot_informed_declared': approval.get('primary_scenario_pilot_informed') is True,
        'prior_variance_locked': approval.get('prior_variance') == 1.0 and type(approval.get('prior_variance')) in (int,float),
        'noise_variance_locked': approval.get('noise_variance') == 0.1 and type(approval.get('noise_variance')) in (int,float),
        'exploration_scale_locked': approval.get('exploration_scale') == 1.0 and type(approval.get('exploration_scale')) in (int,float),
        'environment_lock_sha256': bool(re.fullmatch('[0-9a-f]{64}', str(approval.get('environment_lock_sha256', '')))),
        'bootstrap_seed_declared': type(approval.get('bootstrap_seed')) is int and approval['bootstrap_seed'] >= 0,
        'analysis_plan_approved': approval.get('analysis_plan_approved') is True,
        'independent_label_boundary_audit': approval.get('independent_label_boundary_audit') is True,
        'reviewer_approval': approval.get('reviewer_approval') is True,
        'approved_source_commit_matches': approval.get('approved_source_commit') == sha,
        'approved_seed_digest_matches': approval.get('approved_seed_digest') == seed_digest(SEEDS),
        'approved_source_hashes_match': approval.get('approved_source_sha256') == hashes,
    }
    # A self-declared checklist is NOT independent evidence: assessment intentionally never approves runs.
    return {'status':STATUS, 'source_commit':sha, 'source_sha256':hashes,
            'seed_count':len(SEEDS),'proposed_seed_sha256':seed_digest(SEEDS),
            'checks':conditions,'all_checks_reported':all(conditions.values()),
            'independent_evidence_verified':False,
            'scored_validation_allowed':False,
            'note':'Metadata checks only; independent review and evidence verification must occur outside this self-report gate.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--approval-file',default='research/FREEZE_READINESS_INPUT_V1.json')
    p.add_argument('--out-dir',default='runs/freeze_readiness_v1')
    args=p.parse_args()
    root=pathlib.Path(__file__).resolve().parents[1]
    f=root/args.approval_file
    approval=json.loads(f.read_text()) if f.is_file() else {}
    r=assess(root,approval)
    out=pathlib.Path(args.out_dir)
    out.mkdir(parents=True,exist_ok=True)
    (out/'readiness_report.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':STATUS,'scored_validation_allowed':False,'passed_checks':sum(r['checks'].values()),'total_checks':len(r['checks'])}))

if __name__=='__main__':main()
