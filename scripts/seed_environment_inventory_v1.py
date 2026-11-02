"""Static tracked-source inventory only. Never loads or evaluates held-out tasks."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, subprocess, sys

STATUS='STATIC_INVENTORY_INCOMPLETE_NOT_FROZEN_NO_HOLDOUT'
EXCLUDE_PREFIXES=('runs/','.git/','venv/','.venv/')
PROPOSED=set(range(10000,10100))
PATTERNS=(('range',re.compile(r'\brange\(\s*(\d+)\s*(?:,\s*(\d+)\s*)?\)')),
          ('seed_literal',re.compile(r'\b(?:seed|seeds|random_state|rng_seed)\s*[:=]\s*(\d+)\b',re.I)))

def tracked_paths(root):
    raw=subprocess.check_output(['git','ls-files','-z'],cwd=root)
    return sorted(p.decode('utf-8') for p in raw.split(b'\0') if p and not p.decode('utf-8').startswith(EXCLUDE_PREFIXES))

def scan_text(path,content):
    findings=[]
    for kind,pat in PATTERNS:
        for m in pat.finditer(content):
            lo=int(m.group(1)); hi=int(m.group(2)) if kind=='range' and m.group(2) else (lo if kind=='range' else None)
            # range(end) => 0,...,end-1; range(start,end) => start,...,end-1
            if kind=='range':
                start,stop=(0,lo) if m.group(2) is None else (lo,hi)
                overlap=max(start,10000)<min(stop,10100)
                expression=m.group(0)
            else:
                overlap=lo in PROPOSED; expression=m.group(0)
            findings.append({'path':path,'line':content.count('\n',0,m.start())+1,'kind':kind,'expression':expression,'candidate_holdout_overlap':overlap})
    return findings

def inventory(root):
    root=pathlib.Path(root)
    paths=tracked_paths(root)
    scanned=[]; findings=[]; unreadable=[]
    for p in paths:
        if not p.endswith(('.py','.md','.json','.yaml','.yml','.toml','.txt')):continue
        try: txt=(root/p).read_text(encoding='utf-8')
        except (UnicodeError,OSError): unreadable.append(p);continue
        scanned.append(p);findings.extend(scan_text(p,txt))
    sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    if not re.fullmatch(r'[a-f0-9]{40}',sha):raise ValueError('invalid commit')
    # Files in this inventory contain no held-out data/labels; this is metadata only.
    return {'status':STATUS,'source_commit':sha,'python':sys.version.split()[0],
            'tracked_file_count':len(paths),'text_files_scanned':len(scanned),'unreadable':unreadable,
            'findings':findings,'potential_literal_overlaps':[f for f in findings if f['candidate_holdout_overlap']],
            'proposed_seed_count':len(PROPOSED),'development_seed_history_complete':False,
            'environment_locked':False,'independent_review_complete':False,
            'scored_validation_allowed':False,
            'limitations':['Static patterns are incomplete: dynamic seed generation, manual runs, prior commits and off-repository logs require human audit.',
                           'A code match is not evidence that a seed was used; absence of matches is not evidence of independence.',
                           'Python version is observed, not a locked full dependency environment.']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out-dir',default='runs/seed_environment_inventory_v1');args=parser.parse_args()
    root=pathlib.Path(__file__).resolve().parents[1];result=inventory(root)
    target=pathlib.Path(args.out_dir);target.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
    (target/'inventory.json').write_bytes(data)
    (target/'inventory.sha256').write_text(hashlib.sha256(data).hexdigest()+'  inventory.json\n')
    print(json.dumps({'status':STATUS,'scanned':len(result['findings']),'potential_overlaps':len(result['potential_literal_overlaps']),'scored_validation_allowed':False}))
if __name__=='__main__': main()
