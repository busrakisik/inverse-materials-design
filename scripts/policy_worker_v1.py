"""Policy subprocess. Receives public descriptors and prior observations only.

NOT a security sandbox: the operating system does not isolate filesystem/network access.
"""
from __future__ import annotations
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from scripts.bayesian_only_policy_v1 import BayesianOnlyPolicyV1

MAX_LINE = 100_000


def read_request():
    line = sys.stdin.buffer.readline(MAX_LINE + 1)
    if not line:
        return None
    if len(line) > MAX_LINE or not line.endswith(b'\n'):
        raise ValueError('oversized or unterminated request')
    obj = json.loads(line)
    if not isinstance(obj, dict) or set(obj) - {'command', 'seed', 'public', 'observations'}:
        raise ValueError('unexpected request fields')
    return obj


def main():
    policy = None
    for _ in range(21):
        item = read_request()
        if item is None:
            return
        command = item.get('command')
        if command == 'initialize':
            if policy is not None or set(item) != {'command', 'seed'}:
                raise ValueError('invalid initialization')
            policy = BayesianOnlyPolicyV1(item['seed'])
            response = {'status': 'ready'}
        elif command == 'choose':
            if policy is None or set(item) != {'command', 'public', 'observations'}:
                raise ValueError('invalid choice request')
            response = {'candidate_id': policy.choose(item['public'], item['observations'])}
        else:
            raise ValueError('unsupported command')
        sys.stdout.write(json.dumps(response, sort_keys=True) + '\n')
        sys.stdout.flush()
    raise ValueError('request cap exceeded')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print('invalid worker request: ' + type(exc).__name__, file=sys.stderr)
        raise SystemExit(2)
