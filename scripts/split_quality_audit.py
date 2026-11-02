"""BHS Matbench split quality audit: descriptive, label-free, no model results."""
from __future__ import annotations
import argparse, collections, hashlib, json, pathlib

SHA='783e7d1461eb83b00b2f2942da4b95fda5e58a0d1ae26b581c24cf8a82ca75b2'
SPLITS=('train','validation','test')

def inspect_split(manifest:dict, formulas:list[str], composition_factory, source_sha:str)->dict:
    if source_sha != SHA or manifest.get('source_compressed_sha256') != SHA:
        raise ValueError('source hash mismatch')
    if len(formulas)!=4604 or manifest.get('dataset')!='matbench_expt_gap':
        raise ValueError('dataset mismatch')
    if manifest.get('labels_in_manifest') is not False or manifest.get('label_accessed_by_splitter') is not False or manifest.get('benchmark_run') is not False:
        raise ValueError('unsafe manifest flags')
    assigned={}; groups={}; parts=manifest['partitions']
    for split in SPLITS:
        part=parts[split]; indices=part['original_row_indices']
        if len(indices)!=part['row_count'] or len(indices)!=len(set(indices)):
            raise ValueError('duplicate or inconsistent indices')
        for i in indices:
            if not isinstance(i,int) or isinstance(i,bool) or i<0 or i>=len(formulas) or i in assigned:
                raise ValueError('invalid or overlapping row index')
            assigned[i]=split
    if set(assigned)!=set(range(len(formulas))):
        raise ValueError('incomplete rows')
    for i,formula in enumerate(formulas):
        c=composition_factory(formula)
        els=tuple(sorted(str(x) for x in c.elements))
        if not els: raise ValueError('empty chemical system')
        groups.setdefault(els,collections.Counter())[assigned[i]]+=1
    if any(len(splits)>1 for splits in groups.values()):
        raise ValueError('chemical-system leakage')
    if any(sum(1 for s in groups.values() if p in s)!=parts[p]['chemical_system_count'] for p in SPLITS):
        raise ValueError('group count mismatch')
    group_hist=collections.Counter(sum(c.values()) for c in groups.values())
    split_group_sizes={p:[sum(c.values()) for c in groups.values() if p in c] for p in SPLITS}
    element_sets={p:set().union(*(set(g) for g,c in groups.items() if p in c)) for p in SPLITS}
    train_test_shared=element_sets['train'] & element_sets['test']
    largest=sorted(((len_total,'-'.join(g),next(iter(c))) for g,c in groups.items() for len_total in [sum(c.values())]),reverse=True)[:12]
    return {
      'status':'DESCRIPTIVE_SPLIT_AUDIT_NOT_BENCHMARK',
      'source_sha256':SHA,
      'counts':{p:{'rows':parts[p]['row_count'],'groups':parts[p]['chemical_system_count'],'max_group_size':max(split_group_sizes[p])} for p in SPLITS},
      'total_groups':len(groups),'group_size_histogram':dict(sorted(group_hist.items())),
      'largest_chemical_systems':[{'chemical_system':g,'rows':n,'partition':p} for n,g,p in largest],
      'element_count_by_partition':{p:len(element_sets[p]) for p in SPLITS},
      'shared_train_test_elements':len(train_test_shared),
      'train_test_element_jaccard':len(train_test_shared)/len(element_sets['train']|element_sets['test']),
      'chemical_system_overlap_across_partitions':0,
      'labels_read_by_auditor':False,'objective_frozen':manifest.get('objective_frozen',False),
      'benchmark_run':False,
      'limitation':'Element overlap remains possible; element-set isolation is not family- or structure-disjoint validation.'
    }

def main():
    pa=argparse.ArgumentParser();pa.add_argument('--manifest',required=True);pa.add_argument('--output',required=True);pa.add_argument('--execute',action='store_true');args=pa.parse_args()
    if not args.execute: pa.error('--execute required')
    from pymatgen.core import Composition
    from scripts.acquire_matbench_expt_gap import acquire, read_table
    raw=acquire();sha=hashlib.sha256(raw).hexdigest()
    if sha!=SHA:raise ValueError('source hash changed')
    rows,_=read_table(raw)
    formulas=[x[0] for x in rows];del rows
    manifest=json.loads(pathlib.Path(args.manifest).read_text())
    report=inspect_split(manifest,formulas,Composition,sha)
    dest=pathlib.Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():raise ValueError('refusing to overwrite report')
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
