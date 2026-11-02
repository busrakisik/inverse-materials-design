"""Synthetic adversarial fixtures: no real dataset or labels."""
import json, sys, time, subprocess, os
for line in sys.stdin:
    mode=json.loads(line)['candidate_ids'][0]
    if mode=='hang': time.sleep(30)
    elif mode=='exit': sys.exit(0)
    elif mode=='malformed': sys.stdout.write('bad\n')
    elif mode=='oversize': sys.stdout.write('x'*20000+'\n')
    elif mode=='unknown': sys.stdout.write('{"candidate_id":"not-in-pool"}\n')
    elif mode=='schema': sys.stdout.write('{"candidate_id":7}\n')
    elif mode=='descendant':
        # Creates a process in same group that inherits stdout and waits.
        subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])
        time.sleep(30)
    else: sys.stdout.write(json.dumps({'candidate_id':mode})+'\n')
    sys.stdout.flush()
