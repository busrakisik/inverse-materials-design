"""Consolidate verifiable repository metadata, NEVER run or approve holdout tasks.

A self-authored manifest is not independent scientific review.  All evidence
not actually supplied stays UNKNOWN, and the output always denies validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

STATUS = 'FREEZE_EVIDENCE_ASSEMBLY_ONLY_NOT_APPROVED'
SOURCE_FILES = (
    'scripts/scientific_benchmark_contract_v1.py',
    'scripts/bayesian_only_policy_v1.py',
    'scripts/paired_benchmark_pilot_v1.py',
    'research/VALIDATION_PROTOCOL.md',
    'research/FREEZE_DECISION_RECORD.md',
)
SEEDS = list(range(10000, 10100))
PILOT_SEEDS = set(range(30))
SCENARIOS = ('smooth', 'multimodal', 'uninformative', 'mismatched', 'duplicates')
BUDGETS = (1, 2, 5, 10)
POLICIES = ('random', 'greedy', 'bayesian_only')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def seed_digest() -> str:
    # Preserve the exact wire representation used in freeze_prepare_v1.
    return sha256((json.dumps(SEEDS, separators=(',', ':')) + '\n').encode())


def repo_commit(root: pathlib.Path) -> str:
    result = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if not re.fullmatch('[0-9a-f]{40}', result):
        raise ValueError('Git commit is not a 40-character lowercase SHA')
    return result


def hash_sources(root: pathlib.Path) -> dict[str, str]:
    hashes = {}
    for rel in SOURCE_FILES:
        candidate = root / rel
        if not candidate.is_file():
            raise FileNotFoundError(f'required source absent: {rel}')
        hashes[rel] = sha256(candidate.read_bytes())
    return hashes


def validate_optional_evidence(name: str, blob: bytes) -> dict:
    """Report claims and digest, never convert a self-reported flag to approval."""
    if len(blob) > 2_000_000:
        raise ValueError('evidence too large')
    try:
        item = json.loads(blob)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f'bad JSON evidence: {name}') from exc
    if not isinstance(item, dict):
        raise ValueError('evidence must be a JSON object')
    claimed_sha = item.get('commit', item.get('source_commit'))
    return {'name': name, 'sha256': sha256(blob), 'declared_commit':
            claimed_sha if isinstance(claimed_sha, str) and re.fullmatch('[0-9a-f]{40}', claimed_sha) else None,
            'declared_status': str(item.get('status', 'UNKNOWN'))[:160],
            'independently_verified': False}


def assemble(root: pathlib.Path, *, commit: str | None = None,
             evidence: dict[str, bytes] | None = None) -> dict:
    root = pathlib.Path(root)
    current = repo_commit(root) if commit is None else commit
    if not isinstance(current, str) or not re.fullmatch('[0-9a-f]{40}', current):
        raise ValueError('invalid commit SHA')
    if len(SEEDS) != 100 or len(set(SEEDS)) != 100 or set(SEEDS) & PILOT_SEEDS:
        raise ValueError('seed proposal invalid or overlaps documented pilot')
    hashes = hash_sources(root)
    records = []
    for name, data in sorted((evidence or {}).items()):
        if not isinstance(name, str) or '/' in name or '\\' in name or not name.endswith('.json'):
            raise ValueError('invalid evidence name')
        rec = validate_optional_evidence(name, data)
        rec['same_commit_as_current_tree'] = rec['declared_commit'] == current
        records.append(rec)
    return {
        'schema': 'bhs.validation-freeze-evidence.v1',
        'status': STATUS,
        'current_commit': current,
        'source_sha256': hashes,
        'candidate_holdout_seeds': SEEDS,
        'candidate_holdout_seed_sha256': seed_digest(),
        'documented_pilot_seeds': sorted(PILOT_SEEDS),
        'documented_pilot_disjoint': True,
        'planned_scenarios': list(SCENARIOS),
        'planned_budgets': list(BUDGETS),
        'planned_policies': list(POLICIES),
        'candidate_primary_scenario': 'smooth',
        'candidate_primary_scenario_selection': 'PILOT_INFORMED_NOT_PREAPPROVED',
        'candidate_bayesian_parameters': {
            'prior_variance': 1.0, 'noise_variance': 0.1, 'exploration_scale': 1.0,
        },
        'historical_artifacts_supplied': records,
        'gates': {
            'source_hashes_current_tree_recorded': True,
            'candidate_seeds_disjoint_from_documented_30_pilot_seeds': True,
            'all_historical_and_offline_seeds_audited': False,
            'full_environment_hermetically_pinned': False,
            'primary_design_and_bootstrap_seed_frozen': False,
            'independent_label_firewall_reviewed': False,
            'external_reviewer_approval_verified': False,
            'pre_outcome_immutable_freeze_registered': False,
        },
        'external_independent_evidence_verified': False,
        'freeze_approved': False,
        'scored_validation_allowed': False,
        'holdout_tasks_generated': False,
        'holdout_labels_accessed': False,
        'limitations': [
            'Artifact JSON is self-reported metadata, not independent attestation.',
            'The current commit differs from earlier CI artifact source commits; per-source digests and provenance must be reconciled.',
            'A literal seed list does not prove no prior local, external, or deleted use.',
            'This tool performs no scored benchmark and grants no permission to run one.',
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', default='runs/validation_freeze_manifest_v1')
    parser.add_argument('--evidence-json', action='append', default=[],
                        help='Optional local JSON metadata evidence (never trust as approval)')
    args = parser.parse_args()
    root = pathlib.Path(__file__).resolve().parents[1]
    evidence = {}
    for name in args.evidence_json:
        p = pathlib.Path(name)
        if p.name in evidence:
            raise ValueError('duplicate evidence basename')
        evidence[p.name] = p.read_bytes()
    data = assemble(root, evidence=evidence)
    target = pathlib.Path(args.out_dir)
    target.mkdir(parents=True, exist_ok=True)
    payload = canonical_json(data)
    (target / 'freeze_evidence_manifest.json').write_bytes(payload)
    (target / 'freeze_evidence_manifest.sha256').write_text(
        sha256(payload) + '  freeze_evidence_manifest.json\n', encoding='utf-8')
    print(json.dumps({'status': STATUS, 'source_files': len(SOURCE_FILES),
                      'metadata_evidence_count': len(data['historical_artifacts_supplied']),
                      'scored_validation_allowed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
