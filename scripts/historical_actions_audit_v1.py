"""Read-only GitHub Actions metadata inventory; no holdout tasks or scores."""
import argparse, hashlib, json, os, pathlib, re, sys, urllib.request

STATUS = 'HISTORY_METADATA_ONLY_INCOMPLETE_NO_HOLDOUT'
API = 'https://api.github.com/repos/{repo}/actions/runs?per_page=100&page={page}'

def fetch_pages(repo, token=None, opener=None, max_pages=30):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('invalid repository')
    if max_pages < 1: raise ValueError('invalid page limit')
    opener = opener or urllib.request.urlopen
    rows=[]; total=None
    for page in range(1,max_pages+1):
        req=urllib.request.Request(API.format(repo=repo,page=page),headers={
            'Accept':'application/vnd.github+json','User-Agent':'BHS-historical-audit-v1',
            **({'Authorization': 'Bearer '+token} if token else {})})
        with opener(req,timeout=20) as response:
            data=json.load(response)
        if not isinstance(data,dict) or not isinstance(data.get('workflow_runs'),list):
            raise ValueError('invalid API response')
        if total is None: total=data.get('total_count')
        for r in data['workflow_runs']:
            rows.append({k:r.get(k) for k in ('id','name','path','event','head_sha','status','conclusion','created_at','run_started_at','updated_at','html_url')})
        if not data['workflow_runs']: break
        if isinstance(total,int) and len(rows)>=total:break
        if len(data['workflow_runs'])<100:break
    ids=[r['id'] for r in rows]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate run IDs')
    return {'source':'github_actions_rest_metadata','repo':repo,'api_total':total,'runs_observed':len(rows),
            'pagination_complete':isinstance(total,int) and len(rows)==total,
            'runs':rows,'status':STATUS,'holdout_labels_evaluated':False,
            'historical_seed_usage_verified':False,'all_local_runs_covered':False,
            'independent_validation_approved':False,
            'limitations':['Metadata cannot establish which seeds occurred inside arbitrary scripts or manual runs.',
              'Deleted/expired workflows, external systems, local runs and older provenance are not established.',
              'No GitHub artifacts or logs are downloaded by this stage.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',default='busrakisik/inverse-materials-design');p.add_argument('--out-dir',default='runs/historical_actions_audit_v1');args=p.parse_args()
    result=fetch_pages(args.repo,os.getenv('GITHUB_TOKEN'))
    out=pathlib.Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    (out/'actions_history_metadata.json').write_bytes(data)
    (out/'actions_history_metadata.sha256').write_text(hashlib.sha256(data).hexdigest()+'  actions_history_metadata.json\n')
    print(json.dumps({'status':STATUS,'runs_observed':result['runs_observed'],
        'pagination_complete':result['pagination_complete'],'independent_validation_approved':False}))
    if not result['pagination_complete']:raise SystemExit('Incomplete GitHub API pagination; metadata not complete')
if __name__=='__main__':main()
