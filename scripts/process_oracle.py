"""Synthetic-only isolated policy-worker demonstration; NOT an OS security sandbox."""
from __future__ import annotations
import json
import math
import subprocess
import sys
from dataclasses import dataclass

STATUS = 'SYNTHETIC_PROCESS_CONTRACT_NOT_MATERIALS_BENCHMARK'
MAX_MESSAGE_BYTES = 16384


def _frame(obj):
    raw = json.dumps(obj, allow_nan=False, separators=(',', ':')) + '\n'
    if len(raw.encode()) > MAX_MESSAGE_BYTES:
        raise ValueError('message exceeds size limit')
    return raw


def _request(proc, request):
    if proc.poll() is not None:
        raise RuntimeError('policy worker already exited')
    proc.stdin.write(_frame(request))
    proc.stdin.flush()
    line = proc.stdout.readline(MAX_MESSAGE_BYTES + 1)
    if not line or len(line.encode()) > MAX_MESSAGE_BYTES or not line.endswith('\n'):
        raise RuntimeError('missing or oversized worker response')
    try:
        response = json.loads(line)
    except json.JSONDecodeError as e:
        raise RuntimeError('invalid worker JSON') from e
    if not isinstance(response, dict) or set(response) != {'candidate_id'} or not isinstance(response['candidate_id'], str):
        raise RuntimeError('invalid worker response schema')
    return response['candidate_id']


def run_synthetic_isolated_trial(labels, budget=2, *, worker_module='scripts.synthetic_policy_worker'):
    """Trusted host holds labels. Child receives public IDs and queried observations only.

    Demonstrates process-level separation, not a hardened sandbox. The subprocess
    could read files/network or inspect inherited environment unless separately
    restricted; do not use real held-out labels.
    """
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
        raise ValueError('invalid budget')
    if not isinstance(labels, dict) or not labels or any(not isinstance(k, str) or not k for k in labels):
        raise ValueError('invalid candidates')
    if any(isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v) for v in labels.values()):
        raise ValueError('invalid synthetic labels')
    if budget > len(labels):
        raise ValueError('budget exceeds candidate pool')
    candidate_ids = sorted(labels)
    observations = []
    with subprocess.Popen([sys.executable, '-m', worker_module], stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          text=True, encoding='utf-8', bufsize=1) as proc:
        try:
            for step in range(budget):
                request = {'candidate_ids': candidate_ids, 'remaining_budget': budget-step,
                           'observations': observations}
                chosen = _request(proc, request)
                if chosen not in labels:
                    raise ValueError('unknown policy candidate')
                if any(o['candidate_id'] == chosen for o in observations):
                    raise ValueError('repeated candidate')
                observations.append({'candidate_id':chosen, 'value':float(labels[chosen]), 'step':step+1})
        finally:
            if proc.poll() is None:
                proc.terminate()
                try: proc.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill();proc.communicate()
    return {'status': STATUS, 'query_trace':[{'candidate_id':o['candidate_id'],'step':o['step']} for o in observations],
            'budget_used':len(observations), 'real_labels_used':False, 'benchmark_run':False}
