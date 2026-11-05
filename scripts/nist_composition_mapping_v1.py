"""NIST Fe-Co-Ni composition/target shape contract (DESCRIPTIVE ONLY).

This is deliberately NOT a BHS fit, hypothesis test, scored benchmark, or
validation of chemical column identities. The pinned source is fetched only
when explicitly requested. Raw sample rows are NEVER exported.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from scipy.io import loadmat

from scripts.nist_dataset_inspection_v1 import (
    FIELDS, SOURCE_COMMIT, SOURCE_GIT_BLOB, SOURCE_SIZE, SOURCE_URL,
    fetch_source, validate_source,
)

STATUS = 'BHS_NIST_COMPOSITION_MAPPING_DESCRIPTIVE_ONLY'
TARGETS = ('Coer', 'Kerr')
TOL = 0.02


def _numeric_real(a, name):
    if not isinstance(a, np.ndarray) or not np.issubdtype(a.dtype, np.number) or np.iscomplexobj(a):
        raise ValueError(name + ' must be real numeric ndarray')
    try:
        return np.asarray(a, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError('cannot convert ' + name) from exc


def normalize_composition_axis(a):
    """Require one unambiguous Nx3 or 3xN orientation, N>3.

    Output has NO Fe/Co/Ni labels: column positions 0,1,2 are opaque.
    """
    a = _numeric_real(a, 'C')
    if a.ndim != 2:
        raise ValueError('composition array must be two-dimensional')
    if a.shape[0] > 3 and a.shape[1] == 3:
        return a, 'rows_are_samples'
    if a.shape[1] > 3 and a.shape[0] == 3:
        return a.T, 'columns_are_samples'
    raise ValueError('ambiguous or incompatible composition orientation')


def target_vector(a, n, name):
    """Permit only a scalar per sample, disallow accidental many-column flattening."""
    a = _numeric_real(a, name)
    if a.shape == (n,) or a.shape == (n, 1) or a.shape == (1, n):
        return a.reshape(n)
    raise ValueError('target is not aligned as one scalar per composition')


def summarize_arrays(arrays):
    if type(arrays) is not dict or set(arrays) != set(FIELDS):
        raise ValueError('source MATLAB field set mismatch')
    for k in FIELDS:
        if not isinstance(arrays[k], np.ndarray):
            raise ValueError('all MATLAB fields must be ndarrays')
    for k in ('C','Coer','Kerr'):
        _numeric_real(arrays[k], k)
    comp, orientation = normalize_composition_axis(arrays['C'])
    n = int(comp.shape[0])
    finite_rows = np.isfinite(comp).all(axis=1)
    rows = comp[finite_rows]
    sums = np.sum(rows, axis=1)
    near_one = np.isclose(sums, 1., rtol=0., atol=TOL)
    near_hundred = np.isclose(sums, 100., rtol=0., atol=100*TOL)
    nonnegative = np.all(rows >= 0., axis=1)
    near_fraction = near_one & nonnegative & np.all(rows <= 1.+TOL, axis=1)
    near_percentage = near_hundred & nonnegative & np.all(rows <= 100.+100*TOL, axis=1)
    fraction_row_mask = np.zeros(n, dtype=bool)
    fraction_row_mask[np.flatnonzero(finite_rows)] = near_fraction
    targets = {}
    for name in TARGETS:
        v = target_vector(arrays[name], n, name)
        ok = np.isfinite(v)
        both = ok & finite_rows
        vals = v[ok]
        targets[name] = {
            'raw_shape': list(arrays[name].shape),
            'finite_count': int(ok.sum()),
            'missing_or_nonfinite_count': int((~ok).sum()),
            'joint_finite_composition_count': int(both.sum()),
            'joint_fraction_like_composition_count': int(np.count_nonzero(both & fraction_row_mask)),
            'min_finite': float(vals.min()) if vals.size else None,
            'max_finite': float(vals.max()) if vals.size else None,
            'unit': 'mT' if name=='Coer' else 'mrad',
            'per_sample_uncertainty_known': False,
        }
    xrd = arrays['XRD']
    tth = arrays['TTH']
    # Descriptive shape checks; no implicit matching XRD angle axes to C rows.
    xrd_sample_axis_candidates = [i for i, size in enumerate(xrd.shape) if size == n]
    tth_broadcasting_verified = False
    is_definite_fraction = bool(finite_rows.all() and near_fraction.all())
    is_definite_percent = bool(finite_rows.all() and near_percentage.all())
    return {
        'status': STATUS,
        'source_file_version_pinned': True,
        'samples_inferred': n,
        'composition': {
            'source_shape': list(arrays['C'].shape),
            'orientation': orientation,
            'anonymous_columns': ['source_col_0','source_col_1','source_col_2'],
            'finite_rows': int(finite_rows.sum()),
            'nonfinite_rows': int((~finite_rows).sum()),
            'nonnegative_finite_rows': int(nonnegative.sum()),
            'rows_sum_near_1': int(near_one.sum()),
            'rows_sum_near_100': int(near_hundred.sum()),
            'fraction_like_rows': int(near_fraction.sum()),
            'percentage_like_rows': int(near_percentage.sum()),
            'fraction_like_all_rows': is_definite_fraction,
            'percentage_like_all_rows': is_definite_percent,
            'element_order_verified': False,
            'scale_authoritatively_verified': False,
            'per_row_sample_ids_verified': False,
        },
        'targets': targets,
        'xrd': {'shape': list(xrd.shape), 'candidate_sample_axes':xrd_sample_axis_candidates,
                'sample_axis_authoritatively_verified':False},
        'tth': {'shape': list(tth.shape), 'xrd_axis_alignment_verified': tth_broadcasting_verified},
        'model_contract': {
            'model_input_order': ['Fe', 'Co', 'Ni'],
            'source_columns_mapped_to_model': False,
            'mapping_blocked_reason': 'source elemental column order and scale not authoritatively verified',
            'candidate_response_fit_performed':False,
            'scientific_hypotheses_validated':False,
            'observation_sigma_available':False,
            'actual_experiment_cost_available':False,
        },
        'dataset_ready_for_bhs':False,
        'real_data_experiment_executed':False,
        'physical_validation':False,
        'independent_holdout_used':False,
        'scored_validation_allowed':False,
        'claim_of_superiority':False,
    }


def inspect_source_bytes(raw):
    digest = validate_source(raw)
    data = loadmat(io.BytesIO(raw))
    arrays = {k:v for k,v in data.items() if not k.startswith('__')}
    result = summarize_arrays(arrays)
    result['source'] = {'url':SOURCE_URL,'commit':SOURCE_COMMIT,
                        'git_blob_sha1':SOURCE_GIT_BLOB,'size_bytes':SOURCE_SIZE,
                        'sha256':digest}
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--fetch', action='store_true')
    p.add_argument('--input',type=Path)
    p.add_argument('--out-dir',type=Path,default=Path('runs/nist_composition_mapping_v1'))
    args=p.parse_args()
    if args.fetch == bool(args.input):
        p.error('provide exactly one of --fetch and --input')
    raw=fetch_source() if args.fetch else args.input.read_bytes()
    result=inspect_source_bytes(raw)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    payload=(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    (args.out_dir/'mapping_readiness.json').write_bytes(payload)
    (args.out_dir/'mapping_readiness.sha256').write_text(
        hashlib.sha256(payload).hexdigest()+'  mapping_readiness.json\n')
    print(json.dumps({'status':STATUS,'samples_inferred':result['samples_inferred'],
                      'source_columns_mapped_to_model':False,
                      'scored_validation_allowed':False},sort_keys=True))

if __name__=='__main__': main()
