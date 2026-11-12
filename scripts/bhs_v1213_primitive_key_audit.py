"""V12.13: verify candidate composite keys without touching scientific outcomes."""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

from scripts.bhs_v1213_source_intake import (
    _missing, download_upstream, verify_source_bytes, FILE_NAME,
    UPSTREAM_COMMIT, NO_GO,
)


def assess_keys(raw: bytes) -> dict:
    identity = verify_source_bytes(raw)
    tuples = Counter()
    jobs = Counter()
    by_gb = Counter()
    missing_primitive = Counter()
    original_blank = 0
    original_nonblank = 0
    missing_target = 0
    overlap_missing_target = 0
    declared_for_key = defaultdict(set)
    total = 0
    with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as gz:
        with io.TextIOWrapper(gz, encoding="utf-8", newline="") as stream:
            csv.field_size_limit(20_000_000)
            reader = csv.DictReader(stream)
            required = ("GB", "element", "site", "job_name",
                        "GB_site", "GB_element_site", "E_seg")
            if not set(required).issubset(reader.fieldnames or ()):
                raise ValueError("SOURCE_SCHEMA_CHANGED")
            for row in reader:
                total += 1
                primitive = tuple(row.get(k) for k in ("GB", "element", "site"))
                for name, val in zip(("GB", "element", "site"), primitive):
                    if _missing(val):
                        missing_primitive[name] += 1
                if not any(_missing(v) for v in primitive):
                    tuples[primitive] += 1
                job = row.get("job_name")
                if _missing(job):
                    missing_primitive["job_name"] += 1
                else:
                    jobs[job] += 1
                if _missing(row.get("GB_site")):
                    missing_primitive["GB_site"] += 1
                gb = row.get("GB") or "<missing>"
                by_gb[gb] += 1
                missing_combined = _missing(row.get("GB_element_site"))
                blank_target = _missing(row.get("E_seg"))
                original_blank += int(missing_combined)
                original_nonblank += int(not missing_combined)
                missing_target += int(blank_target)
                overlap_missing_target += int(missing_combined and blank_target)
                if not missing_combined and not any(_missing(x) for x in primitive):
                    declared_for_key[primitive].add(row["GB_element_site"])
    reused_tuples = {key: n for key, n in tuples.items() if n > 1}
    reused_jobs = {job: n for job, n in jobs.items() if n > 1}
    aliased_key_count = sum(len(xs) > 1 for xs in declared_for_key.values())
    primitive_usable = (sum(missing_primitive.values()) == 0
                        and len(reused_tuples) == 0)
    return {
        "schema": "BHS-V12.13-PRIMITIVE-IDENTITY-DECISION",
        "upstream_commit": UPSTREAM_COMMIT,
        "source_filename": FILE_NAME,
        **identity,
        "total_source_records": total,
        "primitive_key_cardinality": len(tuples),
        "duplicated_primitive_key_types": len(reused_tuples),
        "duplicate_primitive_key_excess_rows": sum(n - 1 for n in reused_tuples.values()),
        "duplicated_job_name_types": len(reused_jobs),
        "duplicate_job_name_excess_rows": sum(n - 1 for n in reused_jobs.values()),
        "missing_primitive_fields": dict(sorted(missing_primitive.items())),
        "missing_original_combined_identifiers": original_blank,
        "present_original_combined_identifiers": original_nonblank,
        "primitive_keys_with_multiple_declared_combined_names": aliased_key_count,
        "missing_target_strings_total": missing_target,
        "missing_target_strings_with_missing_combined_id": overlap_missing_target,
        "boundary_rows": dict(sorted(by_gb.items())),
        "primitive_key_identifiable": primitive_usable,
        "raw_combined_identifiers_repaired": False,
        "scored_benchmark_eligible": False,
        "audit_status": "IDENTIFIER_RECOVERY_DIAGNOSTIC_ONLY",
        **NO_GO,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    obj = assess_keys(download_upstream())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Untouched source identity:", obj["audit_status"])
    print("Primitive key cardinality:", obj["primitive_key_cardinality"])
    print("Duplicated primitive keys:", obj["duplicated_primitive_key_types"])
    print("Missing source combined ids:", obj["missing_original_combined_identifiers"])
    print("Missing targets and overlap:", obj["missing_target_strings_total"],
          obj["missing_target_strings_with_missing_combined_id"])
    print("No scored evaluation performed.")


if __name__ == "__main__":
    main()
