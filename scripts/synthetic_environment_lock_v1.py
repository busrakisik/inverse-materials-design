"""Metadata-only environment provenance gate. Never constructs synthetic tasks or runs holdout."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

STATUS = 'PARTIAL_ENVIRONMENT_PIN_NOT_HERMETIC_NO_HOLDOUT'
PYTHON_PIN = (3, 11, 9)
SOURCES = (
    'scripts/scientific_benchmark_contract_v1.py',
    'scripts/bayesian_only_policy_v1.py',
    'scripts/paired_benchmark_pilot_v1.py',
)
ALLOWED_STDLIB = frozenset({'__future__', 'argparse', 'hashlib', 'json', 'math',
                            'random', 'statistics', 'time', 'pathlib', 'dataclasses'})
ALLOWED_LOCAL = frozenset({'scripts.scientific_benchmark_contract_v1',
                           'scripts.bayesian_only_policy_v1'})


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_imports(source: str) -> list[str]:
    """Fail closed on unknown import and obvious dynamic import; not a security sandbox."""
    tree = ast.parse(source)
    problems = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in ALLOWED_STDLIB:
                    problems.append('unexpected import: ' + alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level or (node.module not in ALLOWED_STDLIB and node.module not in ALLOWED_LOCAL):
                problems.append('unexpected from-import: ' + str(node.module))
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {'__import__', 'eval', 'exec'}:
                problems.append('dynamic execution: ' + node.func.id)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {'import_module', 'exec_module'}:
                problems.append('dynamic import call: ' + node.func.attr)
    return problems


def inspect_sources(root: Path) -> dict[str, str]:
    digests = {}
    for relative in SOURCES:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        raw = path.read_bytes()
        failures = check_imports(raw.decode('utf-8'))
        if failures:
            raise ValueError(f'{relative}: ' + '; '.join(failures))
        digests[relative] = sha256(raw)
    return digests


def build_manifest(root: Path, *, version=None, system=None, machine=None,
                   commit=None) -> dict:
    root = Path(root)
    hashes = inspect_sources(root)
    version = tuple(sys.version_info[:3]) if version is None else tuple(version)
    if version != PYTHON_PIN:
        raise ValueError(f'Python patch version must be {PYTHON_PIN}; received {version}')
    system = platform.system() if system is None else system
    machine = platform.machine() if machine is None else machine
    if system != 'Linux' or machine not in ('x86_64', 'AMD64'):
        raise ValueError('CI environment must be Linux x86_64')
    if commit is None:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('invalid commit')
    return {
        'status': STATUS,
        'commit': commit,
        'python_exact': '.'.join(map(str, version)),
        'operating_system': system,
        'architecture': machine,
        'source_sha256': hashes,
        'external_pip_dependencies_required_by_scoped_modules': [],
        'stdlib_import_allowlist_checked': True,
        'runner_label': 'ubuntu-24.04',
        'runner_image_digest_pinned': False,
        'actions_commit_digests_pinned': False,
        'environment_fully_hermetic': False,
        'historical_seeds_fully_audited': False,
        'independent_review_completed': False,
        'scored_validation_allowed': False,
        'limitations': [
            'A pinned Python patch and zero third-party imports do not pin Ubuntu runner image or interpreter build hash.',
            'Static import inspection is not malicious-code isolation and does not prove all runtime code paths.',
            'Generated manifest is observational provenance, not approval of held-out execution.'
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out-dir', default='runs/synthetic_environment_lock_v1')
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = build_manifest(root)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    blob = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode()
    (out / 'environment_manifest.json').write_bytes(blob)
    (out / 'environment_manifest.sha256').write_text(sha256(blob) + '  environment_manifest.json\n')
    print(json.dumps({'status': STATUS, 'python': manifest['python_exact'],
                      'source_files': len(manifest['source_sha256']),
                      'scored_validation_allowed': False}))


if __name__ == '__main__':
    main()
