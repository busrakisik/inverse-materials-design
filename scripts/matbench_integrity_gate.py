#!/usr/bin/env python3
"""Independently re-download and inspect Matbench expt_gap bytes; no results or raw-data publication."""
import argparse, collections, gzip, hashlib, json, math, pathlib, urllib.request
SOURCE='https://ml.materialsproject.org/projects/matbench_expt_gap.json.gz'
BASELINE='783e7d1461eb83b00b2f2942da4b95fda5e58a0d1ae26b581c24cf8a82ca75b2'
LIMIT=12_000_000

def parse(raw):
    if len(raw)>LIMIT: raise ValueError('compressed file exceeds bound')
    with gzip.GzipFile(fileobj=__import__('io').BytesIO(raw)) as f: expanded=f.read(40_000_001)
    if len(expanded)>40_000_000: raise ValueError('decompressed file exceeds bound')
    d=json.loads(expanded)
    if not isinstance(d,dict) or not isinstance(d.get('columns'),list) or not isinstance(d.get('data'),list): raise ValueError('unexpected schema')
    cols=d['columns']; rows=d['data']
    if cols!=['composition','gap expt'] or len(rows)!=4604: raise ValueError('unexpected columns or row count')
    for i,row in enumerate(rows):
        if not isinstance(row,list) or len(row)!=2 or not isinstance(row[0],str) or not row[0].strip() or isinstance(row[1],bool) or not isinstance(row[1],(int,float)) or not math.isfinite(row[1]) or row[1]<0: raise ValueError(f'invalid row {i}')
    return rows

def audit(raw, canonicalize=None):
    rows=parse(raw)
    raw_hash=hashlib.sha256(raw).hexdigest()
    strings=[x[0].strip() for x in rows]
    result={'status':'FILE_INTEGRITY_INSPECTED_NOT_BENCHMARK','source_url':SOURCE,'dataset':'matbench_expt_gap','expected_initial_download_sha256':BASELINE,'repeat_sha256':raw_hash,'same_bytes_as_first_download':raw_hash==BASELINE,'compressed_bytes':len(raw),'rows':len(rows),'distinct_exact_formula_strings':len(set(strings)),'exact_string_duplicate_rows':len(strings)-len(set(strings)),'license_status':'SOURCE_DATA_RIGHTS_REQUIRE_SEPARATE_REVIEW','raw_data_published':False,'split_created':False,'benchmark_run':False}
    if canonicalize is None:
        result['chemical_equivalence_status']='NOT_ASSESSED_REQUIRES_PYMATGEN'
    else:
        canonical=[];errors=[]
        for i,s in enumerate(strings):
            try:canonical.append(canonicalize(s))
            except Exception as e:errors.append({'row':i,'exception_type':type(e).__name__})
        result['chemical_equivalence_status']='CHECKED' if not errors else 'FAILED'
        result['unparseable_formula_count']=len(errors)
        result['unparseable_formula_first_rows']=errors[:10]
        if not errors:
            groups=collections.Counter(canonical)
            result['distinct_reduced_formulas']=len(groups)
            result['reduced_formula_duplicate_rows']=len(canonical)-len(groups)
            result['duplicate_group_sizes']=dict(collections.Counter(n for n in groups.values() if n>1))
    return result

def download():
    req=urllib.request.Request(SOURCE,headers={'User-Agent':'BHS-Integrity-Research/1.0'})
    with urllib.request.urlopen(req,timeout=35) as resp:
        if resp.geturl()!=SOURCE: raise ValueError('redirect requires explicit review')
        raw=resp.read(LIMIT+1)
    if len(raw)>LIMIT: raise ValueError('download exceeds bound')
    return raw

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');ap.add_argument('--output',required=True);args=ap.parse_args()
    if not args.execute: ap.error('explicit --execute required')
    out=pathlib.Path(args.output)
    if out.exists(): ap.error('refusing to overwrite prior audit')
    out.parent.mkdir(parents=True,exist_ok=True)
    try:
        from pymatgen.core import Composition
        def canonicalize(x):
            c=Composition(x)
            return c.reduced_composition.alphabetical_formula
        result=audit(download(),canonicalize)
        if not result['same_bytes_as_first_download']: result['status']='HASH_CHANGED_REQUIRES_REVIEW'
        if result['chemical_equivalence_status']!='CHECKED': result['status']='CANONICALIZATION_FAILED'
    except Exception as exc:
        result={'status':'AUDIT_FAILED','error_type':type(exc).__name__,'error':str(exc),'source_url':SOURCE,'benchmark_run':False,'raw_data_published':False}
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,sort_keys=True))
    if result['status']!='FILE_INTEGRITY_INSPECTED_NOT_BENCHMARK': raise SystemExit(1)
if __name__=='__main__':main()
