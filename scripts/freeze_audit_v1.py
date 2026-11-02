"""Metadata-only BHS validation preflight. Never evaluates holdout tasks."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import pathlib
import re
import subprocess

STATUS = 'AUDIT_ONLY_NOT_FROZEN_NO_HOLDOUT_EVALUATION'
SOURCE_PATHS = (
    'scripts/scientific_benchmark_contract_v1.py',
    'scripts/bayesian_only_policy_v1.py',
    'scripts/paired_benchmark_pilot_v1.py',
    'scripts/validation_freeze_prepare_v1.py',
    'research/VALIDATION_PROTOCOL.md',
    'research/FREEZE_DECISION_RECORD.md',
)
PROPOSED_SEEDS = tuple(range(10000, 10100))
KNOWN_PILOT_SEEDS = tuple(range(30))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get_static_pilot_seed_range(source: str):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'build_pilot':
            for arg, default in zip(reversed(node.args.args), reversed(node.args.defaults)):
                if arg.arg == 'seeds' and isinstance(default, ast.Call) and isinstance(default.func, ast.Name) and default.func.id == 'range' and len(default.args) == 1 and isinstance(default.args[0], ast.Constant) and type(default.args[0].value) is int:
                    return tuple(range(default.args[0].value))
    return None


def audit(root: pathlib.Path) -> dict:
    root = pathlib.Path(root)
    hashes = {}
    for rel in SOURCE_PATHS:
        path = root / rel
        if not path.is_file():
            raise FileNotFoundError(rel)
        hashes[rel] = sha256(path.read_bytes())
    sha = subprocess.check_output(['git','rev-parse','HEAD'], cwd=root, text=True).strip()
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('invalid Git SHA')
    observed_pilot = get_static_pilot_seed_range((root/'scripts/paired_benchmark_pilot_v1.py').read_text())
    if observed_pilot is None:
        raise ValueError('cannot statically establish default pilot seed range')
    if observed_pilot != KNOWN_PILOT_SEEDS:
        raise ValueError('documented pilot seed set differs from code')
    if set(PROPOSED_SEEDS) & set(observed_pilot):
        raise ValueError('candidate holdout intersects documented pilot')
    seed_bytes = (json.dumps(PROPOSED_SEEDS, separators=(',', ':'))+'\n').encode()
    return {
        'status': STATUS,
        'source_commit': sha,
        'source_sha256': hashes,
        'documented_default_pilot_seeds': list(observed_pilot),
        'proposed_holdout_seeds': list(PROPOSED_SEEDS),
        'proposed_holdout_sha256': sha256(seed_bytes),
        'documented_pilot_disjoint': True,
        'all_historical_development_seeds_audited': False,
        'primary_scenario_proposal': 'smooth',
        'primary_scenario_status': 'PILOT_INFORMED_PROPOSAL_NOT_APPROVED',
        'environment_locked': False,
        'independent_label_boundary_audit': False,
        'independent_reviewer_approval': False,
        'freeze_approved': False,
        'scored_validation_allowed': False,
        'limitations': [
            'Static audit covers only documented default pilot seed range; manual runs and external experiments are unknown.',
            'Same-process evaluator is not a security boundary against malicious policy code.',
            'Do not execute proposed seed tasks or inspect their outcomes from this stage.',
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out-dir',default='runs/freeze_audit_v1')
    args=p.parse_args()
    root=pathlib.Path(__file__).resolve().parents[1]
    result=audit(root)
    out=pathlib.Path(args.out_dir);out.mkdir(parents=True, exist_ok=True)
    (out/'audit_manifest.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':STATUS,'scored_validation_allowed':False,'documented_pilot_disjoint':True}))

if __name__=='__main__':main()
