"""Fail-closed metadata gate for future real-data BHS offline acquisition.

This module validates *declared* metadata, not the truth of those declarations.
A future controlled acquisition step must independently verify the bytes,
license and split membership. No dataset is downloaded here.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Any
import json
import re

STATUS = "METADATA_DECLARATIONS_VALIDATED_NOT_DATA_VERIFIED"
EXPECTED_DATASET = "matbench_expt_gap"
EXPECTED_VERSION = "matbench_v0.1"
SHA256 = re.compile(r"^[0-9a-f]{64}$")

class DatasetGateError(ValueError):
    """Missing or invalid mandatory research metadata."""


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise DatasetGateError(f"{name} must be an object")
    return value


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DatasetGateError(f"{name} must be a nonempty string")
    return value.strip()


def _digest(value: Any, name: str) -> str:
    raw = _string(value, name)
    if not SHA256.fullmatch(raw):
        raise DatasetGateError(f"{name} must be a 64-character lowercase SHA-256 hex digest")
    return raw


def validate_manifest(value: Any) -> dict:
    """Validate research declarations; never mark data or splits as verified."""
    m = _mapping(value, "manifest")
    if m.get("schema_version") != "bhs-dataset-gate-v1":
        raise DatasetGateError("unexpected schema_version")
    dataset = _mapping(m.get("dataset"), "dataset")
    if dataset.get("name") != EXPECTED_DATASET or dataset.get("version") != EXPECTED_VERSION:
        raise DatasetGateError("dataset name/version not on approved initial list")
    for field in ("source_url", "source_record_id", "license_identifier", "license_source_url", "citation"):
        _string(dataset.get(field), f"dataset.{field}")
    if not dataset["source_url"].startswith("https://") or not dataset["license_source_url"].startswith("https://"):
        raise DatasetGateError("source and license evidence require HTTPS URLs")
    _digest(dataset.get("raw_sha256"), "dataset.raw_sha256")
    rows = dataset.get("expected_row_count")
    if isinstance(rows, bool) or not isinstance(rows, int) or rows != 4604:
        raise DatasetGateError("expected row count must be 4604; actual row count not yet verified")
    if dataset.get("feature_column") != "composition" or dataset.get("label_column") != "gap expt" or dataset.get("label_unit") != "eV":
        raise DatasetGateError("expected Matbench schema and eV unit required")

    split = _mapping(m.get("split"), "split")
    if split.get("strategy") != "composition_group_disjoint":
        raise DatasetGateError("require composition-group-disjoint split")
    for field in ("train_ids_sha256", "validation_ids_sha256", "test_ids_sha256", "group_definition_sha256"):
        _digest(split.get(field), f"split.{field}")
    if split.get("overlap_audit") != "PASS_VERIFIED_BY_SPLIT_BUILDER":
        raise DatasetGateError("require independently audited split grouping")
    if split.get("test_labels_locked") is not True:
        raise DatasetGateError("test labels must be locked")

    trial = _mapping(m.get("trial"), "trial")
    if trial.get("objective_type") != "target_band_gap_distance":
        raise DatasetGateError("unapproved scientific objective")
    target = trial.get("target_band_gap_ev")
    if isinstance(target, bool) or not isinstance(target, (int, float)) or not 0 < target < 20:
        raise DatasetGateError("target_band_gap_ev must be a finite plausible numeric value")
    import math
    if not math.isfinite(target):
        raise DatasetGateError("target_band_gap_ev must be finite")
    _string(trial.get("target_rationale"), "trial.target_rationale")
    budget = trial.get("query_budget")
    if isinstance(budget, bool) or not isinstance(budget, int) or not 0 < budget <= 4604:
        raise DatasetGateError("invalid query budget")
    seeds = trial.get("seeds")
    if not isinstance(seeds, list) or len(seeds) < 3 or len(set(map(str, seeds))) != len(seeds) or any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in seeds):
        raise DatasetGateError("seeds must be >=3 distinct nonnegative integers")
    if trial.get("hidden_label_access") != "QUERY_ONLY":
        raise DatasetGateError("hidden labels must be query-only")
    if trial.get("selection_without_replacement") is not True:
        raise DatasetGateError("selection must be without replacement")
    if trial.get("baseline_policy_status") != "NOT_EVALUATED":
        raise DatasetGateError("data gate cannot claim benchmark results")

    if m.get("real_data_ingested") is not False or m.get("benchmark_executed") is not False:
        raise DatasetGateError("this gate is metadata-only; data or result claims forbidden")
    return {"status": STATUS, "dataset_name": EXPECTED_DATASET, "version": EXPECTED_VERSION,
            "warning": "Declarations only; raw bytes, license terms, split integrity, leakage, and scientific suitability NOT independently verified"}


def validate_json_file(path: str | Path) -> dict:
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DatasetGateError("unreadable or invalid JSON manifest") from exc
    return validate_manifest(obj)
