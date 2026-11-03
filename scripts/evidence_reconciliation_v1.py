"""Reconcile pinned historical CI artifacts without accessing held-out labels."""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, re, urllib.request, urllib.error, zipfile, io
from urllib.parse import urlsplit

STATUS='HISTORICAL_EVIDENCE_RECONCILED_PARTIAL_NO_HOLDOUT'
REPO='busrakisik/inverse-materials-design'
SOURCES={
 'freeze':(13213742932,'7f91a72ae2db5c7f7f9cf17da9677abe8d6eaa5cd8ea188fe1dc1e075e5b993d','runs/validation_freeze_manifest_v1/freeze_evidence_manifest.json','2cb4126a2cd27b5d1c442f90e9af763865547f1b'),
 'environment':(13211390930,'822bea24d1c2d4afa0e75f9d5940fdd1279c3ad6f7f37e08456f4ad99fee15ae','runs/synthetic_environment_lock_v1/environment_manifest.json','30413f8f03c1ea310469820b952a4c735a48b440'),
 'history':(13161561259,'a2c0514dd2ce714acccaefbb99d3d9b1b3d0da2fc9eabbd7a2e9ff6de59aa742','runs/historical_actions_audit_v1/actions_history_metadata.json',None),
 'pilot':(13146289436,'5ec12d275e5bbbc0a321c29e88ea46aea40e4873447ccaa5c289b11cb2d7756e','runs/paired_pilot_v1/pilot_manifest.json',None),
 'inventory':(13160318234,'1f40ca9f21855ac53ddcbafc498ffdd156b2095bee47f8ac43707704ec6a3ff4','runs/seed_environment_inventory_v1/inventory.json','589cba8891f36a58d02a62e19a50a102e813fc73'),
}
MAX_ZIP=4_000_000
MAX_MEMBER=2_000_000

def digest(b):return hashlib.sha256(b).hexdigest()

def read_zip(blob, expected_digest, member):
 if len(blob)>MAX_ZIP or digest(blob)!=expected_digest:raise ValueError('artifact ZIP checksum/size mismatch')
 with zipfile.ZipFile(io.BytesIO(blob)) as z:
  entries=z.infolist()
  if len(entries)>100 or len({e.filename for e in entries})!=len(entries):raise ValueError('unsafe/ambiguous archive')
  if member not in z.namelist():raise ValueError('missing required manifest: '+member)
  for e in entries:
   if e.file_size>MAX_MEMBER or e.flag_bits&1 or e.filename.startswith('/') or '..' in pathlib.PurePosixPath(e.filename).parts:
    raise ValueError('unsafe archive entry')
  content=z.read(member)
  if len(content)>MAX_MEMBER:raise ValueError('manifest oversized')
  result=json.loads(content)
  if not isinstance(result,dict):raise ValueError('manifest not object')
  return result,digest(content)

def reconcile(blobs):
 if set(blobs)!=set(SOURCES):raise ValueError('all five pinned archives required')
 records={}; docs={}
 for name,(artifact_id,expected,member,sha) in SOURCES.items():
  obj,inner=read_zip(blobs[name],expected,member)
  if sha and obj.get('current_commit',obj.get('commit',obj.get('source_commit')))!=sha:
   raise ValueError('commit provenance mismatch: '+name)
  docs[name]=obj
  records[name]={'artifact_id':artifact_id,'zip_sha256':expected,'manifest_sha256':inner,'manifest_path':member,'source_commit':sha,'verified_zip_bytes':True}
 freeze,env,history,pilot,inv=(docs[k] for k in ('freeze','environment','history','pilot','inventory'))
 common=set(freeze.get('source_sha256',{})) & set(env.get('source_sha256',{}))
 if len(common)!=3:raise ValueError('missing shared source hashes')
 matched={p:freeze['source_sha256'][p]==env['source_sha256'][p] for p in sorted(common)}
 if not all(matched.values()):raise ValueError('source contents inconsistent across commits')
 if env.get('python_exact')!='3.11.9' or env.get('environment_fully_hermetic') is not False:raise ValueError('environment scope mismatch')
 if history.get('pagination_complete') is not True or not isinstance(history.get('runs_observed'),int):raise ValueError('incomplete workflow metadata')
 if pilot.get('n_rows')!=1800 or pilot.get('n_pairs')!=30 or pilot.get('confirmatory') is not False:raise ValueError('pilot manifest invalid')
 if freeze.get('scored_validation_allowed') is not False or inv.get('scored_validation_allowed') is not False:raise ValueError('unexpected validation approval')
 pil_member='runs/paired_pilot_v1/pilot_raw.jsonl'
 with zipfile.ZipFile(io.BytesIO(blobs['pilot'])) as z:
  raw=z.read(pil_member)
  if len(raw)>MAX_MEMBER:raise ValueError('raw pilot oversized')
  rows=[json.loads(line) for line in raw.splitlines() if line]
 if len(rows)!=1800:raise ValueError('raw pilot count mismatch')
 seeds={r['seed'] for r in rows if type(r.get('seed')) is int}
 if len(seeds)!=30 or seeds!=set(range(30)):raise ValueError('pilot seeds mismatch')
 if len({(r.get('seed'),r.get('scenario'),r.get('budget'),r.get('policy')) for r in rows})!=1800:raise ValueError('duplicate/unpaired pilot rows')
 proposed=freeze.get('candidate_holdout_seeds')
 if proposed!=list(range(10000,10100)):raise ValueError('proposed seed definition changed')
 return {'status':STATUS,'artifacts':records,'shared_source_hashes_agree':matched,
  'distinct_provenance_commits':sorted({s[3] for s in SOURCES.values() if s[3]}),
  'historical_actions_runs_observed':history['runs_observed'],
  'pilot_raw_rows_verified':len(rows),'pilot_seeds_verified':sorted(seeds),
  'pilot_vs_candidate_seed_overlap':sorted(seeds & set(proposed)),
  'python_patch_observed':env['python_exact'],'environment_fully_hermetic':False,
  'all_historical_local_external_seed_uses_excluded':False,
  'independent_label_boundary_review_completed':False,
  'pre_outcome_frozen_approval':False,'scored_validation_allowed':False,
  'holdout_tasks_generated':False,'holdout_outcomes_seen':False,
  'limitations':['Evidence pertains to multiple commits; equal core module hashes do not prove whole-tree identity.',
   'The pilot artifact establishes only its own executed seeds, not all historical runs.',
   'Artifact and manifest hashes establish byte identity, not independent reviewer approval.',
   'No real materials validation or independent synthetic holdout has been performed.']}

class _NoRedirect(urllib.request.HTTPRedirectHandler):
 """Return redirects to caller; never forward API credentials to blob storage."""
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  return None

def _trusted_artifact_host(host):
 host=(host or '').lower()
 return host == 'objects.githubusercontent.com' or host.endswith('.actions.githubusercontent.com') or host.endswith('.blob.core.windows.net')

def _read_bounded(response):
 content=response.read(MAX_ZIP+1)
 if len(content)>MAX_ZIP:raise ValueError('ZIP too large')
 return content

def download_artifact(id,token,*,opener=None):
 """Authenticate only GitHub API; fetch signed blob separately with NO Authorization."""
 if not token:raise ValueError('GitHub token required in CI')
 if type(id) is not int or id<=0:raise ValueError('invalid artifact id')
 opener=opener if opener is not None else urllib.request.build_opener(_NoRedirect())
 api=f'https://api.github.com/repos/{REPO}/actions/artifacts/{id}/zip'
 req=urllib.request.Request(api,headers={'Authorization':'Bearer '+token,
    'Accept':'application/vnd.github+json','User-Agent':'BHS-evidence-reconciliation-v1'})
 try:
  with opener.open(req,timeout=30) as resp:
   return _read_bounded(resp)
 except urllib.error.HTTPError as exc:
  if exc.code not in (301,302,303,307,308):
   raise RuntimeError(f'GitHub artifact API request failed (HTTP {exc.code}); check actions:read and artifact retention') from None
  location=exc.headers.get('Location','')
  parsed=urlsplit(location)
  if parsed.scheme!='https' or parsed.username or parsed.password or not _trusted_artifact_host(parsed.hostname):
   raise ValueError('untrusted artifact redirect destination') from None
 # Build a fresh credential-free request. Do NOT reuse req or opener proxy auth.
 blob_req=urllib.request.Request(location,headers={'User-Agent':'BHS-evidence-reconciliation-v1'})
 try:
  with opener.open(blob_req,timeout=30) as resp:
   return _read_bounded(resp)
 except urllib.error.HTTPError as exc:
  raise RuntimeError(f'Artifact blob request failed (HTTP {exc.code}); signed link may be expired') from None

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--local-dir',type=pathlib.Path,help='Folder of artifact-<id>.zip, otherwise download from GitHub')
 ap.add_argument('--out-dir',type=pathlib.Path,default=pathlib.Path('runs/evidence_reconciliation_v1'))
 args=ap.parse_args()
 blobs={}
 for name,(artifact_id,*_) in SOURCES.items():
  if args.local_dir:
   p=args.local_dir/f'artifact-{artifact_id}.zip';blobs[name]=p.read_bytes()
  else:blobs[name]=download_artifact(artifact_id,os.getenv('GITHUB_TOKEN'))
 report=reconcile(blobs);args.out_dir.mkdir(parents=True,exist_ok=True)
 raw=(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
 (args.out_dir/'reconciliation.json').write_bytes(raw)
 (args.out_dir/'reconciliation.sha256').write_text(digest(raw)+'  reconciliation.json\n',encoding='utf-8')
 print(json.dumps({'status':STATUS,'artifacts_verified':len(SOURCES),'pilot_rows':report['pilot_raw_rows_verified'],
   'shared_source_hashes_agree':all(report['shared_source_hashes_agree'].values()),'scored_validation_allowed':False},sort_keys=True))
if __name__=='__main__':main()
