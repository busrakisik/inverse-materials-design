"""Deterministic synthetic contracts for real-materials replicate-aware audits."""
import hashlib
import io
import unittest

import numpy as np

from scripts.bhs_replicate_leakage_v10 import (
    SOURCE_BLOB_SHA1, SOURCE_GEOMETRIES, SOURCE_ROWS,
    SOURCE_COLUMNS, DataContractError, audit_development,
    checked_git_blob, main, parse_source, replicate_summary,
    require_development_seeds, split_diagnostics, validate_measurements,
)


def synthetic_triplicates():
    # Six hundred unique geometries, each observed exactly three times.
    X, y = [], []
    for k in range(SOURCE_GEOMETRIES):
        geom = [float(6 + 2 * (k % 5)), float(k // 5), 2.0, 0.7]
        center = 15.0 + (k % 11) * 0.5
        for offset in (-1.0, 0.0, 1.0):
            X.append(geom)
            y.append(center + offset)
    return validate_measurements(np.asarray(X), np.asarray(y))


def make_synthetic_csv():
    X, y, _ = synthetic_triplicates()
    lines = [",".join(SOURCE_COLUMNS)]
    for geom, strength in zip(X, y):
        lines.append(",".join(str(float(x)) for x in geom) + "," + str(float(strength)))
    return ("\n".join(lines) + "\n").encode()


class ReplicateAwareContracts(unittest.TestCase):
    def test_600_designs_have_1800_measurements(self):
        X, y, group = synthetic_triplicates()
        self.assertEqual(X.shape, (SOURCE_ROWS, 4))
        self.assertEqual(len(np.unique(group)), SOURCE_GEOMETRIES)
        np.testing.assert_array_equal(
            np.bincount(group), np.full(SOURCE_GEOMETRIES, 3))

    def test_replicate_noise_descriptive_not_calibrated(self):
        _, y, group = synthetic_triplicates()
        s = replicate_summary(y, group)
        self.assertEqual(s["profile_count"], 600)
        self.assertAlmostEqual(s["sample_sd_joule_median"], 1.0)
        self.assertAlmostEqual(s["replicate_range_joule_max"], 2.0)
        self.assertFalse(s["measurement_noise_is_calibrated"])

    def test_corrupted_header_rejected(self):
        bad = make_synthetic_csv().replace(b"toughness\n", b"output\n", 1)
        with self.assertRaisesRegex(DataContractError, "UNEXPECTED_COLUMN_SCHEMA"):
            parse_source(bad, require_pinned_blob=False)

    def test_nonfinite_measurement_rejected(self):
        X, y, _ = synthetic_triplicates()
        y[0] = np.nan
        with self.assertRaisesRegex(DataContractError, "NONFINITE_MEASUREMENT"):
            validate_measurements(X, y)

    def test_wrong_geometry_count_rejected(self):
        X, y, _ = synthetic_triplicates()
        X[:3] = X[3]
        with self.assertRaisesRegex(DataContractError, "UNEXPECTED_GEOMETRY_COUNT"):
            validate_measurements(X, y)

    def test_nontriplicate_geometry_rejected(self):
        X, y, _ = synthetic_triplicates()
        X[0] = X[3]
        # Keep all 600 geometries while changing two repeat counts from 3.
        with self.assertRaisesRegex(DataContractError, "NONTRIPLICATE_GEOMETRY"):
            validate_measurements(X, y)

    def test_invalid_design_rejected(self):
        X, y, _ = synthetic_triplicates()
        X[0, 3] = 3.0   # wall thickness cannot exceed outer radius
        with self.assertRaisesRegex(DataContractError, "INVALID_MECHANICAL_DESIGN"):
            validate_measurements(X, y)

    def test_no_unverified_source_blob_accepted(self):
        with self.assertRaisesRegex(DataContractError, "GIT_SOURCE_BLOB_MISMATCH"):
            checked_git_blob(b"unverified source content")
        self.assertEqual(len(SOURCE_BLOB_SHA1), 40)

    def test_bad_raw_schema_must_not_bypass_pinning(self):
        valid_synthetic = make_synthetic_csv()
        with self.assertRaisesRegex(DataContractError, "GIT_SOURCE_BLOB_MISMATCH"):
            parse_source(valid_synthetic)
        _, y, group = parse_source(valid_synthetic, require_pinned_blob=False)
        self.assertEqual(len(y), 1800)
        self.assertEqual(len(np.unique(group)), 600)

    def test_development_seed_guard(self):
        require_development_seeds((7, 13, 23, 31, 43))
        for seed in (10000, 10054, 10099, -1, True):
            with self.assertRaisesRegex(ValueError, "DEVELOPMENT_SEEDS_ONLY"):
                require_development_seeds((seed,))

    def test_group_holdout_cannot_share_geometry(self):
        X, y, group = synthetic_triplicates()
        cases, result = audit_development(X, y, seeds=(7,))
        row = next(x for x in cases if x["protocol"] == "measurement_row_random")
        grouped = next(x for x in cases if x["protocol"] == "geometry_grouped")
        self.assertGreater(row["test_measurement_fraction_with_geometry_seen_in_training"], 0.80)
        self.assertEqual(grouped["test_measurement_fraction_with_geometry_seen_in_training"], 0.0)
        self.assertEqual(grouped["test_unique_geometries"], 150)
        self.assertEqual(grouped["test_measurements"], 450)
        self.assertIsNone(grouped["geometry_lookup_mae_joule_when_supported"])
        self.assertGreaterEqual(row["random_forest_mae_joule"], 0.0)
        self.assertGreaterEqual(grouped["random_forest_mae_joule"], 0.0)

    def test_overlapping_train_and_test_indices_rejected(self):
        X, y, group = synthetic_triplicates()
        with self.assertRaisesRegex(DataContractError, "TRAIN_TEST_INDEX_OVERLAP"):
            split_diagnostics(X, y, group, np.arange(1000),
                              np.arange(900, 1800), 7, "measurement_row_random")

    def test_do_not_download_without_execute(self):
        self.assertEqual(main([]), 0)


if __name__ == "__main__":
    unittest.main()
