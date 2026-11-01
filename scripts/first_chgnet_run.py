#!/usr/bin/env python3
"""BHS one-candidate CHGNet experiment: explicit execution and honest provenance.

Default: validate a caller-supplied CIF and write a NOT_RUN manifest.
Execution: --execute --ack-model-download, requiring separate CHGNet install.
Never computes formation energy, hull stability, convergence proof, or discovery.
Run from the repository root: python scripts/first_chgnet_run.py ...
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import sys
from datetime import datetime, timezone


MAX_CIF_BYTES = 2_000_000
MAX_SITES = 200


def _package_version(name):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _utc():
    return datetime.now(timezone.utc).isoformat()


def _write_json(path, content):
    path.write_text(
        json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def prepare_input(cif_path):
    """Read caller-provided structure, rejecting large/invalid inputs."""
    from pymatgen.core import Structure

    if not cif_path.is_file():
        raise ValueError(f"Input CIF not found: {cif_path}")
    if cif_path.stat().st_size > MAX_CIF_BYTES:
        raise ValueError("CIF exceeds 2 MB limit")
    data = cif_path.read_bytes()
    if not data:
        raise ValueError("CIF is empty")
    try:
        structure = Structure.from_str(data.decode("utf-8-sig"), fmt="cif")
    except Exception as exc:
        raise ValueError("Cannot parse input CIF") from exc
    if not 0 < len(structure) <= MAX_SITES:
        raise ValueError("CIF must contain 1–200 sites")
    if not structure.is_ordered:
        raise ValueError("Disordered/partially occupied sites are not supported")
    return structure, hashlib.sha256(data).hexdigest()


def run_once(cif, out_dir, *, execute=False, ack_model_download=False):
    """Create immutable run directory and provenance, optionally run CHGNet.

    This intentionally does not use the orchestrator for arbitrary fmax/steps:
    it runs the audited MLFFValidator default (fmax=0.1, steps=100) once.
    """
    if execute and not ack_model_download:
        raise ValueError("--execute requires --ack-model-download")
    cif = Path(cif).expanduser()
    out = Path(out_dir).expanduser()
    # Validate before creating any outputs; no CHGNet import during a dry-run.
    structure, sha = prepare_input(cif)
    out.mkdir(parents=True, exist_ok=False)
    record = {
        "schema": "bhs_first_physics_run_v1",
        "started_utc": _utc(),
        "status": "NOT_RUN",
        "input": {
            "cif_filename": cif.name,
            "sha256": sha,
            "formula": str(structure.composition.reduced_formula),
            "site_count": len(structure),
            "source": "USER_SUPPLIED_CIF_UNVERIFIED",
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pymatgen": _package_version("pymatgen"),
            "numpy": _package_version("numpy"),
            "chgnet": _package_version("chgnet"),
            "torch": _package_version("torch"),
        },
        "settings": {
            "engine": "CHGNet",
            "device": "cpu",
            "fmax_ev_per_angstrom": 0.1,
            "max_relax_steps": 100,
            "relax_cell": True,
            "initial_model_weights_may_be_downloaded": bool(execute),
        },
        "result": {
            "potential_energy_total_ev": None,
            "potential_energy_ev_per_atom": None,
            "maximum_final_force_ev_per_angstrom": None,
            "minimum_interatomic_distance_angstrom": None,
            "relaxed_cif_sha256": None,
        },
        "scientific_claims": {
            "formation_energy": "NOT_CALCULATED",
            "energy_above_hull": "NOT_CALCULATED",
            "band_gap": "NOT_CALCULATED",
            "stability": "NOT_EVALUATED",
            "independent_convergence": "NOT_VERIFIED",
            "novel_material_discovery": "NOT_DEMONSTRATED",
            "experimental_validation": "NOT_PERFORMED",
        },
        "ended_utc": None,
        "error": None,
    }
    manifest = out / "run_manifest.json"
    _write_json(manifest, record)
    if not execute:
        record["ended_utc"] = _utc()
        _write_json(manifest, record)
        return record

    record["status"] = "RUNNING"
    _write_json(manifest, record)
    try:
        from src.imd_pipeline.validation.mlff_validator import MLFFValidator

        raw = MLFFValidator(use_gpu=False).evaluate_and_relax(
            structure, fmax=0.1, steps=100
        )
        if (
            raw.get("engine") != "CHGNet"
            or raw.get("execution_status") != "CHGNET_OPTIMIZER_RETURNED_OUTPUT"
            or raw.get("model_output_provenance")
            != "MLFF_PREDICTION_NOT_EXPERIMENT"
        ):
            raise RuntimeError("CHGNet provenance validation failed")
        relaxed = raw["relaxed_structure"]
        if len(relaxed) != len(structure) or relaxed.composition != structure.composition:
            raise RuntimeError("Relaxed candidate composition changed")
        total = float(raw["potential_energy_total_ev"])
        per_atom = float(raw["potential_energy_ev_per_atom"])
        if (not math.isfinite(total) or not math.isfinite(per_atom)
                or not math.isclose(total, per_atom * len(relaxed), rel_tol=1e-7, abs_tol=1e-7)):
            raise RuntimeError("CHGNet energies invalid or inconsistent")
        from pymatgen.io.cif import CifWriter
        cif_text = str(CifWriter(relaxed))
        output_data = cif_text.encode("utf-8")
        (out / "relaxed_structure.cif").write_bytes(output_data)
        record["result"] = {
            "potential_energy_total_ev": total,
            "potential_energy_ev_per_atom": per_atom,
            "maximum_final_force_ev_per_angstrom": raw.get("max_force"),
            "minimum_interatomic_distance_angstrom": raw.get("min_distance"),
            "relaxed_cif_sha256": hashlib.sha256(output_data).hexdigest(),
        }
        record["status"] = "CHGNET_OPTIMIZER_RETURNED_OUTPUT"
    except Exception as exc:
        record["status"] = "FAILED"
        record["error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "note": "No fallback physics value was substituted",
        }
    finally:
        record["ended_utc"] = _utc()
        _write_json(manifest, record)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cif", type=Path, required=True, help="Caller-supplied CIF file")
    parser.add_argument("--out-dir", type=Path, required=True, help="Fresh result directory")
    parser.add_argument("--execute", action="store_true", help="Explicitly run CHGNet")
    parser.add_argument(
        "--ack-model-download",
        action="store_true",
        help="Acknowledge that running CHGNet may download pretrained model weights",
    )
    args = parser.parse_args(argv)
    try:
        result = run_once(
            args.cif, args.out_dir,
            execute=args.execute, ack_model_download=args.ack_model_download
        )
    except (ValueError, OSError) as exc:
        parser.exit(2, f"INPUT ERROR: {exc}\n")
    print(json.dumps(
        {"status": result["status"],
         "manifest": str(args.out_dir / "run_manifest.json"),
         "predicted_potential_energy_ev_per_atom":
             result["result"]["potential_energy_ev_per_atom"]},
        indent=2,
    ))
    return 0 if result["status"] in ("NOT_RUN", "CHGNET_OPTIMIZER_RETURNED_OUTPUT") else 1


if __name__ == "__main__":
    sys.exit(main())
