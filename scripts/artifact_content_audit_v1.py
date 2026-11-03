"""Audit real synthetic pilot ZIP records, without evaluating new/holdout tasks."""
import argparse, hashlib, json, pathlib, zipfile

STATUS = 'PILOT_ARTIFACT_VERIFIED_ONLY_NO_HOLDOUT_APPROVAL'
EXPECTED_POLICIES = {'random','greedy','bayesian_only'}
EXPECTED_SCENARIOS = {'smooth','multimodal','uninformative','mismatched','duplicates'}
EXPECTED_BUDGETS = {1,2,5,10}
PROPOSED_HOLDOUT = set(range(10000,10100))
MAX_COMPRESSED = 20_000_000
MAX_UNCOMPRESSED = 120_000_000

def audit_zip(path):
    path = pathlib.Path(path)
    if not path.is_file() or path.stat().st_size > MAX_COMPRESSED: raise ValueError('missing or oversized archive')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with zipfile.ZipFile(path) as z:
        items = z.infolist()
        if len(items) > 1000 or sum(i.file_size for i in items) > MAX_UNCOMPRESSED: raise ValueError('oversized archive content')
        for i in items:
            if i.flag_bits & 1 or i.is_dir() and i.file_size: raise ValueError('unsupported archive entry')
        raw = [i for i in items if i.filename.endswith('/pilot_raw.jsonl')]
        manifest = [i for i in items if i.filename.endswith('/pilot_manifest.json')]
        if len(raw)!=1 or len(manifest)!=1: raise ValueError('expected pilot entries missing/ambiguous')
        rows=[]
        for b in z.read(raw[0]).splitlines():
            if not b.strip():continue
            r=json.loads(b)
            if not isinstance(r,dict) or type(r.get('seed')) is not int or type(r.get('budget')) is not int or type(r.get('scenario')) is not str or type(r.get('policy')) is not str:
                raise ValueError('malformed pilot row')
            rows.append(r)
        m=json.loads(z.read(manifest[0]))
    if not rows or len(rows)!=1800:raise ValueError('unexpected pilot cardinality')
    observed=set();seeds=set(); scenarios=set();budgets=set();policies=set()
    for r in rows:
        key=(r['scenario'],r['seed'],r['budget'],r['policy'])
        if key in observed:raise ValueError('duplicate paired record')
        observed.add(key);seeds.add(r['seed']);scenarios.add(r['scenario']);budgets.add(r['budget']);policies.add(r['policy'])
        if r.get('queries')!=r['budget'] or not isinstance(r.get('trace'),list) or len(r['trace'])!=r['budget']:
            raise ValueError('invalid query budget')
        ids=[x.get('candidate_id') for x in r['trace']]
        if len(ids)!=len(set(ids)):raise ValueError('repeated candidate')
    if scenarios!=EXPECTED_SCENARIOS or budgets!=EXPECTED_BUDGETS or policies!=EXPECTED_POLICIES or seeds!=set(range(30)):
        raise ValueError('unexpected pilot specification or seeds')
    if len(observed)!=len(scenarios)*len(seeds)*len(budgets)*len(policies):raise ValueError('unpaired runs')
    if m.get('n_rows')!=1800 or m.get('n_pairs')!=30 or m.get('confirmatory') is not False or m.get('synthetic_only') is not True:
        raise ValueError('manifest mismatch')
    return {'status':STATUS,'archive_sha256':digest,'archive_filename':path.name,'pilot_rows_verified':len(rows),
        'observed_task_seeds':sorted(seeds),'observed_seed_count':len(seeds),
        'proposed_holdout_seed_overlap':sorted(seeds & PROPOSED_HOLDOUT),
        'pilot_seed_disjoint_from_proposal':not bool(seeds & PROPOSED_HOLDOUT),
        'coverage':'ONLY_THIS_PILOT_ZIP','historical_seed_usage_completely_audited':False,
        'local_and_external_runs_audited':False,'environment_locked':False,
        'scored_validation_allowed':False,'scientific_claim':'SYNTHETIC_ONLY_NOT_CONFIRMATORY'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive',required=True);ap.add_argument('--out-dir',default='runs/artifact_content_audit_v1');a=ap.parse_args()
    record=audit_zip(a.archive);target=pathlib.Path(a.out_dir);target.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(record,indent=2,sort_keys=True)+'\n').encode();(target/'pilot_evidence_report.json').write_bytes(data)
    (target/'pilot_evidence_report.sha256').write_text(hashlib.sha256(data).hexdigest()+'  pilot_evidence_report.json\n')
    print(json.dumps({'status':STATUS,'rows':record['pilot_rows_verified'],'seeds':record['observed_seed_count'],'holdout_approved':False}))
if __name__=='__main__': main()
