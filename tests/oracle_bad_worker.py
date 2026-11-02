"""Synthetic fixture; mode selected via candidate ID. Never supply real labels."""
import json
import sys
import time
for line in sys.stdin:
    msg = json.loads(line)
    mode = msg['candidate_ids'][0]
    if mode == 'hang':
        time.sleep(60)
    elif mode == 'exit':
        sys.exit(0)
    elif mode == 'invalid':
        sys.stdout.write('not-json\n')
    elif mode == 'oversize':
        sys.stdout.write('x' * 20000 + '\n')
    elif mode == 'unknown':
        sys.stdout.write(json.dumps({'candidate_id': 'not-in-pool'}) + '\n')
    elif mode == 'schema':
        sys.stdout.write(json.dumps({'candidate_id': 1}) + '\n')
    else:
        sys.stdout.write(json.dumps({'candidate_id': mode}) + '\n')
    sys.stdout.flush()
