"""One author-archived original starting structure versus one source row.

Only one initial-coordinate pair is inspected. No label, post-relaxation
geometry, magnetic moment, output energy, cost claim or performance score.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
from scipy.optimize import linear_sum_assignment

from scripts.bhs_v1213_source_intake import (
    REPO_ID, UPSTREAM_COMMIT, _missing, _sha1_git_blob,
    download_upstream, verify_source_bytes,
)

INPUT_PATH = "Data/S11-RA110-S3-32-He-19/POSCAR.orig"
INPUT_BLOB = "c1b92f972db85ebbce5bf9cc8e58a4d356ee27be"
PARAMS_PATH = "Data/S11-RA110-S3-32-He-19/INCAR.orig"
PARAMS_BLOB = "d0a1a818098b901317b1803eb20a4c1db95f54fd"
SAMPLE_GB = "S11_RA110_S3_32"
SAMPLE_ELEMENT = "He"
SAMPLE_SITE = "19"
FIXED_TOLERANCE_ANGSTROM = 0.001
MAX_INPUT_FILE_BYTES = 100_000
MAX_SERIALIZED_STRUCTURE_CHARS = 500_000
GATES = {
    "development_only": True,
    "scored_validation_allowed": False,
    "precalculation_geometry_certified": False,
    "policy_time_access_certified": False,
    "full_4289_row_input_lineage_certified": False,
    "independent_holdout_used": False,
    "real_cost_verified": False,
    "physical_validation_by_bhs": False,
    "claim_of_superiority": False,
    "statistical_guarantee_supported": False,
    "real_savings_measured": False,
    "laboratory_action_allowed": False,
}


class GeometryContractError(ValueError):
    pass


def _mat(x):
    a = np.asarray(x, dtype=float)
    if a.shape != (3, 3) or not np.isfinite(a).all():
        raise GeometryContractError("INVALID_LATTICE")
    if abs(float(np.linalg.det(a))) < 1.0e-7:
        raise GeometryContractError("SINGULAR_LATTICE")
    return a


def parse_poscar(raw: bytes) -> dict:
    if not isinstance(raw, bytes) or not (20 < len(raw) <= MAX_INPUT_FILE_BYTES):
        raise GeometryContractError("INVALID_POSCAR_BYTES")
    try:
        lines = [l.strip() for l in raw.decode("utf-8").splitlines() if l.strip()]
        factor = float(lines[1])
        if not math.isfinite(factor) or factor <= 0:
            raise GeometryContractError("INVALID_SCALE")
        lattice = _mat([[float(t) for t in lines[i].split()[:3]]
                        for i in range(2, 5)]) * factor
        names = lines[5].split()
        counts = [int(v) for v in lines[6].split()]
        if not names or len(names) != len(counts) or any(v < 1 for v in counts):
            raise GeometryContractError("INVALID_POSCAR_SPECIES")
        if not all(name.isalpha() and name[0].isupper() for name in names):
            raise GeometryContractError("INVALID_POSCAR_ELEMENT")
        p = 7
        if lines[p].lower().startswith("s"):
            p += 1
        mode = lines[p].lower()
        if not mode.startswith(("direct", "cart", "k", "d", "c")):
            raise GeometryContractError("UNKNOWN_POSCAR_COORDINATE_MODE")
        direct = mode[0] == "d"
        p += 1
        n = sum(counts)
        if len(lines) < p + n:
            raise GeometryContractError("INSUFFICIENT_POSCAR_ATOMS")
        xyz = np.array([[float(t) for t in lines[p+i].split()[:3]]
                        for i in range(n)], dtype=float)
        if xyz.shape != (n, 3) or not np.isfinite(xyz).all():
            raise GeometryContractError("INVALID_POSCAR_COORDINATES")
        fractional = xyz if direct else (xyz * factor) @ np.linalg.inv(lattice)
        species = [name for name, count in zip(names, counts) for _ in range(count)]
    except (TypeError, IndexError, UnicodeError, ValueError, np.linalg.LinAlgError) as exc:
        if isinstance(exc, GeometryContractError):
            raise
        raise GeometryContractError("INVALID_POSCAR_FORMAT") from exc
    return {"lattice": lattice, "frac": fractional, "species": species}


def parse_structure_repr(text: str) -> dict:
    if not isinstance(text, str) or len(text) > MAX_SERIALIZED_STRUCTURE_CHARS or _missing(text):
        raise GeometryContractError("MISSING_OR_OVERSIZED_START_STRUCTURE")
    try:
        try:
            d = json.loads(text)
        except json.JSONDecodeError:
            d = ast.literal_eval(text)
        if not isinstance(d, dict) or not isinstance(d.get("lattice"), dict):
            raise GeometryContractError("UNRECOGNIZED_START_STRUCTURE_FORMAT")
        lattice = _mat(d["lattice"]["matrix"])
        sites = d["sites"]
        if not isinstance(sites, list) or not sites or len(sites) > 10000:
            raise GeometryContractError("INVALID_STRUCTURE_SITES")
        species = []
        frac = []
        for site in sites:
            if not isinstance(site, dict):
                raise GeometryContractError("INVALID_STRUCTURE_SITE")
            entry = site.get("species")
            if not isinstance(entry, list) or len(entry) != 1:
                raise GeometryContractError("NONUNIT_STRUCTURE_OCCUPANCY")
            atom = entry[0]
            if not isinstance(atom, dict) or abs(float(atom.get("occu", 0))-1.0) > 1e-8:
                raise GeometryContractError("NONUNIT_STRUCTURE_OCCUPANCY")
            element = atom.get("element")
            if not isinstance(element, str) or not element.isalpha() or not element[0].isupper():
                raise GeometryContractError("UNKNOWN_ATOM_ELEMENT")
            xyz = site.get("abc")
            if not isinstance(xyz, list) or len(xyz) != 3:
                raise GeometryContractError("MISSING_FRACTIONAL_COORDINATES")
            numbers = [float(v) for v in xyz]
            if not all(math.isfinite(v) for v in numbers):
                raise GeometryContractError("NONFINITE_COORDINATES")
            frac.append(numbers)
            species.append(element)
    except (ValueError, SyntaxError, TypeError, KeyError, IndexError,
            RecursionError, OverflowError) as exc:
        if isinstance(exc, GeometryContractError):
            raise
        raise GeometryContractError("INVALID_START_STRUCTURE_SERIALIZATION") from exc
    return {"lattice": lattice, "frac": np.asarray(frac, dtype=float),
            "species": species}


def match_input_geometry(original: dict, published: dict) -> dict:
    """Assignment is species-constrained; 27 lattice offsets per pair."""
    x, y = original, published
    if len(x["species"]) != len(y["species"]):
        raise GeometryContractError("ATOM_COUNT_MISMATCH")
    if Counter(x["species"]) != Counter(y["species"]):
        raise GeometryContractError("SPECIES_MISMATCH")
    a = _mat(x["lattice"])
    b = _mat(y["lattice"])
    lattice_error = float(np.max(np.abs(a - b)))
    shifts = np.asarray([(i, j, k) for i in (-1, 0, 1)
                         for j in (-1, 0, 1) for k in (-1, 0, 1)], dtype=float)
    distances = []
    for element in sorted(set(x["species"])):
        left = x["frac"][np.array(x["species"]) == element]
        right = y["frac"][np.array(y["species"]) == element]
        if not (np.isfinite(left).all() and np.isfinite(right).all()):
            raise GeometryContractError("NONFINITE_FRACTIONAL_COORDINATE")
        diff = (left[:, None, :] - right[None, :, :])
        diff = diff - np.rint(diff)
        xyz = (diff[:, :, None, :] + shifts[None, None, :, :]) @ a
        cost = np.linalg.norm(xyz, axis=-1).min(axis=2)
        rows, cols = linear_sum_assignment(cost)
        distances.extend(float(cost[u, v]) for u, v in zip(rows, cols))
    maximum = max(distances, default=float("inf"))
    mean = float(sum(distances) / len(distances)) if distances else float("inf")
    return {
        "atom_count": len(distances),
        "species_counts": dict(sorted(Counter(x["species"]).items())),
        "max_lattice_component_difference_angstrom": lattice_error,
        "max_species_matched_min_image_displacement_angstrom": maximum,
        "mean_species_matched_min_image_displacement_angstrom": mean,
        "fixed_tolerance_angstrom": FIXED_TOLERANCE_ANGSTROM,
        "sample_geometry_match": (
            lattice_error <= FIXED_TOLERANCE_ANGSTROM
            and maximum <= FIXED_TOLERANCE_ANGSTROM
        ),
    }


def extract_one_structure(raw: bytes, gb=SAMPLE_GB, element=SAMPLE_ELEMENT,
                          site=SAMPLE_SITE, verify=True) -> str:
    if verify:
        verify_source_bytes(raw)
    count = 0
    chosen = None
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") as z:
            with io.TextIOWrapper(z, encoding="utf-8", newline="") as f:
                csv.field_size_limit(20_000_000)
                r = csv.DictReader(f)
                if not {"GB", "element", "site", "structure_unrel"}.issubset(r.fieldnames or []):
                    raise GeometryContractError("SOURCE_COLUMNS_MISSING")
                for row in r:
                    if None in row:
                        raise GeometryContractError("MALFORMED_SOURCE_ROW")
                    if (row["GB"].strip(), row["element"].strip(),
                            row["site"].strip()) == (gb, element, site):
                        count += 1
                        chosen = row["structure_unrel"]
    except (OSError, EOFError, UnicodeError, csv.Error) as exc:
        raise GeometryContractError("SOURCE_COMPRESSION_OR_CSV_ERROR") from exc
    if count != 1 or _missing(chosen):
        raise GeometryContractError("MISSING_DUPLICATED_OR_BLANK_SOURCE_SAMPLE")
    return chosen


def get_pinned_author_file(full_name: str, path: str, expected_blob: str) -> bytes:
    url = ("https://raw.githubusercontent.com/" + full_name + "/" +
           UPSTREAM_COMMIT + "/" + path)
    with urlopen(Request(url, headers={"User-Agent":"BHS-input-provenance"}), timeout=30) as res:
        raw = res.read(MAX_INPUT_FILE_BYTES + 1)
    if not raw or len(raw) > MAX_INPUT_FILE_BYTES or _sha1_git_blob(raw) != expected_blob:
        raise GeometryContractError("SOURCE_INPUT_GIT_BLOB_MISMATCH")
    return raw


def load_example_inputs() -> tuple[bytes, bytes]:
    u = "https://api.github.com/repositories/" + str(REPO_ID)
    with urlopen(Request(u, headers={"User-Agent":"BHS-input-provenance",
                                    "Accept":"application/vnd.github+json"}), timeout=30) as res:
        repo = json.load(res)
    if repo.get("id") != REPO_ID or repo.get("private") is not False:
        raise GeometryContractError("SOURCE_REPOSITORY_IDENTITY_MISMATCH")
    full_name = repo["full_name"]
    return (get_pinned_author_file(full_name, INPUT_PATH, INPUT_BLOB),
            get_pinned_author_file(full_name, PARAMS_PATH, PARAMS_BLOB))


def audit_first_sample(source: bytes, poscar: bytes, params: bytes) -> dict:
    verification = verify_source_bytes(source)
    if _sha1_git_blob(poscar) != INPUT_BLOB or _sha1_git_blob(params) != PARAMS_BLOB:
        raise GeometryContractError("SAMPLE_INPUT_BLOB_MISMATCH")
    sample_structure = extract_one_structure(source)
    inp = parse_poscar(poscar)
    pub = parse_structure_repr(sample_structure)
    match = match_input_geometry(inp, pub)
    return {
        "schema": "BHS-V12.16-SINGLE-ORIGINAL-INPUT-LINEAGE",
        "source_commit": UPSTREAM_COMMIT,
        "source_csv_integrity": verification,
        "sample_key": [SAMPLE_GB, SAMPLE_ELEMENT, SAMPLE_SITE],
        "sample_poscar_git_blob": INPUT_BLOB,
        "sample_incar_git_blob": PARAMS_BLOB,
        "sample_poscar_sha256": hashlib.sha256(poscar).hexdigest(),
        "sample_incar_sha256": hashlib.sha256(params).hexdigest(),
        "author_archived_original_input_present": True,
        "matched_record_exactly_one": True,
        "input_geometry_comparison": match,
        "sample_input_structural_lineage_supported": match["sample_geometry_match"],
        "numerical_label_or_relaxed_structure_accessed": False,
        "real_expensive_calculation_timing_documented": False,
        "all_candidates_policy_time_accessible": False,
        "status": ("ONE_SAMPLE_GEOMETRIC_CONGRUENCE_ONLY_NOT_CHRONOLOGY"
                   if match["sample_geometry_match"] else
                   "ONE_SAMPLE_GEOMETRIC_MISMATCH_OR_UNRESOLVED"),
        "fair_comparison_authorized": False,
        **GATES,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    source = download_upstream()
    poscar, params = load_example_inputs()
    result = audit_first_sample(source, poscar, params)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("Original sample geometric match:", result["input_geometry_comparison"]["sample_geometry_match"])
    print("Original input atoms:", result["input_geometry_comparison"]["atom_count"])
    print("Max lattice difference:", result["input_geometry_comparison"]["max_lattice_component_difference_angstrom"])
    print("Max matched atom shift:", result["input_geometry_comparison"]["max_species_matched_min_image_displacement_angstrom"])
    print("Chronology and decision-time access: NOT CERTIFIED; scored comparison: BLOCKED")


if __name__ == "__main__":
    main()
