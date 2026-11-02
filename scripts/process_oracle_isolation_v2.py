"""Synthetic process group and full-duplex deadline gate. POSIX only; NOT a sandbox."""
from __future__ import annotations
import json, math, os, selectors, signal, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 16384
STATUS = "SYNTHETIC_PROCESS_GROUP_CONTRACT_ONLY_NOT_BENCHMARK"

class IsolationProtocolError(RuntimeError): pass
class IsolationDeadlineError(TimeoutError): pass

def _exchange(proc, obj, timeout):
    payload = (json.dumps(obj, allow_nan=False, separators=(',', ':')) + "\n").encode()
    if len(payload) > MAX_BYTES: raise IsolationProtocolError("oversized request")
    deadline = time.monotonic() + timeout
    buf = bytearray(); sent = 0
    for stream in (proc.stdin, proc.stdout): os.set_blocking(stream.fileno(), False)
    with selectors.DefaultSelector() as sel:
        sel.register(proc.stdin, selectors.EVENT_WRITE)
        sel.register(proc.stdout, selectors.EVENT_READ)
        while True:
            remain = deadline - time.monotonic()
            if remain <= 0: raise IsolationDeadlineError("worker exchange deadline")
            events = sel.select(remain)
            if not events: raise IsolationDeadlineError("worker exchange deadline")
            for key, event in events:
                if key.fileobj is proc.stdin:
                    try: n = os.write(proc.stdin.fileno(), payload[sent:])
                    except (BrokenPipeError, OSError) as e: raise IsolationProtocolError("worker input failed") from e
                    if n == 0: raise IsolationProtocolError("zero-byte worker write")
                    sent += n
                    if sent == len(payload): sel.unregister(proc.stdin)
                else:
                    try: piece = os.read(proc.stdout.fileno(), min(4096, MAX_BYTES + 1-len(buf)))
                    except OSError as e: raise IsolationProtocolError("worker output failed") from e
                    if not piece: raise IsolationProtocolError("worker output EOF")
                    buf.extend(piece)
                    if len(buf) > MAX_BYTES: raise IsolationProtocolError("oversized response")
                    if b"\n" in buf:
                        if not buf.endswith(b"\n") or buf.count(b"\n") != 1:
                            raise IsolationProtocolError("invalid response framing")
                        try: msg = json.loads(bytes(buf).decode())
                        except (UnicodeError, json.JSONDecodeError) as e: raise IsolationProtocolError("invalid JSON") from e
                        if not isinstance(msg,dict) or set(msg) != {'candidate_id'} or not isinstance(msg['candidate_id'],str):
                            raise IsolationProtocolError("invalid response schema")
                        return msg['candidate_id']

def _cleanup_group(proc):
    # Do not depend on parent liveness: descendants might keep stdout open.
    try: os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError: pass
    try: proc.wait(timeout=0.3)
    except subprocess.TimeoutExpired: pass
    # Kill the group even if the leader has already exited.
    try: os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError: pass
    try: proc.wait(timeout=1.0)
    except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=1.0)
    for stream in (proc.stdin,proc.stdout):
        if stream: stream.close()

def run_synthetic_isolation_trial(labels, budget=2, *, worker_module='scripts.synthetic_policy_worker', timeout_seconds=3.0):
    if os.name != 'posix': raise RuntimeError('POSIX only')
    if isinstance(timeout_seconds,bool) or not isinstance(timeout_seconds,(int,float)) or not math.isfinite(timeout_seconds) or timeout_seconds <= 0: raise ValueError('invalid timeout')
    if isinstance(budget,bool) or not isinstance(budget,int) or budget < 1: raise ValueError('invalid budget')
    if not isinstance(labels,dict) or not labels or any(not isinstance(k,str) or not k for k in labels): raise ValueError('invalid pool')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in labels.values()): raise ValueError('invalid labels')
    if budget > len(labels): raise ValueError('budget exceeds pool')
    if not isinstance(worker_module,str) or not worker_module or not all(x.isidentifier() for x in worker_module.split('.')): raise ValueError('invalid module')
    env = {'PATH':os.environ.get('PATH','/usr/bin:/bin'), 'PYTHONPATH':str(ROOT),'PYTHONDONTWRITEBYTECODE':'1'}
    p = subprocess.Popen([sys.executable,'-B','-m',worker_module],cwd=str(ROOT),env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,bufsize=0,start_new_session=True,close_fds=True)
    observations=[]
    try:
        for step in range(budget):
            req={'candidate_ids':sorted(labels),'remaining_budget':budget-step,'observations':observations}
            chosen=_exchange(p,req,float(timeout_seconds))
            if chosen not in labels or any(o['candidate_id']==chosen for o in observations): raise IsolationProtocolError('invalid candidate selection')
            observations.append({'candidate_id':chosen,'value':float(labels[chosen]),'step':step+1})
    finally: _cleanup_group(p)
    return {'status':STATUS,'query_trace':[{'candidate_id':o['candidate_id'],'step':o['step']} for o in observations],'budget_used':len(observations),'real_labels_used':False,'benchmark_run':False}
