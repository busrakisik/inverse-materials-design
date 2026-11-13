"""Outcome-free V12.14 structural split feasibility and selection-time feature gate.

No segregation-energy numeric value is read, parsed, stored, or scored.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

from scripts.bhs_v1213_source_intake import (
    _missing, download_upstream, verify_source_bytes, FILE_NAME, UPSTREAM_COMMIT
)

EXPECTED_ROWS = 4289
EXPECTED_GB = 6
EXPECTED_ELEMENTS = 91
EXPECTED_MISSING_COMBINED = 110
EXPECTED_MISSING_TARGET = 30
REQUIRED = ("GB", "element", "Z", "site", "GB_site",
            "GB_element_site", "job_name", "E_seg")
BANNED_PREDICTION_COLUMNS = (
    "E_seg", "E_seg_unrel", "Wsep_RGS_min",
    "structure", "structure_unrel", "magmom_solute",
    "dist_GB", "convergence", "DDEC6_ANSBO_min",
)
GATES = {
    "development_only": True,
    "scored_validation_allowed": False,
    "independent_holdout_used": False,
    "physical_validation_by_bhs": False,
    "claim_of_superiority": False,
    "real_savings_measured": False,
    "statistical_guarantee_supported": False,
    "laboratory_action_allowed": False,
}


class SplitContractError(ValueError):
    pass


def extract_metadata(raw: bytes, require_original: bool = True) -> list[dict]:
    """Only primitive identifiers and TARGET BLANKNESS, no numeric labels."""
    if require_original:
        verify_source_bytes(raw)
    records = []
    identities = set()
    atom_by_element = {}
    combined_missing = 0
    blank_target = 0
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as stream:
            with io.TextIOWrapper(stream, encoding="utf-8", newline="") as handle:
                csv.field_size_limit(20_000_000)
                reader = csv.DictReader(handle)
                fields = reader.fieldnames
                if fields is None or len(set(fields)) != len(fields) or not set(REQUIRED).issubset(fields):
                    raise SplitContractError("INVALID_HEADERS")
                if require_original and len(fields) != 90:
                    raise SplitContractError("COLUMN_COUNT_MISMATCH")
                for row in reader:
                    if None in row or any(_missing(row.get(k)) for k in (
                            "GB", "element", "site", "Z", "GB_site", "job_name")):
                        raise SplitContractError("BAD_PRIMITIVE_IDENTITY")
                    gb, el, site = (str(row[k]).strip() for k in ("GB", "element", "site"))
                    key = (gb, el, site)
                    if key in identities:
                        raise SplitContractError("DUPLICATE_PRIMITIVE_KEY")
                    identities.add(key)
                    try:
                        import math
                        number = float(row["Z"])
                        if not math.isfinite(number) or number < 1 or not number.is_integer():
                            raise ValueError("noninteger")
                        z = int(number)
                    except (ValueError, TypeError) as exc:
                        raise SplitContractError("INVALID_ATOMIC_NUMBER") from exc
                    if el in atom_by_element and atom_by_element[el] != z:
                        raise SplitContractError("ATOMIC_NUMBER_CONFLICT")
                    atom_by_element[el] = z
                    mc = _missing(row.get("GB_element_site"))
                    mt = _missing(row.get("E_seg"))
                    combined_missing += int(mc)
                    blank_target += int(mt)
                    records.append({
                        "id": key, "gb_site": str(row["GB_site"]).strip(),
                        "target_blank": mt, "combined_blank": mc,
                    })
    except (OSError, EOFError, UnicodeError, csv.Error) as exc:
        raise SplitContractError("CORRUPT_COMPRESSED_SOURCE") from exc
    if require_original:
        if len(records) != EXPECTED_ROWS or len({r["id"][0] for r in records}) != EXPECTED_GB:
            raise SplitContractError("SOURCE_CARDINALITY_MISMATCH")
        if len(atom_by_element) != EXPECTED_ELEMENTS:
            raise SplitContractError("SOURCE_ELEMENT_COUNT_MISMATCH")
        if combined_missing != EXPECTED_MISSING_COMBINED or blank_target != EXPECTED_MISSING_TARGET:
            raise SplitContractError("SOURCE_MISSINGNESS_CHANGED")
    return records


def canonical_digest(rows: list[dict]) -> str:
    """Stable raw-identity digest: no energies and no source-row ordering."""
    keys = sorted(r["id"] for r in rows)
    if len(keys) != len(set(keys)):
        raise SplitContractError("DUPLICATE_KEYS_IN_SPLIT")
    payload = json.dumps(keys, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _group_metrics(rows: list[dict]) -> dict:
    return {
        "rows": len(rows),
        "target_nonblank_rows": sum(not r["target_blank"] for r in rows),
        "target_blank_rows": sum(r["target_blank"] for r in rows),
        "distinct_gb_sites": len({r["gb_site"] for r in rows}),
        "key_digest": canonical_digest(rows),
    }


def one_fold(rows: list[dict], family: str, gb: str | None = None,
             element: str | None = None) -> dict:
    """Return grouping-only train/test/embargo manifest with hard no-leakage checks."""
    if family not in ("leave_one_gb_out", "leave_one_element_out", "crossed_gb_element"):
        raise SplitContractError("UNKNOWN_SPLIT_FAMILY")
    if family == "leave_one_gb_out":
        if gb is None or element is not None:
            raise SplitContractError("INVALID_FOLD_ID")
        test = [r for r in rows if r["id"][0] == gb]
        train = [r for r in rows if r["id"][0] != gb]
        embargo = []
    elif family == "leave_one_element_out":
        if element is None or gb is not None:
            raise SplitContractError("INVALID_FOLD_ID")
        test = [r for r in rows if r["id"][1] == element]
        train = [r for r in rows if r["id"][1] != element]
        embargo = []
    else:
        if gb is None or element is None:
            raise SplitContractError("INVALID_FOLD_ID")
        test = [r for r in rows if r["id"][0] == gb and r["id"][1] == element]
        train = [r for r in rows if r["id"][0] != gb and r["id"][1] != element]
        embargo = [r for r in rows if r["id"][0] == gb and r["id"][1] != element
                   or r["id"][0] != gb and r["id"][1] == element]
    if not train or not test:
        raise SplitContractError("EMPTY_TRAIN_OR_TEST")
    ta = {r["id"] for r in train}
    te = {r["id"] for r in test}
    em = {r["id"] for r in embargo}
    if ta & te or ta & em or te & em or len(ta | te | em) != len(rows):
        raise SplitContractError("IDENTITY_OVERLAP_OR_COVERAGE_ERROR")
    if gb is not None and any(r["id"][0] == gb for r in train):
        raise SplitContractError("GB_LEAKAGE")
    if element is not None and any(r["id"][1] == element for r in train):
        raise SplitContractError("ELEMENT_LEAKAGE")
    train_sites = {r["gb_site"] for r in train}
    test_sites = {r["gb_site"] for r in test}
    return {
        "family": family,
        "heldout_gb": gb,
        "heldout_element": element,
        "train": _group_metrics(train),
        "test": _group_metrics(test),
        "embargo": _group_metrics(embargo),
        "shared_gb_site_identifiers_train_test": len(train_sites & test_sites),
        "gb_site_disjoint": len(train_sites & test_sites) == 0,
        "shared_gb_labels_train_test": len(
            {r["id"][0] for r in train} & {r["id"][0] for r in test}),
        "shared_element_labels_train_test": len(
            {r["id"][1] for r in train} & {r["id"][1] for r in test}),
        "both_gb_and_element_disjoint": (
            not ({r["id"][0] for r in train} & {r["id"][0] for r in test})
            and not ({r["id"][1] for r in train} & {r["id"][1] for r in test})
        ),
        "test_target_status": (
            "NOT_SCOREABLE_TARGETS_ABSENT"
            if all(r["target_blank"] for r in test)
            else "TARGET_EXISTS_NOT_SCORING_AUTHORIZED"
        ),
        "tested_outcomes": False,
    }


def evaluate_metadata(rows: list[dict]) -> dict:
    if not rows or len({r["id"] for r in rows}) != len(rows):
        raise SplitContractError("BAD_OR_DUPLICATE_INPUTS")
    gb = sorted({r["id"][0] for r in rows})
    elements = sorted({r["id"][1] for r in rows})
    observed_cells = sorted({(r["id"][0], r["id"][1]) for r in rows})
    unobserved_cells = [
        (g, e) for g in gb for e in elements
        if (g, e) not in set(observed_cells)
    ]
    folds = {
        "leave_one_gb_out": [one_fold(rows, "leave_one_gb_out", gb=g) for g in gb],
        "leave_one_element_out": [
            one_fold(rows, "leave_one_element_out", element=e) for e in elements
        ],
        "crossed_gb_element": [
            one_fold(rows, "crossed_gb_element", gb=g, element=e)
            for g, e in observed_cells
        ],
    }
    source_identity = Counter(r["id"][0] for r in rows)
    source_element = Counter(r["id"][1] for r in rows)
    site_reuse = Counter(r["gb_site"] for r in rows)
    nonblank = sum(not r["target_blank"] for r in rows)
    all_sites = len(site_reuse)
    cross = folds["crossed_gb_element"]
    return {
        "schema": "BHS-V12.14-GROUP-DISJOINT-READINESS",
        "source_commit": UPSTREAM_COMMIT,
        "source_file": FILE_NAME,
        "source_record_count": len(rows),
        "source_identity_digest": canonical_digest(rows),
        "source_target_nonblank_rows": nonblank,
        "source_target_blank_rows": len(rows) - nonblank,
        "gb_count": len(gb),
        "element_count": len(elements),
        "gb_site_count": all_sites,
        "gb_site_identifiers_reused_across_rows": sum(n > 1 for n in site_reuse.values()),
        "gb_site_rows_representing_reuse": sum(n for n in site_reuse.values() if n > 1),
        "gb_row_counts": dict(sorted(source_identity.items())),
        "element_row_counts": dict(sorted(source_element.items())),
        "fold_counts": {name: len(v) for name, v in folds.items()},
        "possible_gb_element_cells": len(gb) * len(elements),
        "observed_gb_element_cells": len(observed_cells),
        "unobserved_gb_element_cells": len(unobserved_cells),
        "unobserved_cells": [list(pair) for pair in unobserved_cells],
        "source_missing_original_combined_ids": sum(r["combined_blank"] for r in rows),
        "elements_with_only_blank_target_strings": sorted(
            e for e in elements if not any(
                r["id"][1] == e and not r["target_blank"] for r in rows
            )
        ),
        "crossed_cells_with_only_blank_targets": [
            [f["heldout_gb"], f["heldout_element"]]
            for f in folds["crossed_gb_element"]
            if f["test"]["target_nonblank_rows"] == 0
        ],
        "crossed_test_rows_min": min(f["test"]["rows"] for f in cross),
        "crossed_test_rows_max": max(f["test"]["rows"] for f in cross),
        "crossed_test_target_nonblank_min": min(f["test"]["target_nonblank_rows"] for f in cross),
        "crossed_test_target_nonblank_max": max(f["test"]["target_nonblank_rows"] for f in cross),
        "crossed_test_target_all_blank_folds": sum(
            f["test"]["target_nonblank_rows"] == 0 for f in cross),
        "eligible_numeric_predecision_features": ["Z"],
        "identity_only_features": ["GB", "element", "site", "GB_site", "job_name"],
        "banned_free_prediction_columns": list(BANNED_PREDICTION_COLUMNS),
        "unverified_fidelity_cost": True,
        "external_physical_validation": False,
        "folds": folds,
        "status": "STRUCTURAL_SPLIT_MANIFEST_ONLY_NOT_SCORING_READY",
        **GATES,
    }


def run(source: bytes) -> dict:
    verify_source_bytes(source)
    rows = extract_metadata(source, require_original=True)
    result = evaluate_metadata(rows)
    result["source_sha256"] = hashlib.sha256(source).hexdigest()
    result["upstream_git_blob_verified"] = True
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    report = run(download_upstream())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Structural gate:", report["status"])
    print("Source rows / GBs / elements:", report["source_record_count"],
          report["gb_count"], report["element_count"])
    print("Unique site identities:", report["gb_site_count"])
    print("Fold families:", report["fold_counts"])
    print("Crossed test group min/max:", report["crossed_test_rows_min"],
          report["crossed_test_rows_max"])
    print("Observed / missing GB-element cells:",
          report["observed_gb_element_cells"], report["unobserved_gb_element_cells"])
    print("Element labels with only blank target strings:",
          report["elements_with_only_blank_target_strings"])
    print("No target magnitude, model score or real cost assessed.")


if __name__ == "__main__":
    main()
