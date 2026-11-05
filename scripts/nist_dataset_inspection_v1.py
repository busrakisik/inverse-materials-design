"""NIST Fe-Co-Ni MAT-file inspection: metadata/quality only; no BHS evaluation.

Downloads pinned NIST source ONLY on explicit --fetch. Verifies Git blob SHA-1
and exact byte count; does not redistribute the source or export raw rows.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import urllib.request
from pathlib import Path

import numpy as np
from scipy.io import loadmat

STATUS = "NIST_REAL_FILE_DESCRIPTIVE_INSPECTION_NOT_BENCHMARKED"
SOURCE_COMMIT = "596b04435fb577175264a70c4434f5539b809510"
SOURCE_GIT_BLOB = "e506db115d522d62618042abead7df2695ccf13e"
SOURCE_SIZE = 289480
SOURCE_URL = ("https://raw.githubusercontent.com/usnistgov/remi/" + SOURCE_COMMIT
              + "/data/Combinatorial%20Libraries/Fe-Co-Ni/FeCoNi_benchmark_dataset_220501a.mat")
FIELDS = ("C", "XRD", "TTH", "Coer", "Kerr")
MAX_BYTES = 2_000_000


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def validate_source(raw: bytes) -> str:
    if not isinstance(raw, bytes) or len(raw) != SOURCE_SIZE:
        raise ValueError("NIST source size mismatch")
    if git_blob_sha1(raw) != SOURCE_GIT_BLOB:
        raise ValueError("NIST pinned Git blob mismatch")
    return hashlib.sha256(raw).hexdigest()


def fetch_source():
    """Bounded, fail-closed fetch; downloads are not committed or archived."""
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent":"BHS-NIST-inspection-v1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("download size bound exceeded")
    validate_source(raw)
    return raw


def _stats(arr):
    if not np.issubdtype(arr.dtype, np.number):
        return {"numeric": False, "shape": list(arr.shape), "dtype": str(arr.dtype)}
    if np.iscomplexobj(arr):
        return {"numeric": False, "shape": list(arr.shape), "dtype": str(arr.dtype),
                "reason": "complex values unsupported"}
    x = np.asarray(arr, dtype=np.float64)
    finite = np.isfinite(x)
    values = x[finite]
    return {"numeric": True, "shape": list(x.shape), "dtype": str(arr.dtype),
            "count": int(x.size), "finite": int(finite.sum()),
            "nan": int(np.isnan(x).sum()), "posinf": int(np.isposinf(x).sum()),
            "neginf": int(np.isneginf(x).sum()),
            "min_finite": float(values.min()) if values.size else None,
            "max_finite": float(values.max()) if values.size else None,
            "median_finite": float(np.median(values)) if values.size else None}


def inspect_arrays(fields: dict) -> dict:
    if type(fields) is not dict or set(fields) != set(FIELDS):
        raise ValueError("unexpected or missing MATLAB fields")
    if any(not isinstance(fields[k], np.ndarray) for k in FIELDS):
        raise ValueError("all dataset fields must be numpy arrays")
    profiles = {k: _stats(fields[k]) for k in FIELDS}
    c = fields["C"]
    c_orientation = ("samples_by_three_columns" if c.ndim == 2 and c.shape[1] == 3
                     else "three_rows_by_samples" if c.ndim == 2 and c.shape[0] == 3
                     else "unresolved")
    samples = int(c.shape[0] if c_orientation == "samples_by_three_columns" else
                  c.shape[1]) if c_orientation != "unresolved" else None
    comp = c if c_orientation == "samples_by_three_columns" else c.T if c_orientation == "three_rows_by_samples" else None
    comp_summary = {"orientation": c_orientation, "inferred_sample_count": samples,
                    "element_column_order_verified": False, "fraction_or_percent_verified": False,
                    "sum_closeness_is_diagnostic_not_a_unit_certification": True}
    if comp is not None and np.issubdtype(comp.dtype, np.number) and not np.iscomplexobj(comp):
        z = np.asarray(comp, dtype=float)
        mask = np.isfinite(z).all(axis=1)
        sums = z[mask].sum(axis=1)
        comp_summary.update({"complete_rows": int(mask.sum()),
                             "nonnegative_complete_rows": int(np.sum((z[mask] >= 0).all(axis=1))),
                             "sum_near_one_rows": int(np.sum(np.isclose(sums, 1, atol=.02, rtol=0))),
                             "sum_near_hundred_rows": int(np.sum(np.isclose(sums, 100, atol=2, rtol=0)))})
    targets = {}
    for key in ("Coer", "Kerr"):
        a = fields[key]
        targets[key] = {"shape": list(a.shape),
                        "sample_axis_alignment_possible": samples is not None and samples in a.shape,
                        "measurement_error_per_row_documented": False}
    return {"status": STATUS, "fields": profiles, "composition": comp_summary,
            "targets": targets, "documented_measurement_units": {"Coer": "mT", "Kerr": "mrad"},
            "source_description_field_mapping_only": True,
            "source_file_version_pinned": True,
            "source_license_and_redistribution_cleared": False,
            "independent_holdout_used": False, "scored_validation_allowed": False,
            "real_data_experiment_executed": False, "physical_validation": False,
            "measured_experiment_costs_verified": False,
            "dataset_ready_for_bhs": False, "claim_of_superiority": False}


def inspect_bytes(raw):
    sha = validate_source(raw)
    import io
    data = loadmat(io.BytesIO(raw))
    arrays = {k: v for k, v in data.items() if not k.startswith("__")}
    report = inspect_arrays(arrays)
    report["source"] = {"url": SOURCE_URL, "commit": SOURCE_COMMIT,
                       "git_blob_sha1": SOURCE_GIT_BLOB, "size_bytes": len(raw),
                       "content_sha256": sha}
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="Explicitly download pinned NIST data")
    parser.add_argument("--input", type=Path, help="Local .mat (same pinned bytes only)")
    parser.add_argument("--out-dir", type=Path, default=Path("runs/nist_dataset_inspection_v1"))
    args = parser.parse_args()
    if args.fetch == bool(args.input):
        parser.error("provide exactly one of --fetch or --input")
    raw = fetch_source() if args.fetch else args.input.read_bytes()
    report = inspect_bytes(raw)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    (args.out_dir / "descriptive_inspection.json").write_bytes(payload)
    (args.out_dir / "descriptive_inspection.sha256").write_text(
        hashlib.sha256(payload).hexdigest() + "  descriptive_inspection.json\n")
    print(json.dumps({"status": STATUS, "sample_count_inferred":
                      report["composition"]["inferred_sample_count"],
                      "scored_validation_allowed": False, "dataset_ready_for_bhs": False}, sort_keys=True))


if __name__ == "__main__":
    main()
