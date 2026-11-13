"""V12.15: immutable source feature-presence audit; no physical values examined.

Column presence, blank strings, and known grouping identifiers only.
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
    FILE_NAME, UPSTREAM_COMMIT, _missing, download_upstream, verify_source_bytes,
)
from scripts.bhs_v1214_group_split_readiness import (
    SplitContractError, canonical_digest, extract_metadata,
)

SELECTION_TIME_KNOWN = frozenset({"GB", "element", "Z"})
IDENTITY_ONLY = frozenset({
    "site", "GB_site", "GB_element_site", "job_name",
})
POTENTIAL_PREGEOMETRY = frozenset({
    "structure_unrel", "dist_GB_unrel", "site_z_unrel",
})
BANNED_ENERGY_AND_OUTPUT = frozenset({
    "E_seg", "E_seg_unrel", "structure", "site_z",
    "dist_GB", "magmoms", "magmom_solute", "magmoms_unrel",
    "magmom_solute_unrel", "convergence", "convergence_pureGB",
    "pure_min_wsep_rigid", "pure_cleavage_energies",
    "magmoms_pureGB",
})
CANDIDATES = (
    "structure_unrel", "dist_GB_unrel", "site_z_unrel",
)
GATES = {
    "development_only": True,
    "scored_validation_allowed": False,
    "precalculation_geometry_certified": False,
    "real_cost_verified": False,
    "independent_holdout_used": False,
    "physical_validation_by_bhs": False,
    "claim_of_superiority": False,
    "statistical_guarantee_supported": False,
    "real_savings_measured": False,
    "laboratory_action_allowed": False,
}


def classify(field: str) -> str:
    if field in SELECTION_TIME_KNOWN:
        return "SELECTION_KNOWN_IDENTITY"
    if field in IDENTITY_ONLY:
        return "IDENTIFIER_ONLY_NO_PREDICTION"
    if field in POTENTIAL_PREGEOMETRY or (
            field.startswith("VorNN_") and field.endswith("_unrel")):
        return "CANDIDATE_UNREL_GEOMETRY_NOT_CERTIFIED"
    if field in BANNED_ENERGY_AND_OUTPUT or field.startswith(("E_", "Wsep", "R_Wsep",
                                                                "DDEC6", "R_DDEC6", "pure_")):
        return "COMPUTED_OR_POSTRUN_DENY"
    if field.startswith("VorNN_") or field.endswith("_unrel"):
        return "COMPUTED_OR_UNCERTAIN_DENY"
    return "UNKNOWN_PROVENANCE_DENY"


def source_feature_availability(raw: bytes, require_original: bool = True) -> dict:
    """Never interpret cell contents beyond identity keys and blankness."""
    integrity = verify_source_bytes(raw) if require_original else {}
    records = extract_metadata(raw, require_original=require_original)
    cands = {}
    per_gb = {}
    cross_missingness = {}
    label_blanks = 0
    rows = 0
    headers = None
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as source:
            with io.TextIOWrapper(source, encoding="utf-8", newline="") as decoded:
                csv.field_size_limit(20_000_000)
                csv_rows = csv.DictReader(decoded)
                headers = csv_rows.fieldnames
                if (not headers or len(set(headers)) != len(headers)
                        or not set(SELECTION_TIME_KNOWN | IDENTITY_ONLY | {"E_seg"}).issubset(headers)):
                    raise SplitContractError("INVALID_HEADERS")
                if require_original and len(headers) != 90:
                    raise SplitContractError("COLUMN_COUNT_MISMATCH")
                cands = {col: Counter() for col in headers
                         if classify(col) == "CANDIDATE_UNREL_GEOMETRY_NOT_CERTIFIED"}
                per_gb = {col: {} for col in cands}
                cross_missingness = {col: {
                    "target_blank_and_feature_present": 0,
                    "target_blank_and_feature_blank": 0,
                    "target_present_and_feature_present": 0,
                    "target_present_and_feature_blank": 0,
                } for col in cands}
                for row in csv_rows:
                    if None in row or len(row) != len(headers):
                        raise SplitContractError("MALFORMED_CSV_RECORD")
                    rows += 1
                    gb = str(row["GB"]).strip()
                    mt = _missing(row["E_seg"])
                    label_blanks += int(mt)
                    for col in cands:
                        found = not _missing(row[col])
                        cands[col]["populated" if found else "blank"] += 1
                        gb_count = per_gb[col].setdefault(gb, {"populated": 0, "blank": 0})
                        gb_count["populated" if found else "blank"] += 1
                        key = "target_" + ("blank" if mt else "present") + "_and_feature_" + (
                            "present" if found else "blank")
                        cross_missingness[col][key] += 1
    except (OSError, EOFError, UnicodeError, csv.Error) as exc:
        raise SplitContractError("SOURCE_FORMAT_ERROR") from exc

    if rows != len(records) or sum(r["target_blank"] for r in records) != label_blanks:
        raise SplitContractError("RECORD_OR_MISSINGNESS_COUNT_CHANGED")
    fields = sorted(headers)
    categories = {col: classify(col) for col in fields}
    unknown = [col for col in fields
               if categories[col] in ("UNKNOWN_PROVENANCE_DENY", "COMPUTED_OR_UNCERTAIN_DENY")]
    vornn = sorted(x for x in cands if x.startswith("VorNN_"))
    return {
        "schema": "BHS-V12.15-PRECOMPUTATION-AVAILABILITY",
        "upstream_commit": UPSTREAM_COMMIT,
        "file_name": FILE_NAME,
        **integrity,
        "row_count": rows,
        "gb_count": len({r["id"][0] for r in records}),
        "element_count": len({r["id"][1] for r in records}),
        "key_sha256": canonical_digest(records),
        "target_blank_strings": label_blanks,
        "original_combined_identifier_blanks": sum(r["combined_blank"] for r in records),
        "header_count": len(fields),
        "sorted_header_names": fields,
        "header_sha256": hashlib.sha256(json.dumps(
            fields, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest(),
        "column_provenance_states": categories,
        "unreviewed_or_uncertain_columns": unknown,
        "geometry_candidate_column_count": len(cands),
        "candidate_voronoi_column_count": len(vornn),
        "candidate_geometry_fields": sorted(cands),
        "claimed_core_candidate_header_presence": {
            col: col in fields for col in CANDIDATES
        },
        "candidate_column_coverage": {col: {
            "populated_rows": cands[col]["populated"],
            "blank_rows": cands[col]["blank"],
            "by_gb": dict(sorted(per_gb[col].items())),
            "paired_target_string_missingness": cross_missingness[col],
            "chronology_verified": False,
            "predecision_feature_approved": False,
        } for col in sorted(cands)},
        "sample_poscar_available_in_upstream_repo": True,
        "sample_poscar_git_blob": "c1b92f972db85ebbce5bf9cc8e58a4d356ee27be",
        "sample_incar_git_blob": "d0a1a818098b901317b1803eb20a4c1db95f54fd",
        "full_4289_row_starting_structure_lineage_verified": False,
        "raw_values_or_scientific_outcomes_inspected": False,
        "approved_numerical_geometry_predictor_columns": [],
        "status": "FEATURE_PRESENCE_ONLY_PROVENANCE_UNVERIFIED",
        **GATES,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    report = source_feature_availability(download_upstream())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("V12.15:", report["status"])
    print("Columns / candidate geometry columns:", report["header_count"],
          report["geometry_candidate_column_count"])
    print("Candidate starting structure/header presence:",
          report["claimed_core_candidate_header_presence"])
    print("Candidate Voronoi columns:", report["candidate_voronoi_column_count"])
    print("No geometry or energy values, model outputs, physical costs inspected.")


if __name__ == "__main__":
    main()
