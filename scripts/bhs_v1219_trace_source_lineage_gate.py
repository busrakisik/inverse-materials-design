"""V12.19 metadata-only trace-to-trial gate, not experimental evidence.

No downloads, unzipping, parsing of force/displacement samples or labels.
A technically consistent synthetic manifest cannot prove authentic source data.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "research/BHS_V1219_SOURCE_ACCESS_INVENTORY.json"
ORIGINAL_ID = "CROSSED_BARREL_2020_ORIGINAL"
EXPECTED_IDS = frozenset({
    ORIGINAL_ID,
    "CROSSED_BARREL_2021_EXPANDED_FEA",
    "LATTICE_2022_SEPARATE",
    "ADTS_2024_SEPARATE",
})
ROW_KEYS = frozenset({
    "experiment_id", "design_group_id", "n", "theta_deg", "r_mm", "t_mm",
    "curve_file", "acquisition_timestamp",
})
MANIFEST_KEYS = frozenset({"source_dataset_id", "experiment_rows", "declared_archive_sha256"})
MAX_ZIP_BYTES = 2_000_000_000
MAX_MEMBER_UNCOMPRESSED = 30_000_000
MAX_MEMBERS = 50_000

CLOSED = {
    "development_only": True,
    "scored_validation_allowed": False,
    "full_bhs_fair_comparison_ready": False,
    "raw_2020_trace_bytes_verified": False,
    "raw_2020_replicate_join_verified": False,
    "physical_mechanism_hypotheses_validated": False,
    "scientific_likelihood_calibrated": False,
    "independent_holdout_used": False,
    "real_cost_verified": False,
    "claim_of_superiority": False,
    "laboratory_action_allowed": False,
}


class SourceTraceError(ValueError):
    pass


def audit_catalog(raw: bytes | None = None) -> dict:
    raw = CATALOG.read_bytes() if raw is None else raw
    try:
        cat = json.loads(raw)
    except (ValueError, UnicodeError, TypeError) as exc:
        raise SourceTraceError("CATALOG_INVALID_JSON") from exc
    if (type(cat) is not dict
            or cat.get("schema") != "BHS-V12.19-PUBLIC-SOURCE-ACCESS-INVENTORY"
            or cat.get("source_content_verification_complete") is not False
            or cat.get("new_empirical_score_permitted") is not False
            or cat.get("all_source_outcome_values_read") is not False):
        raise SourceTraceError("CATALOG_SCIENTIFIC_STATE_CHANGED")
    entries = cat.get("entries")
    if type(entries) is not list or len(entries) != len(EXPECTED_IDS):
        raise SourceTraceError("SOURCE_CATALOG_CARDINALITY_CHANGED")
    indices = {x.get("id") for x in entries if type(x) is dict}
    if indices != EXPECTED_IDS:
        raise SourceTraceError("SOURCE_DOMAIN_IDENTITY_CHANGED")
    origin = next(x for x in entries if x["id"] == ORIGINAL_ID)
    if (origin.get("citation_doi") != "10.1126/sciadv.aaz1708"
            or origin.get("raw_archive_bytes_downloaded") is not False
            or origin.get("historical_v11_replicate_curve_join_verified") is not False
            or origin.get("file_integrity_digest_independently_verified") is not False
            or origin.get("per_trial_original_ids_verified") is not False
            or origin.get("source_license_of_raw_files_verified") is not False
            or origin.get("score_use_authorized") is not False):
        raise SourceTraceError("ORIGINAL_SOURCE_PROVENANCE_ASSERTION_UNSUPPORTED")
    for entry in entries:
        if entry.get("score_use_authorized") is not False:
            raise SourceTraceError("OTHER_SOURCE_AUTOMATICALLY_APPROVED")
    return {
        "schema": "BHS-V12.19-SOURCE-ONLY-EVIDENCE-STATUS",
        "catalog_sha256": hashlib.sha256(raw).hexdigest(),
        "source_ids": sorted(indices),
        "source_entry_count": len(entries),
        "original_2020_entry_documented": True,
        "original_2020_public_folder_link_found": True,
        "original_2020_external_raw_trace_file_listing_accessible": False,
        "original_2020_per_replicate_curve_matching_proven": False,
        "separate_2021_2022_2024_sources_not_conflated": True,
        "source_measurements_read": False,
        "new_scientific_performance_scored": False,
        "status": "NO_GO_ORIGINAL_2020_TRACE_MAPPING_UNVERIFIED",
        **CLOSED,
    }


def _validate_design(row: dict) -> tuple:
    if type(row) is not dict or set(row) != ROW_KEYS:
        raise SourceTraceError("ROW_FIELDS_MISSING_OR_LEAKED")
    for k in ("experiment_id", "design_group_id", "curve_file"):
        v = row[k]
        if (type(v) is not str or not v.strip() or len(v) > 180):
            raise SourceTraceError("INVALID_EXPERIMENT_ID_OR_CURVE_NAME")
    n = row["n"]
    if type(n) is not int or not 1 <= n <= 100:
        raise SourceTraceError("INVALID_N")
    geom = [n]
    for key in ("theta_deg", "r_mm", "t_mm"):
        v = row[key]
        if type(v) not in (float, int) or not math.isfinite(float(v)):
            raise SourceTraceError("INVALID_GEOMETRY")
        geom.append(float(v))
    if not (0 <= geom[1] <= 180 and 0 < geom[3] <= geom[2] <= 1000):
        raise SourceTraceError("INVALID_GEOMETRY_BOUNDS")
    stamp = row["acquisition_timestamp"]
    if type(stamp) is not str:
        raise SourceTraceError("MISSING_OR_UNVERIFIED_TIMESTAMP")
    try:
        d = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SourceTraceError("INVALID_TIME_FORMAT") from exc
    if d.tzinfo is None or d.utcoffset() is None:
        raise SourceTraceError("TIMEZONE_MISSING")
    fname = row["curve_file"]
    if (PurePosixPath(fname).name != fname or fname.startswith(".")
            or ".." in fname or not re.fullmatch(r"[A-Za-z0-9_.-]+\.csv", fname)):
        raise SourceTraceError("UNSAFE_CURVE_FILE_NAME")
    return tuple(geom)


def _archive_names_only(raw: bytes) -> tuple[set[str], dict]:
    """Inspect only the ZIP central directory and archive hash; never file bodies."""
    if type(raw) is not bytes or not (1 <= len(raw) <= MAX_ZIP_BYTES):
        raise SourceTraceError("INVALID_ARCHIVE_BYTES")
    try:
        with zipfile.ZipFile(io.BytesIO(raw), mode="r") as z:
            members = z.infolist()
            if not members or len(members) > MAX_MEMBERS:
                raise SourceTraceError("UNSUPPORTED_ZIP_MEMBER_COUNT")
            names = []
            total = 0
            for m in members:
                name = m.filename
                if m.is_dir() or m.flag_bits & 0x1:
                    raise SourceTraceError("FOLDERS_OR_ENCRYPTION_NOT_ALLOWED")
                if (PurePosixPath(name).name != name or name.startswith(".")
                        or ".." in name or not re.fullmatch(r"[A-Za-z0-9_.-]+\.csv", name)):
                    raise SourceTraceError("INVALID_ARCHIVE_MEMBER_PATH")
                if stat.S_IFMT(m.external_attr >> 16) == stat.S_IFLNK:
                    raise SourceTraceError("ZIP_SYMLINK_NOT_ALLOWED")
                if m.file_size > MAX_MEMBER_UNCOMPRESSED:
                    raise SourceTraceError("ZIP_MEMBER_TOO_LARGE")
                total += m.file_size
                if total > MAX_ZIP_BYTES:
                    raise SourceTraceError("ZIP_EXPANDED_CONTENT_LIMIT")
                names.append(name)
            if len(names) != len(set(names)):
                raise SourceTraceError("DUPLICATED_ZIP_MEMBER_NAMES")
    except (zipfile.BadZipFile, OSError, EOFError) as exc:
        raise SourceTraceError("INVALID_ZIP_DIRECTORY") from exc
    return set(names), {
        "archive_sha256_computed_from_local_bytes": hashlib.sha256(raw).hexdigest(),
        "uncompressed_bytes_declared_by_zip": total,
        "member_count": len(names),
        "numeric_force_displacement_values_parsed": False,
    }


def audit_trial_archive(manifest: dict, archive: bytes, *,
                        original_grid_scope: bool = True) -> dict:
    """Technical shape check. A self-supplied digest is NEVER external authentication."""
    if type(manifest) is not dict or set(manifest) != MANIFEST_KEYS:
        raise SourceTraceError("MANIFEST_SCHEMA_INVALID")
    if manifest["source_dataset_id"] != ORIGINAL_ID:
        raise SourceTraceError("CROSS_STUDY_DATASET_JOIN_BLOCKED")
    declared = manifest["declared_archive_sha256"]
    if (type(declared) is not str or
            not re.fullmatch("[0-9a-f]{64}", declared)):
        raise SourceTraceError("NO_VALID_DECLARED_ARCHIVE_DIGEST")
    rows = manifest["experiment_rows"]
    if type(rows) is not list or not rows:
        raise SourceTraceError("MISSING_EXPERIMENT_ROWS")
    if original_grid_scope and len(rows) != 1800:
        raise SourceTraceError("ORIGINAL_V11_GRID_REPLICATE_COUNT_MISMATCH")

    ids, files, groups = set(), set(), defaultdict(list)
    for row in rows:
        geom = _validate_design(row)
        rid, f, gid = row["experiment_id"], row["curve_file"], row["design_group_id"]
        if rid in ids or f in files:
            raise SourceTraceError("DUPLICATE_TRIAL_ID_OR_CURVE_MAPPING")
        ids.add(rid)
        files.add(f)
        groups[gid].append(geom)

    if original_grid_scope and len(groups) != 600:
        raise SourceTraceError("ORIGINAL_V11_GROUP_COUNT_MISMATCH")
    group_geometry = set()
    for designs in groups.values():
        if len(designs) != 3:
            raise SourceTraceError("REPLICATES_NOT_TRIPLETS")
        if len(set(designs)) != 1:
            raise SourceTraceError("GROUP_HAS_INCONSISTENT_PUBLIC_DESIGN")
        group_geometry.add(designs[0])
    if len(group_geometry) != len(groups):
        raise SourceTraceError("DUPLICATE_DESIGN_ACROSS_GROUPS")

    members, zinfo = _archive_names_only(archive)
    if members != files:
        raise SourceTraceError("ARCHIVE_MEMBER_AND_EXPERIMENT_MAPPING_DIFFER")
    if zinfo["archive_sha256_computed_from_local_bytes"] != declared:
        raise SourceTraceError("DECLARED_ARCHIVE_DIGEST_MISMATCH")

    return {
        "schema": "BHS-V12.19-ZIP-DIRECTORY-TECHNICAL-ONLY",
        "trial_count": len(ids),
        "distinct_design_group_count": len(groups),
        "curve_file_count": len(files),
        **zinfo,
        "matches_manifest_declared_digest": True,
        "archive_digest_independently_authenticated": False,
        "original_creator_experiment_id_mapping_authenticated": False,
        "physical_curve_content_read": False,
        "per_experiment_label_visibility_at_policy_time_verified": False,
        "real_2020_physical_curve_dataset_authenticated": False,
        "status": "STRUCTURAL_TEST_ONLY_AUTHOR_SOURCE_AUTHENTICATION_REQUIRED",
        **CLOSED,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    r = audit_catalog()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print("Public source entries:", r["source_entry_count"])
    print("Original 2020 per-trace provenance:", r["status"])
    print("No physical curve values inspected and no model score authorized.")


if __name__ == "__main__":
    main()
