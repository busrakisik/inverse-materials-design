"""Metadata inventory and bounded local archive evidence extraction; never evaluates holdouts."""
from __future__ import annotations
import argparse, csv, hashlib, json, os, pathlib, re, urllib.request, zipfile
STATUS = 'PARTIAL_ARTIFACT_EVIDENCE_NO_HOLDOUT_APPROVAL'
API='https://api.github.com/repos/{repo}/actions/artifacts?per_page=100&page={page}'
MAX_FILE=8_000_000
MAX_TOTAL=30_000_000
ALLOWED=('.json','.jsonl','.csv','.txt')
SEED_KEYS={'seed','task_seed','random_seed','rng_seed','random_state'}

def inventory(repo, token=None, opener=None):
    if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]*/[A-Za-z0-9_][A-Za-z0-9_.-]*',repo): raise ValueError('invalid repo')
    opener=opener or urllib.request.urlopen
    rows=[]; expected=None; complete=False
    for page in range(1,31):
        req=urllib.request.Request(API.format(repo=repo,page=page),headers={'Accept':'application/vnd.github+json','User-Agent':'BHS-artifact-evidence-v1',**({'Authorization':'Bearer '+token} if token else {})})
        with opener(req,timeout=20) as resp: obj=json.load(resp)
        if not isinstance(obj,dict) or not isinstance(obj.get('artifacts'),list):raise ValueError('invalid API response')
        if expected is None: expected=obj.get('total_count')
        for a in obj['artifacts']:
            rows.append({'id':a.get('id'),'name':a.get('name'),'expired':a.get('expired'),'size_in_bytes':a.get('size_in_bytes'),'run_id':(a.get('workflow_run') or {}).get('id'),'created_at':a.get('created_at')})
        if len(rows)==expected:complete=True;break
        if len(obj['artifacts'])<100:break
    if len(set(a['id'] for a in rows))!=len(rows):raise ValueError('duplicate artifact ids')
    return {'status':STATUS,'repo':repo,'api_total':expected,'count':len(rows),'pagination_complete':complete,'artifacts':rows,'seed_usage_fully_verified':False,'scored_validation_allowed':False}

def seed_values(obj):
    found=[]
    def walk(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k.lower() in SEED_KEYS and type(v) is int:found.append(v)
                if isinstance(v,(dict,list)):walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(obj)
    return found

def scan_zip(path):
    records=[]; warnings=[]; total=0
    with zipfile.ZipFile(path) as z:
        names=z.infolist()
        if len(names)>500:raise ValueError('too many ZIP entries')
        for item in names:
            if item.is_dir() or not item.filename.lower().endswith(ALLOWED):continue
            name=pathlib.PurePosixPath(item.filename)
            if name.is_absolute() or '..' in name.parts:raise ValueError('unsafe archive path')
            if item.file_size>MAX_FILE:raise ValueError('file size limit exceeded')
            total+=item.file_size
            if total>MAX_TOTAL:raise ValueError('archive size limit exceeded')
            with z.open(item) as f:data=f.read(MAX_FILE+1)
            if len(data)>MAX_FILE:raise ValueError('decompression limit exceeded')
            try:content=data.decode('utf-8')
            except UnicodeDecodeError:warnings.append({'entry':item.filename,'reason':'non_utf8'});continue
            try:
                if item.filename.lower().endswith('.json'):values=seed_values(json.loads(content))
                elif item.filename.lower().endswith('.jsonl'):
                    values=[]
                    for line in content.splitlines():
                        if line.strip():values.extend(seed_values(json.loads(line)))
                elif item.filename.lower().endswith('.csv'):
                    import io
                    values=[]
                    for row in csv.DictReader(io.StringIO(content)):
                        for k,v in row.items():
                            if k and k.lower() in SEED_KEYS and v and re.fullmatch(r'-?\d+',v.strip()):values.append(int(v.strip()))
                else:values=[];warnings.append({'entry':item.filename,'reason':'unstructured_text_not_proof'})
                records.append({'entry':item.filename,'seeds':sorted(set(values)),'seed_mentions':len(values)})
            except (ValueError,TypeError,csv.Error):
                warnings.append({'entry':item.filename,'reason':'parse_error'})
    observed=sorted(set(s for r in records for s in r['seeds']))
    overlaps=sorted(set(observed)&set(range(10000,10100)))
    return {'archive':pathlib.Path(path).name,'sha256':hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest(),
            'entries_scanned':records,'observed_seeds':observed,'proposed_seed_overlaps':overlaps,'warnings':warnings,
            'evidence_scope':'ONLY_SUPPLIED_ARCHIVE_STRUCTURED_FILES','all_historical_runs_covered':False,
            'scored_validation_allowed':False,'status':STATUS}

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',default='busrakisik/inverse-materials-design');p.add_argument('--zip',action='append',default=[]);p.add_argument('--out-dir',default='runs/historical_artifact_evidence_v1');p.add_argument('--skip-api',action='store_true');a=p.parse_args()
    result={'status':STATUS,'artifact_inventory':None if a.skip_api else inventory(a.repo,os.getenv('GITHUB_TOKEN')),
            'archives':[scan_zip(q) for q in a.zip], 'scored_validation_allowed':False,
            'limitations':['Only supplied local ZIP archives are scanned for seeds; this does not establish all historical seed use.','GitHub artifact listings are metadata, not seed evidence.','No holdout tasks or labels are accessed.']}
    out=pathlib.Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode()
    (out/'artifact_evidence.json').write_bytes(raw)
    (out/'artifact_evidence.sha256').write_text(hashlib.sha256(raw).hexdigest()+'  artifact_evidence.json\n')
    print(json.dumps({'status':STATUS,'archives_scanned':len(a.zip),'scored_validation_allowed':False}))
if __name__=='__main__': main()
