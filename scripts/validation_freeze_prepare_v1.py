"""Metadata-only preparation for independent synthetic validation. Never computes scores."""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

FILES = (
    'scripts/scientific_benchmark_contract_v1.py',
    'scripts/bayesian_only_policy_v1.py',
    'scripts/paired_benchmark_pilot_v1.py',
    'research/VALIDATION_PROTOCOL.md',
)
SEEDS = tuple(range(10000, 10100))
PILOT_SEEDS = frozenset(range(30))
STATUS = 'PROPOSED_NOT_FROZEN_NO_HOLDOUT_EVALUATION'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def prepare(root):
    root = pathlib.Path(root)
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if len(sha) != 40 or any(c not in '0123456789abcdef' for c in sha):
        raise ValueError('invalid commit SHA')
    hashes = {}
    for relative in FILES:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f'missing required source: {relative}')
        hashes[relative] = digest(path.read_bytes())
    if len(SEEDS) != 100 or len(set(SEEDS)) != 100 or PILOT_SEEDS.intersection(SEEDS):
        raise ValueError('seed collision with known exploratory pilot')
    seed_bytes = (json.dumps(SEEDS, separators=(',', ':')) + '\n').encode()
    return {
        'status': STATUS,
        'git_commit': sha,
        'source_sha256': hashes,
        'proposed_holdout_seeds': list(SEEDS),
        'proposed_holdout_seed_sha256': digest(seed_bytes),
        'known_pilot_seeds_excluded': list(sorted(PILOT_SEEDS)),
        'all_other_development_seeds_audited': False,
        'primary_scenario': None,
        'selection_rationale_recorded': False,
        'policy_parameters_confirmed': False,
        'environment_lock_sha256': None,
        'independent_leakage_audit_passed': False,
        'freeze_approved': False,
        'scored_validation_allowed': False,
        'note': 'Proposal only. Do not run holdout. Audit other previous dev seeds and predeclare primary scenario before freeze.'
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', default='runs/validation_freeze_preparation_v1')
    args = parser.parse_args()
    root = pathlib.Path(__file__).resolve().parents[1]
    manifest = prepare(root)
    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'freeze_proposal.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (out / 'holdout_seed_proposal.json').write_text(json.dumps(SEEDS, separators=(',', ':')) + '\n', encoding='utf-8')
    print(json.dumps({'status': STATUS, 'seed_count': len(SEEDS), 'scored_validation_allowed': False}, sort_keys=True))

if __name__ == '__main__':
    main()
