"""V12.13: explain first source-intake rejection using only identifier fields."""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
from collections import Counter
from pathlib import Path

from scripts.bhs_v1213_source_intake import (
    REQUIRED, _missing, download_upstream, verify_source_bytes,
    FILE_NAME, UPSTREAM_COMMIT, NO_GO,
)


def diagnose(raw: bytes) -> dict:
    source = verify_source_bytes(raw)
    count = 0
    count_missing = 0
    field_missing = Counter()
    combination_missing = Counter()
    affected_boundaries = Counter()
    blank_targets = 0
    complete_id_rows = 0
    keys = sorted(REQUIRED - {"E_seg"})
    with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as gz:
        with io.TextIOWrapper(gz, encoding="utf-8", newline="") as handle:
            csv.field_size_limit(20_000_000)
            reader = csv.DictReader(handle)
            if not REQUIRED.issubset(reader.fieldnames or []):
                raise ValueError("REQUIRED_FIELDS_NOT_PRESENT")
            for row in reader:
                count += 1
                absent = tuple(k for k in keys if _missing(row.get(k)))
                if absent:
                    count_missing += 1
                    field_missing.update(absent)
                    combination_missing["+".join(absent)] += 1
                    affected_boundaries[str(row.get("GB") or "<missing>")] += 1
                else:
                    complete_id_rows += 1
                if _missing(row.get("E_seg")):
                    blank_targets += 1
    return {
        "schema": "BHS-V12.13-IDENTITY-DIAGNOSTIC",
        "upstream_commit": UPSTREAM_COMMIT,
        "source_filename": FILE_NAME,
        **source,
        "total_records": count,
        "complete_identifier_records": complete_id_rows,
        "missing_identifier_records": count_missing,
        "missing_identifier_columns": dict(sorted(field_missing.items())),
        "missing_identifier_patterns": dict(sorted(combination_missing.items())),
        "affected_boundary_counts": dict(sorted(affected_boundaries.items())),
        "missing_target_strings": blank_targets,
        "target_magnitudes_inspected": False,
        "outcome_score_calculated": False,
        "next_stage_eligible": False,
        "audit_status": "DIAGNOSTIC_ONLY_NO_GO",
        **NO_GO,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    report = diagnose(download_upstream())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("Source identity diagnostic:", report["audit_status"])
    print("Total / complete / incomplete identities:",
          report["total_records"], report["complete_identifier_records"],
          report["missing_identifier_records"])
    print("Field count:", report["missing_identifier_columns"])
    print("Patterns:", report["missing_identifier_patterns"])
