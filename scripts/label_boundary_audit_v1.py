"""Static, fail-closed audit of the synthetic benchmark's label boundary.

This tool does not generate tasks, inspect labels, or approve held-out experiments.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path

CORE = 'scripts/scientific_benchmark_contract_v1.py'
PILOT = 'scripts/paired_benchmark_pilot_v1.py'
STATUS = 'IN_PROCESS_LABEL_BOUNDARY_NOT_ISOLATED_NO_HOLDOUT'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _method(tree: ast.AST, klass: str, method: str):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == klass:
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == method:
                    return child
    return None


def _function(tree: ast.AST, name: str):
    return next((n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None)


def _has_attribute(root: ast.AST, attr: str) -> bool:
    return any(isinstance(n, ast.Attribute) and n.attr == attr for n in ast.walk(root))


def _calls_method(root: ast.AST, name: str) -> bool:
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == name for n in ast.walk(root))


def assess(core: str, pilot: str) -> dict:
    core_tree, pilot_tree = ast.parse(core), ast.parse(pilot)
    run = _method(core_tree, 'MeteredEvaluator', 'run')
    task = next((n for n in core_tree.body if isinstance(n, ast.ClassDef) and n.name == 'SyntheticTask'), None)
    evaluate = _function(pilot_tree, 'evaluate')
    if run is None or task is None or evaluate is None:
        raise ValueError('Expected benchmark source structures are missing')
    checks = {
        'evaluator_accesses_private_labels': _has_attribute(run, '_labels'),
        'policy_invoked_in_same_process': _calls_method(run, 'choose'),
        'task_object_contains_private_labels': any(isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == '_labels' for n in task.body),
        'pilot_reads_oracle_for_regret': _has_attribute(evaluate, '_labels'),
        'policy_input_uses_public_view': _calls_method(run, 'public_view'),
    }
    # Avoid inferring strong isolation from surface-level argument passing: same-process
    # Python policies can inspect stack frames and mutable objects.
    if not all(checks.values()):
        raise ValueError('Unexpected benchmark structure; manual security review required')
    return {
        'schema': 'bhs.label-boundary-audit.v1', 'status': STATUS,
        'static_structure_checks': checks,
        'normal_api_uses_public_descriptors_and_prior_observations': True,
        'adversarial_code_isolation_established': False,
        'independent_label_firewall_review_completed': False,
        'trusted_in_process_evaluator_only': True,
        'scored_validation_allowed': False,
        'holdout_tasks_generated': False,
        'holdout_labels_accessed': False,
        'limitations': [
            'AST inspection is not a runtime guarantee of confidentiality.',
            'Private attribute names do not enforce a security boundary in Python.',
            'Policies invoked in-process can potentially introspect caller frames or reachable objects.',
            'A process boundary with a narrowly serialized request/response protocol is required before claiming hostile-policy isolation.',
        ],
    }


def audit_repository(root: Path) -> dict:
    root = Path(root)
    contents = {}
    for path in (CORE, PILOT):
        f = root / path
        if not f.is_file():
            raise FileNotFoundError(path)
        contents[path] = f.read_bytes()
    report = assess(contents[CORE].decode('utf-8'), contents[PILOT].decode('utf-8'))
    report['source_sha256'] = {k: sha256(v) for k, v in contents.items()}
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', default='runs/label_boundary_audit_v1')
    args = ap.parse_args()
    report = audit_repository(Path(__file__).resolve().parents[1])
    target = Path(args.out_dir)
    target.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    (target / 'label_boundary_report.json').write_bytes(raw)
    (target / 'label_boundary_report.sha256').write_text(sha256(raw) + '  label_boundary_report.json\n')
    print(json.dumps({'status': STATUS, 'checks': len(report['static_structure_checks']),
                      'adversarial_code_isolation_established': False,
                      'scored_validation_allowed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
