"""Explain first V12.14 source-group mismatch without reading outcome magnitudes."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import io
import json
from pathlib import Path

from scripts.bhs_v1213_source_intake import (
    _missing, download_upstream, verify_source_bytes, NO_GO, UPSTREAM_COMMIT
)


def audit_element_coverage(raw: bytes, verify: bool = True) -> dict:
    identity = verify_source_bytes(raw) if verify else {}
    all_elements = Counter()
    with_combined = Counter()
    without_combined = Counter()
    by_gb = defaultdict(set)
    n_rows = 0
    missing_label = 0
    missing_combined_count = 0
    with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as zipped:
        with io.TextIOWrapper(zipped, encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not {"GB", "element", "Z", "site", "GB_element_site", "E_seg"}.issubset(reader.fieldnames or []):
                raise ValueError("SOURCE_FIELDS_MISSING")
            for row in reader:
                n_rows += 1
                el = str(row["element"]).strip()
                gb = str(row["GB"]).strip()
                if _missing(el) or _missing(gb):
                    raise ValueError("SOURCE_PRIMITIVE_GROUP_BLANK")
                all_elements[el] += 1
                by_gb[el].add(gb)
                mc = _missing(row.get("GB_element_site"))
                mt = _missing(row.get("E_seg"))
                if mc:
                    without_combined[el] += 1
                    missing_combined_count += 1
                else:
                    with_combined[el] += 1
                missing_label += int(mt)
    return {
        "schema": "BHS-V12.14-ELEMENT-CARDINALITY-DIAGNOSTIC",
        "source_commit": UPSTREAM_COMMIT,
        **identity,
        "total_records": n_rows,
        "full_element_count": len(all_elements),
        "complete_combined_id_element_count": len(with_combined),
        "incomplete_combined_id_element_count": len(without_combined),
        "missing_combined_id_records": missing_combined_count,
        "missing_target_strings": missing_label,
        "elements_full_source": sorted(all_elements),
        "elements_complete_id_subset": sorted(with_combined),
        "elements_incomplete_id_subset": sorted(without_combined),
        "elements_only_in_incomplete_id_subset": sorted(
            set(without_combined) - set(with_combined)),
        "rows_for_elements_only_in_incomplete_subset": {
            e: all_elements[e] for e in sorted(set(without_combined) - set(with_combined))
        },
        "boundaries_for_elements_only_in_incomplete_subset": {
            e: sorted(by_gb[e]) for e in sorted(set(without_combined) - set(with_combined))
        },
        "scientific_outcomes_inspected": False,
        "selected_holdout": False,
        "status": "CARDINALITY_DIAGNOSTIC_NO_GO",
        **NO_GO,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    result = audit_element_coverage(download_upstream())
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("Source elements / complete-ID subset:", result["full_element_count"],
          result["complete_combined_id_element_count"])
    print("Additional element labels:", result["elements_only_in_incomplete_id_subset"])
    print("Extra rows:", result["rows_for_elements_only_in_incomplete_subset"])
    print("No target values or model outcomes evaluated.")


if __name__ == "__main__":
    main()
