"""Synthetic-only policy/evaluator process boundary demonstration. NO holdout.

Trusted parent retains the complete labels; worker receives public descriptors and
prior observations only. Distinct processes != security sandbox.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from scripts.scientific_benchmark_contract_v1 import make_task

STATUS = 'SYNTHETIC_PROCESS_BOUNDARY_DEMO_NOT_SANDBOX_NO_HOLDOUT'
MAX_MESSAGE = 100_000
WORKER = Path(__file__).with_name('policy_worker_v1.py').resolve()


def _exchange(process, payload):
    data = json.dumps(payload, sort_keys=True, allow_nan=False)
    if len(data.encode('utf-8')) > MAX_MESSAGE - 1:
        raise ValueError('request too large')
    process.stdin.write(data + '\n')
    process.stdin.flush()
    response = process.stdout.readline(MAX_MESSAGE)
    if not response or len(response) >= MAX_MESSAGE:
        raise RuntimeError('worker ended or oversized reply')
    parsed = json.loads(response)
    if not isinstance(parsed, dict):
        raise RuntimeError('invalid worker response')
    return parsed


def run_demo(*, scenario='smooth', task_seed=7, policy_seed=13, budget=5, worker_path=WORKER):
    # Allow only one fixed development seed in the CLI/demo; no independent holdout.
    if scenario != 'smooth' or type(task_seed) is not int or task_seed != 7:
        raise ValueError('only predefined development task smooth/7 is permitted')
    if type(policy_seed) is not int or policy_seed != 13 or type(budget) is not int or budget != 5:
        raise ValueError('only predefined policy seed/budget are permitted')
    task = make_task(scenario, task_seed, n=20)
    public = task.public_view()
    observations = []
    trace = []
    # Isolated interpreter flags prevent user site packages and site initialization.
    # They do NOT block networking, file reads, or malicious worker code.
    env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'PYTHONIOENCODING': 'utf-8'}
    process = subprocess.Popen(
        [sys.executable, '-I', '-S', str(Path(worker_path).resolve())],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding='utf-8', env=env, cwd=str(Path(worker_path).resolve().parents[1]),
    )
    try:
        result = _exchange(process, {'command': 'initialize', 'seed': policy_seed})
        if result != {'status': 'ready'}:
            raise RuntimeError('worker did not acknowledge initialization')
        for step in range(budget):
            # Only these two fields flow into choose(). The full label map stays here.
            result = _exchange(process, {'command': 'choose', 'public': public,
                                         'observations': observations})
            if set(result) != {'candidate_id'}:
                raise RuntimeError('invalid worker response fields')
            candidate = result['candidate_id']
            if type(candidate) is not str or candidate not in public or candidate in {r[0] for r in observations}:
                raise RuntimeError('invalid or repeated action')
            value = task._labels[candidate]
            observations.append([candidate, value])
            trace.append({'step': step + 1, 'candidate_id': candidate, 'value': value})
        process.stdin.close()
        try:
            exitcode = process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait()
            raise RuntimeError('worker exit timeout')
        if exitcode != 0:
            raise RuntimeError('worker exit failure')
    finally:
        if process.poll() is None:
            process.kill(); process.wait()
        if process.stdin and not process.stdin.closed:
            process.stdin.close()
        if process.stdout: process.stdout.close()
        if process.stderr: process.stderr.close()
    return {
        'status': STATUS, 'scenario': scenario, 'task_seed': task_seed,
        'policy_seed': policy_seed, 'budget': budget,
        'trace': trace, 'public_view_sha256': hashlib.sha256(json.dumps(public,sort_keys=True).encode()).hexdigest(),
        'worker_receives_complete_label_map': False,
        'separate_processes': True,
        'adversarial_worker_containment_proven': False,
        'os_security_sandbox': False,
        'scored_validation_allowed': False,
        'holdout_tasks_generated': False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', default='runs/policy_evaluator_isolation_v1')
    args = parser.parse_args()
    report = run_demo()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(report, indent=2, sort_keys=True) + '\n').encode()
    (out / 'process_boundary_demo.json').write_bytes(data)
    (out / 'process_boundary_demo.sha256').write_text(hashlib.sha256(data).hexdigest() + '  process_boundary_demo.json\n')
    print(json.dumps({'status': STATUS, 'queries': len(report['trace']),
                      'scored_validation_allowed': False}))

if __name__ == '__main__':
    main()
