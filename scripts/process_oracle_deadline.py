"""Synthetic-only process-oracle deadline gate. NOT an OS sandbox or real benchmark."""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time

STATUS = 'SYNTHETIC_DEADLINE_CONTRACT_ONLY_NOT_BENCHMARK'
MAX_MESSAGE_BYTES = 16384
REPO_ROOT = Path(__file__).resolve().parents[1]

class OracleProtocolError(RuntimeError):
    pass

class OracleDeadlineError(TimeoutError):
    pass

def _frame(obj):
    raw = (json.dumps(obj, allow_nan=False, separators=(',', ':')) + '\n').encode('utf-8')
    if len(raw) > MAX_MESSAGE_BYTES:
        raise ValueError('oversized request')
    return raw

def _readline_deadline(proc, timeout_seconds):
    """Bounded binary read using POSIX selectors; no indefinite buffered readline."""
    deadline = time.monotonic() + timeout_seconds
    out = bytearray()
    with selectors.DefaultSelector() as selector:
        selector.register(proc.stdout, selectors.EVENT_READ)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise OracleDeadlineError('worker response deadline exceeded')
            if not selector.select(remaining):
                raise OracleDeadlineError('worker response deadline exceeded')
            piece = os.read(proc.stdout.fileno(), min(4096, MAX_MESSAGE_BYTES + 1 - len(out)))
            if not piece:
                raise OracleProtocolError('worker exited or closed stdout')
            out.extend(piece)
            if len(out) > MAX_MESSAGE_BYTES:
                raise OracleProtocolError('oversized worker response')
            if b'\n' in out:
                if not out.endswith(b'\n') or out.count(b'\n') != 1:
                    raise OracleProtocolError('multiple responses in one frame')
                return bytes(out)

def _request(proc, req, timeout_seconds):
    if proc.poll() is not None:
        raise OracleProtocolError('worker already exited')
    try:
        proc.stdin.write(_frame(req))
        proc.stdin.flush()
    except (BrokenPipeError, OSError) as exc:
        raise OracleProtocolError('worker input pipe failed') from exc
    raw = _readline_deadline(proc, timeout_seconds)
    try:
        response = json.loads(raw.decode('utf-8'))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise OracleProtocolError('invalid JSON response') from exc
    if not isinstance(response, dict) or set(response) != {'candidate_id'} or not isinstance(response['candidate_id'], str):
        raise OracleProtocolError('invalid response schema')
    return response['candidate_id']

def run_synthetic_deadline_trial(labels, budget=2, *, worker_module='scripts.synthetic_policy_worker', response_timeout_seconds=3.0):
    """Fabricated labels only. Worker inherits filesystem/network rights: NOT secure isolation."""
    if isinstance(response_timeout_seconds, bool) or not isinstance(response_timeout_seconds, (int, float)) or not math.isfinite(response_timeout_seconds) or response_timeout_seconds <= 0:
        raise ValueError('invalid timeout')
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
        raise ValueError('invalid budget')
    if not isinstance(labels, dict) or not labels or any(not isinstance(k, str) or not k for k in labels):
        raise ValueError('invalid candidates')
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in labels.values()):
        raise ValueError('invalid synthetic labels')
    if budget > len(labels):
        raise ValueError('budget exceeds pool')
    if not isinstance(worker_module, str) or not worker_module or not all(part.isidentifier() for part in worker_module.split('.')):
        raise ValueError('invalid worker module')
    env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'PYTHONPATH': str(REPO_ROOT), 'PYTHONDONTWRITEBYTECODE': '1'}
    observations = []
    proc = subprocess.Popen([sys.executable, '-B', '-m', worker_module], cwd=str(REPO_ROOT), env=env,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            bufsize=0, close_fds=True)
    try:
        for step in range(budget):
            req = {'candidate_ids': sorted(labels), 'remaining_budget': budget - step, 'observations': observations}
            chosen = _request(proc, req, float(response_timeout_seconds))
            if chosen not in labels:
                raise OracleProtocolError('unknown candidate')
            if any(o['candidate_id'] == chosen for o in observations):
                raise OracleProtocolError('repeated candidate')
            observations.append({'candidate_id': chosen, 'value': float(labels[chosen]), 'step': step + 1})
    finally:
        if proc.poll() is None:
            proc.terminate()
        try:
            proc.communicate(timeout=0.5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate(timeout=1)
    return {'status': STATUS, 'query_trace': [{'candidate_id': o['candidate_id'], 'step': o['step']} for o in observations],
            'budget_used': len(observations), 'real_labels_used': False, 'benchmark_run': False}
