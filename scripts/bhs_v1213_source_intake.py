"""V12.13: immutable upstream DFT file and outcome-free metadata intake."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen

SCHEMA = "BHS-V12.13-SOURCE-ONLY"
REPO_ID = 789358474
UPSTREAM_COMMIT = "c079fcd00cf1e085fe917d460dbc36a064155296"
FILE_NAME = "2025_03_02_ptable_Fe_GB_df.csv.gz"
FILE_SIZE = 31745622
GIT_BLOB = "fcd4e2ef24da093438030e3095469a679ed54d04"
EXPECTED_ROWS = 4289
EXPECTED_COLUMNS = 90
REQUIRED = frozenset(("GB", "element", "Z", "site", "GB_site",
                      "GB_element_site", "job_name", "E_seg"))
NO_GO = {
    "development_only": True,
    "scored_validation_allowed": False,
    "independent_holdout_used": False,
    "physical_validation_by_bhs": False,
    "claim_of_superiority": False,
    "statistical_guarantee_supported": False,
    "real_savings_measured": False,
    "physical_recommendation_allowed": False,
    "laboratory_action_allowed": False,
}
MAX_FILE_BYTES = 34_000_000


class SourceContractError(ValueError):
    """A mismatch is a stop condition, not a cleaning instruction."""


def _sha1_git_blob(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


def verify_source_bytes(raw: bytes) -> dict:
    if not isinstance(raw, bytes) or len(raw) > MAX_FILE_BYTES:
        raise SourceContractError("SOURCE_BYTES_INVALID")
    if len(raw) != FILE_SIZE:
        raise SourceContractError("SOURCE_SIZE_MISMATCH")
    blob = _sha1_git_blob(raw)
    if blob != GIT_BLOB:
        raise SourceContractError("SOURCE_GIT_BLOB_MISMATCH")
    return {"source_bytes": len(raw), "source_git_blob": blob,
            "source_sha256": hashlib.sha256(raw).hexdigest()}


def _missing(v) -> bool:
    return v is None or not str(v).strip() or str(v).strip().lower() in ("nan", "none", "null")


def scan_source(raw: bytes, expected_rows: int | None = None,
                expected_columns: int | None = None) -> dict:
    """Inspect only identifiers and whether target strings are missing.

    Never convert target strings into numeric values or return label records.
    Small fixed test fixtures can set expected_rows/columns; production
    always uses original README counts.
    """
    counts = Counter()
    elements = set()
    sites = set()
    pair_groups = set()
    unique_labels = set()
    atom_num = {}
    missing_target = 0
    duplicate_ids = 0
    problems = set()
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as decoded:
                csv.field_size_limit(20_000_000)
                reader = csv.DictReader(decoded)
                headers = reader.fieldnames
                if not headers or len(headers) != len(set(headers)):
                    raise SourceContractError("MISSING_OR_DUPLICATED_HEADERS")
                if not REQUIRED.issubset(headers):
                    raise SourceContractError("REQUIRED_SOURCE_COLUMNS_MISSING")
                if expected_columns is not None and len(headers) != expected_columns:
                    problems.add("COLUMN_COUNT_MISMATCH")
                for row in reader:
                    if None in row or len(row) != len(headers):
                        problems.add("MALFORMED_CSV_RECORD")
                        continue
                    gb = row["GB"]
                    el = row["element"]
                    identifier = row["GB_element_site"]
                    site = row["GB_site"]
                    if any(_missing(row[k]) for k in REQUIRED - {"E_seg"}):
                        problems.add("MISSING_REQUIRED_IDENTITY")
                        continue
                    try:
                        z = float(row["Z"])
                        if not math.isfinite(z) or z <= 0 or not z.is_integer():
                            raise ValueError("bad")
                        zi = int(z)
                    except ValueError:
                        problems.add("ATOMIC_NUMBER_INVALID")
                        continue
                    if el in atom_num and atom_num[el] != zi:
                        problems.add("ATOMIC_NUMBER_CONFLICT")
                    atom_num[el] = zi
                    if identifier in unique_labels:
                        duplicate_ids += 1
                    unique_labels.add(identifier)
                    counts[gb] += 1
                    elements.add(el)
                    sites.add(site)
                    pair_groups.add((gb, el))
                    if _missing(row["E_seg"]):
                        missing_target += 1
    except (UnicodeError, OSError, EOFError, csv.Error) as exc:
        raise SourceContractError("SOURCE_DECOMPRESSION_OR_CSV_ERROR") from exc
    n = sum(counts.values())
    if expected_rows is not None and n != expected_rows:
        problems.add("ROW_COUNT_MISMATCH")
    if duplicate_ids:
        problems.add("DUPLICATE_RECORD_IDENTIFIER")
    if n == 0:
        problems.add("NO_RECORDS")
    return {
        "row_count": n,
        "column_count": len(headers),
        "boundary_count": len(counts),
        "boundary_row_counts": dict(sorted(counts.items())),
        "element_count": len(elements),
        "boundary_element_groups": len(pair_groups),
        "unique_boundary_site_ids": len(sites),
        "duplicate_record_ids": duplicate_ids,
        "missing_target_strings": missing_target,
        "structural_problems": sorted(problems),
    }


def audit(raw: bytes) -> dict:
    integrity = verify_source_bytes(raw)
    groups = scan_source(raw, EXPECTED_ROWS, EXPECTED_COLUMNS)
    checks = groups["structural_problems"]
    if groups["boundary_count"] != 6:
        checks.append("BOUNDARY_COUNT_MISMATCH")
    return {
        "schema": SCHEMA,
        "source_type": "retrospective_external_density_functional_calculations",
        "upstream_repository_id": REPO_ID,
        "upstream_commit": UPSTREAM_COMMIT,
        "source_filename": FILE_NAME,
        **integrity,
        **groups,
        "intake_status": "INTAKE_BLOCKED" if checks else "SOURCE_ONLY_NOT_EVALUATION_READY",
        "target_magnitudes_inspected": False,
        "trained_model": False,
        "run_cost_verified": False,
        "outcome_free_feature_whitelist": [],
        **NO_GO,
    }


def download_upstream() -> bytes:
    """Resolve the upstream identity through its numeric GitHub repository ID."""
    headers = {"User-Agent": "BHS-source-integrity-audit", "Accept": "application/vnd.github+json"}
    with urlopen(Request("https://api.github.com/repositories/" + str(REPO_ID), headers=headers), timeout=40) as resp:
        repo = json.load(resp)
    if repo.get("id") != REPO_ID or repo.get("private") is not False:
        raise SourceContractError("UPSTREAM_REPOSITORY_IDENTITY_UNVERIFIED")
    full_name = repo["full_name"]
    url = ("https://raw.githubusercontent.com/" + full_name + "/" +
           UPSTREAM_COMMIT + "/" + FILE_NAME)
    with urlopen(Request(url, headers={"User-Agent": "BHS-source-integrity-audit"}), timeout=240) as resp:
        data = resp.read(MAX_FILE_BYTES + 1)
    verify_source_bytes(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    raw = args.source.read_bytes() if args.source else download_upstream()
    report = audit(raw)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("Source intake:", report["intake_status"])
    print("SHA-256:", report["source_sha256"])
    if report["structural_problems"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
