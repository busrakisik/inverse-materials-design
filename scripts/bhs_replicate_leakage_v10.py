"""Replicate-aware validation audit of a historical mechanical-experiment archive.

The real measurements were made by the original research groups, not BHS.
This is a DEVELOPMENT-ONLY retrospective validation-method audit, not new
physical experimentation, causal identification or independent evaluation.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from collections import defaultdict
from pathlib import Path
from urllib.request import urlopen

import numpy as np

SOURCE_COMMIT = "7585c517ad88e676c42c6bf24a8ad278e01ddb21"
SOURCE_BLOB_SHA1 = "b007fe5d8762233bbd23c8cf83858b169f05492a"
SOURCE_URL = (
    "https://raw.githubusercontent.com/PV-Lab/Benchmarking/"
    + SOURCE_COMMIT + "/datasets/Crossed%20barrel_dataset.csv"
)
SOURCE_COLUMNS = ("n", "theta", "r", "t", "toughness")
SOURCE_ROWS = 1800
SOURCE_GEOMETRIES = 600
REPEATS_PER_GEOMETRY = 3
DEVELOPMENT_SEEDS = (7, 13, 23, 31, 43)
RESERVED_SEEDS = range(10000, 10100)
TEST_FRACTION = 0.25
FOREST_PARAMETERS = {
    "n_estimators": 120,
    "min_samples_leaf": 2,
    "max_features": 1.0,
    "n_jobs": 1,
}


class DataContractError(ValueError):
    """Source integrity or structural assumptions were not met."""


def checked_git_blob(source: bytes) -> str:
    if not isinstance(source, bytes):
        raise DataContractError("SOURCE_NOT_RAW_BYTES")
    sha = hashlib.sha1(b"blob " + str(len(source)).encode() + b"\0" + source).hexdigest()
    if sha != SOURCE_BLOB_SHA1:
        raise DataContractError("GIT_SOURCE_BLOB_MISMATCH")
    return sha


def parse_source(source: bytes, *, require_pinned_blob=True):
    import pandas as pd
    if require_pinned_blob:
        checked_git_blob(source)
    try:
        table = pd.read_csv(io.BytesIO(source))
        if tuple(table.columns) != SOURCE_COLUMNS:
            raise DataContractError("UNEXPECTED_COLUMN_SCHEMA")
        if table.shape != (SOURCE_ROWS, len(SOURCE_COLUMNS)):
            raise DataContractError("UNEXPECTED_MEASUREMENT_COUNT")
        if any(not pd.api.types.is_numeric_dtype(table[col]) for col in SOURCE_COLUMNS):
            raise DataContractError("NONNUMERIC_MEASUREMENT")
        X = table[list(SOURCE_COLUMNS[:4])].to_numpy(dtype=float)
        y = table["toughness"].to_numpy(dtype=float)
    except DataContractError:
        raise
    except (ValueError, TypeError, UnicodeError, pd.errors.ParserError) as exc:
        raise DataContractError("SOURCE_PARSE_FAILED") from exc
    return validate_measurements(X, y)


def validate_measurements(X, y):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).reshape(-1)
    if X.shape != (SOURCE_ROWS, 4) or y.shape != (SOURCE_ROWS,):
        raise DataContractError("UNEXPECTED_MEASUREMENT_COUNT")
    if not (np.isfinite(X).all() and np.isfinite(y).all()):
        raise DataContractError("NONFINITE_MEASUREMENT")
    if (np.any(X[:, 0] <= 0)
        or np.any(X[:, 0] != np.floor(X[:, 0]))
        or np.any(X[:, 1] < 0)
        or np.any(X[:, 1] > 360)
        or np.any(X[:, 2] <= 0)
        or np.any(X[:, 3] <= 0)
        or np.any(X[:, 3] > X[:, 2])
        or np.any(y < 0)):
        raise DataContractError("INVALID_MECHANICAL_DESIGN_OR_RESPONSE")
    geometry, group = np.unique(X, axis=0, return_inverse=True)
    if len(geometry) != SOURCE_GEOMETRIES:
        raise DataContractError("UNEXPECTED_GEOMETRY_COUNT")
    counts = np.bincount(group)
    if len(counts) != SOURCE_GEOMETRIES or np.any(counts != REPEATS_PER_GEOMETRY):
        raise DataContractError("NONTRIPLICATE_GEOMETRY")
    return X, y, group


def replicate_summary(y, group):
    y = np.asarray(y, dtype=float)
    group = np.asarray(group, dtype=int)
    means = []
    deviations = []
    sds = []
    spans = []
    for g in sorted(np.unique(group)):
        measurements = y[group == g]
        if len(measurements) != REPEATS_PER_GEOMETRY:
            raise DataContractError("NONTRIPLICATE_GEOMETRY")
        mu = float(np.mean(measurements))
        means.append(mu)
        deviations.extend((measurements - mu).tolist())
        sds.append(float(np.std(measurements, ddof=1)))
        spans.append(float(np.ptp(measurements)))
    return {
        "profile_count": len(sds),
        "measurements_per_profile": REPEATS_PER_GEOMETRY,
        "fraction_profiles_nonzero_span": float(np.mean(np.asarray(spans) > 1e-12)),
        "sample_sd_joule_median": float(np.median(sds)),
        "sample_sd_joule_p90": float(np.quantile(sds, 0.90)),
        "sample_sd_joule_max": float(np.max(sds)),
        "replicate_range_joule_median": float(np.median(spans)),
        "replicate_range_joule_p90": float(np.quantile(spans, 0.90)),
        "replicate_range_joule_max": float(np.max(spans)),
        "within_profile_rms_deviation_joule": float(np.sqrt(np.mean(np.square(deviations)))),
        "measurement_noise_is_calibrated": False,
        "batch_variance_is_identified": False,
    }


def require_development_seeds(seeds):
    if not seeds or any(
            isinstance(s, bool) or not isinstance(s, (int, np.integer))
            or s < 0 or s in RESERVED_SEEDS for s in seeds):
        raise ValueError("DEVELOPMENT_SEEDS_ONLY; reserved 10000..10099 prohibited")


def split_diagnostics(X, y, group, train, test, seed, protocol):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    train, test = np.asarray(train, dtype=int), np.asarray(test, dtype=int)
    if (len(set(train.tolist())) != len(train)
        or len(set(test.tolist())) != len(test)
        or set(train.tolist()).intersection(test.tolist())
        or len(train) + len(test) != len(y)):
        raise DataContractError("TRAIN_TEST_INDEX_OVERLAP_OR_MISSING_ROWS")
    seen_geometry = set(group[train].tolist())
    previously_seen = np.array([int(g) in seen_geometry for g in group[test]])
    if protocol == "geometry_grouped" and np.any(previously_seen):
        raise DataContractError("GROUPED_SPLIT_LEAKS_GEOMETRY")
    model = RandomForestRegressor(random_state=int(seed), **FOREST_PARAMETERS)
    model.fit(X[train], y[train])
    predictions = model.predict(X[test])
    memo = defaultdict(list)
    for i in train:
        memo[int(group[i])].append(float(y[i]))
    covered = test[previously_seen]
    lookup_mae = None
    if len(covered):
        lookup = np.asarray([np.mean(memo[int(group[i])]) for i in covered], dtype=float)
        lookup_mae = float(mean_absolute_error(y[covered], lookup))
    return {
        "seed": int(seed),
        "protocol": protocol,
        "train_measurements": int(len(train)),
        "test_measurements": int(len(test)),
        "train_unique_geometries": int(len(set(group[train].tolist()))),
        "test_unique_geometries": int(len(set(group[test].tolist()))),
        "test_measurement_fraction_with_geometry_seen_in_training": float(np.mean(previously_seen)),
        "random_forest_mae_joule": float(mean_absolute_error(y[test], predictions)),
        "random_forest_rmse_joule": float(np.sqrt(mean_squared_error(y[test], predictions))),
        "geometry_lookup_test_coverage": float(np.mean(previously_seen)),
        "geometry_lookup_mae_joule_when_supported": lookup_mae,
        "model_is_predeclared_baseline_not_bhs": True,
    }


def audit_development(X, y, group, seeds=DEVELOPMENT_SEEDS):
    from sklearn.model_selection import GroupShuffleSplit, train_test_split
    require_development_seeds(seeds)
    results = []
    all_rows = np.arange(len(y))
    for seed in seeds:
        train_row, test_row = train_test_split(
            all_rows, test_size=TEST_FRACTION, random_state=int(seed), shuffle=True)
        results.append(split_diagnostics(
            X, y, group, train_row, test_row, int(seed), "measurement_row_random"))
        train_group, test_group = next(GroupShuffleSplit(
            n_splits=1, test_size=TEST_FRACTION, random_state=int(seed)
        ).split(X, y, groups=group))
        results.append(split_diagnostics(
            X, y, group, train_group, test_group, int(seed), "geometry_grouped"))
    by_protocol = {}
    for name in ("measurement_row_random", "geometry_grouped"):
        subset = [r for r in results if r["protocol"] == name]
        maes = [r["random_forest_mae_joule"] for r in subset]
        seen = [r["test_measurement_fraction_with_geometry_seen_in_training"] for r in subset]
        by_protocol[name] = {
            "development_partitions": len(subset),
            "mae_joule_mean": float(np.mean(maes)),
            "mae_joule_median": float(np.median(maes)),
            "mae_joule_min": float(min(maes)),
            "mae_joule_max": float(max(maes)),
            "mean_test_fraction_seen_geometry": float(np.mean(seen)),
        }
    return results, by_protocol


def build_report(X, y, group, raw_sha256):
    row_results, summary = audit_development(X, y, group)
    return {
        "study": "BHS v10 replicate-aware mechanical measurements evaluation audit",
        "source": {
            "repository": "PV-Lab/Benchmarking",
            "publication_doi": "10.1038/s41524-021-00656-9",
            "original_experiment_doi": "10.1126/sciadv.aaz1708",
            "source_commit": SOURCE_COMMIT,
            "original_csv_git_blob_sha1": SOURCE_BLOB_SHA1,
            "downloaded_raw_csv_sha256": raw_sha256,
            "public_repository_license": "MIT",
            "raw_data_redistributed": False,
        },
        "data_contract": {
            "measurements": SOURCE_ROWS,
            "distinct_geometry_profiles": SOURCE_GEOMETRIES,
            "replicates_per_profile": REPEATS_PER_GEOMETRY,
            "predictors": list(SOURCE_COLUMNS[:4]),
            "target": "toughness",
            "target_unit": "joule",
            "geometry_feature_grouping": "exact_numeric_vector",
            "all_data_are_original_historical_measurements": True,
            "bhs_performed_new_physical_experiments": False,
        },
        "repeatability": replicate_summary(y, group),
        "protocol": {
            "reference_model": "fixed_random_forest",
            "parameters": FOREST_PARAMETERS,
            "development_seeds": list(DEVELOPMENT_SEEDS),
            "reserved_independent_seeds_used": False,
            "test_fraction": TEST_FRACTION,
            "metrics": ["mae_joule", "rmse_joule", "seen_geometry_fraction"],
            "evaluation_scope": "retrospective development split methodology audit",
        },
        "results_by_seed": row_results,
        "aggregate_by_protocol": summary,
        "decision": {
            "status": "REQUIRE_GEOMETRY_GROUPED_EVALUATION_FOR_NEW_GEOMETRY_CLAIMS",
            "reason_codes": [
                "REPEATED_MEASUREMENTS_ARE_NOT_DISTINCT_GEOMETRIES",
                "ROW_RANDOM_SPLIT_MAY_INCLUDE_SAME_GEOMETRY_IN_TRAIN_AND_TEST",
                "UNVERIFIED_BATCH_PROCESS_AND_PRINTER_INDEPENDENCE",
                "NO_UNTOUCHED_PROSPECTIVE_LABORATORY_EVALUATION",
            ],
            "laboratory_action_authorized": False,
        },
        "hard_gates": {
            "development_only": True,
            "scored_validation_allowed": False,
            "independent_holdout_used": False,
            "physical_validation_by_bhs": False,
            "calibrated_uncertainty_proven": False,
            "causal_identification": False,
            "method_superiority_claimed": False,
            "measured_cost_savings": False,
        },
    }


def fetch_pinned_source():
    with urlopen(SOURCE_URL, timeout=45) as response:
        raw = response.read()
    checked_git_blob(raw)
    return raw


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--execute", action="store_true",
                   help="Fetch pinned historical external measurements and run development audit.")
    p.add_argument("--out", default="runs/bhs_replicate_leakage_v10.json")
    args = p.parse_args(argv)
    if not args.execute:
        print("Study protocol only: data download and label evaluation disabled.")
        return 0
    raw = fetch_pinned_source()
    X, y, group = parse_source(raw)
    report = build_report(X, y, group, hashlib.sha256(raw).hexdigest())
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "repeatability": report["repeatability"],
        "aggregate_by_protocol": report["aggregate_by_protocol"],
        "decision": report["decision"]["status"],
        "development_only": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
