#!/usr/bin/env python3
"""Controlled Matbench expt-gap acquisition. NOT a benchmark or license clearance."""
from __future__ import annotations
import argparse, gzip, hashlib, json, math, pathlib, urllib.request
from urllib.parse import urlparse

SOURCE = 'https://ml.materialsproject.org/projects/matbench_expt_gap.json.gz'
EXPECTED_COLUMNS = ('composition', 'gap expt')
MAX_BYTES = 12_000_000


def read_table(raw: bytes):
    try:
        expanded = gzip.decompress(raw)
        if len(expanded) > 40_000_000:
            raise ValueError('decompressed data exceeds safety limit')
        obj = json.loads(expanded)
    except (OSError, ValueError, UnicodeError) as exc:
        raise ValueError('invalid compressed JSON') from exc
    if isinstance(obj, dict) and {'columns', 'data'} <= obj.keys():
        cols = obj['columns']
        if len(cols) != len(set(cols)) or not set(EXPECTED_COLUMNS) <= set(cols):
            raise ValueError('unexpected or duplicate columns')
        ic, ig = cols.index('composition'), cols.index('gap expt')
        rows = [(row[ic], row[ig]) for row in obj['data'] if isinstance(row, list) and len(row) == len(cols)]
        if len(rows) != len(obj['data']):
            raise ValueError('malformed table row')
        return rows, cols
    if isinstance(obj, list) and all(isinstance(x, dict) for x in obj):
        if not all(set(EXPECTED_COLUMNS) <= x.keys() for x in obj):
            raise ValueError('missing expected columns')
        return [(x['composition'], x['gap expt']) for x in obj], list(obj[0]) if obj else []
    raise ValueError('unrecognized Matbench JSON table schema')


def inspect(raw: bytes):
    rows, columns = read_table(raw)
    if len(rows) != 4604:
        raise ValueError(f'expected 4604 rows, got {len(rows)}')
    invalid = []
    unique_formulas = set()
    for i, (formula, gap) in enumerate(rows):
        if not isinstance(formula, str) or not formula.strip() or isinstance(gap, bool) or not isinstance(gap, (float, int)) or not math.isfinite(float(gap)) or gap < 0:
            invalid.append(i)
        else:
            unique_formulas.add(formula.strip())
    if invalid:
        raise ValueError(f'{len(invalid)} invalid records, first positions {invalid[:8]}')
    return {'source_url': SOURCE, 'dataset': 'matbench_expt_gap', 'dataset_release': 'Matbench v0.1', 'status': 'RAW_FILE_AND_SCHEMA_VERIFIED_LICENSE_NOT_CLEARED', 'download_sha256': hashlib.sha256(raw).hexdigest(), 'download_bytes': len(raw), 'rows': len(rows), 'columns': columns, 'label_unit': 'eV', 'unique_formula_strings': len(unique_formulas), 'formula_duplicates_by_exact_string': len(rows) - len(unique_formulas), 'labels_exposed_to_policy': False, 'split_created': False, 'benchmark_run': False, 'license_review': 'PENDING_MANUAL_VERIFICATION', 'citation': 'Zhuo et al. (2018), DOI 10.1021/acs.jpclett.8b00124; Dunn et al. (2020), DOI 10.1038/s41524-020-00406-3'}


def acquire():
    req = urllib.request.Request(SOURCE, headers={'User-Agent': 'BHS-Research-Data-Audit/1.0'})
    with urllib.request.urlopen(req, timeout=35) as r:
        final = urlparse(r.geturl())
        if final.scheme != 'https' or final.hostname != 'ml.materialsproject.org':
            raise ValueError('unexpected redirect host')
        buf = r.read(MAX_BYTES + 1)
    if len(buf) > MAX_BYTES:
        raise ValueError('download exceeds safety limit')
    return buf


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out-dir', required=True)
    p.add_argument('--execute', action='store_true', help='authorizes real network download')
    args = p.parse_args()
    if not args.execute:
        p.error('pass --execute for a real, manual download')
    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'acquisition_manifest.json'
    if path.exists():
        p.error('refusing to overwrite an existing acquisition manifest')
    try:
        raw = acquire()
        report = inspect(raw)
    except Exception as exc:
        report = {'status': 'ACQUISITION_FAILED', 'source_url': SOURCE, 'exception_type': type(exc).__name__, 'error': str(exc), 'license_review': 'PENDING_MANUAL_VERIFICATION', 'benchmark_run': False}
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        print(json.dumps(report, indent=2))
        raise SystemExit(1)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
