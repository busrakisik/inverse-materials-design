"""Toy synthetic worker. No labels, dataset paths, or training are provided."""
import json
import sys


def choose(msg):
    if not isinstance(msg, dict) or set(msg) != {'candidate_ids', 'remaining_budget', 'observations'}:
        raise ValueError('invalid request')
    ids = msg['candidate_ids']
    observations = msg['observations']
    if not isinstance(ids,list) or any(not isinstance(i,str) for i in ids) or not isinstance(observations,list):
        raise ValueError('invalid field types')
    queried = {o['candidate_id'] for o in observations}
    return next(x for x in ids if x not in queried)


def main():
    for line in sys.stdin:
        try:
            msg = json.loads(line)
            result = {'candidate_id':choose(msg)}
        except (ValueError, TypeError, KeyError, StopIteration):
            result = {'candidate_id':''}
        print(json.dumps(result,allow_nan=False),flush=True)

if __name__ == '__main__':main()
