#!/usr/bin/env python3
"""Label-blind deterministic *chemical-system* split gate for Matbench expt_gap.

The element-set grouping is a first leakage control, NOT guaranteed independence
between structurally/chemically related materials or a benchmark evaluation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

EXPECTED_SOURCE_SHA = '783e7d1461eb83b00b2f2942da4b95fda5e58a0d1ae26b581c24cf8a82ca75b2'
EXPECTED_ROWS = 4604
SALT = 'BHS-MATBENCH-EXPT-GAP-CHEMSYS-SPLIT-V1-2026-11-01'
SPLITS = ('train', 'validation', 'test')


def _require_formula(formula: str, composition_factory) -> tuple[str, str]:
    if not isinstance(formula, str) or not formula.strip():
        raise ValueError('empty/nonstring composition')
    comp = composition_factory(formula)
    if not comp or not comp.elements:
        raise ValueError('empty/unparseable chemical composition')
    elements = tuple(sorted(str(e) for e in comp.elements))
    if not elements:
        raise ValueError('empty chemical system')
    return '-'.join(elements), str(comp.reduced_formula)


def build_manifest(formulas, *, source_sha256: str, composition_factory, salt: str = SALT,
                   expected_rows: int = EXPECTED_ROWS) -> dict:
    """Consumes composition strings only: no labels, estimators, or outcomes."""
    if source_sha256 != EXPECTED_SOURCE_SHA:
        raise ValueError('raw compressed dataset SHA-256 does not match verified acquisition')
    if not isinstance(salt, str) or salt != SALT:
        raise ValueError('split salt must match preregistered constant')
    if not isinstance(formulas, (list, tuple)) or len(formulas) != expected_rows:
        raise ValueError('unexpected row count')
    if isinstance(expected_rows, bool) or expected_rows < 3:
        raise ValueError('invalid expected row count')
    groups = {}
    normalized = {}
    for index, formula in enumerate(formulas):
        group, reduced = _require_formula(formula, composition_factory)
        if reduced in normalized:
            raise ValueError('duplicate reduced formula: review duplicates before splitting')
        normalized[reduced] = index
        groups.setdefault(group, []).append(index)
    if len(groups) < 3:
        raise ValueError('insufficient distinct chemical systems for split')
    # Group assignment only depends on the fixed salt and unordered element set.
    # A single group can be large, so row proportions are not guaranteed.
    membership = {}
    for group in sorted(groups):
        value = int.from_bytes(hashlib.sha256((salt + '|' + group).encode()).digest()[:8], 'big') / 2**64
        membership[group] = 'train' if value < .70 else 'validation' if value < .85 else 'test'
    counts = Counter(membership.values())
    if any(counts.get(part, 0) == 0 for part in SPLITS):
        raise ValueError('one partition has zero chemical systems; do not silently resample')
    partitions = {p: [] for p in SPLITS}
    for group, indices in groups.items():
        partitions[membership[group]].extend(indices)
    for p in SPLITS:
        partitions[p].sort()
    all_ids = sum((partitions[p] for p in SPLITS), [])
    if len(all_ids) != expected_rows or sorted(all_ids) != list(range(expected_rows)):
        raise AssertionError('row coverage or partition overlap failure')
    # IDs are deterministic hashes of normalized formula + row index, not labels.
    identities = {}
    for reduced, index in normalized.items():
        identities[index] = hashlib.sha256(f'{salt}|row|{index}|{reduced}'.encode()).hexdigest()
    report = {
      'status':'LABEL_BLIND_SPLIT_CREATED_NOT_BENCHMARK',
      'dataset':'matbench_expt_gap','dataset_version':'matbench_v0.1',
      'source_compressed_sha256':source_sha256,
      'grouping':'unordered_element_set_chemical_system',
      'grouping_limitation':'Element overlap and other chemical similarities may persist across groups; not family-disjoint or structural-disjoint proof',
      'split_algorithm':'sha256(salt|chemical_system), first 64 bits / 2**64; [0,.70) train, [.70,.85) validation, [.85,1) test',
      'split_salt':salt,
      'partitions':{p:{'row_count':len(partitions[p]),'chemical_system_count':counts[p],
                       'row_ids_sha256':[identities[i] for i in partitions[p]],'original_row_indices':partitions[p]}
                    for p in SPLITS},
      'label_accessed_by_splitter':False,'labels_in_manifest':False,
      'objective_frozen':False,'policy_tuning_authorized':False,'benchmark_run':False,
      'license_review':'PENDING_SOURCE_DATA_RIGHTS_REVIEW',
    }
    return report


def validate_manifest(m):
    partitions=m['partitions']
    idxs=[set(partitions[p]['original_row_indices']) for p in SPLITS]
    if any(a & b for i,a in enumerate(idxs) for b in idxs[i+1:]):
        raise ValueError('overlapping split indices')
    if len(set.union(*idxs))!=EXPECTED_ROWS:
        raise ValueError('missing rows')
    if m.get('label_accessed_by_splitter') is not False or m.get('benchmark_run') is not False:
        raise ValueError('unsafe research claim')
    return True


def main():
    p=argparse.ArgumentParser(description='Manual audited split generation; no policy training')
    p.add_argument('--output',required=True)
    p.add_argument('--execute',action='store_true')
    args=p.parse_args()
    if not args.execute:p.error('explicit --execute required')
    # Keep raw data in runner memory; archive only split manifest after review.
    from pymatgen.core import Composition
    from scripts.acquire_matbench_expt_gap import acquire, read_table
    raw=acquire()
    digest=hashlib.sha256(raw).hexdigest()
    rows,columns=read_table(raw)
    if list(columns)!=['composition','gap expt']:
        raise ValueError('unexpected source columns')
    # Discard label values immediately: only formula strings reach splitter.
    formulas=[row[0] for row in rows]
    del rows
    report=build_manifest(formulas,source_sha256=digest,composition_factory=Composition)
    validate_manifest(report)
    dest=Path(args.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():p.error('refuse overwriting existing manifest')
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'counts':{p:report['partitions'][p]['row_count'] for p in SPLITS},'output':str(dest)},indent=2))

if __name__=='__main__':main()
