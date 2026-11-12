"""Adversarial source-intake tests; all records here are manufactured."""
from __future__ import annotations

import csv
import gzip
import io
import json
import unittest
from unittest.mock import patch

from scripts import bhs_v1213_source_intake as mod

HEADERS = ["GB", "element", "Z", "site", "GB_site", "GB_element_site",
           "job_name", "E_seg"]


def fixture(rows, headers=HEADERS):
    stream = io.StringIO(newline="")
    w = csv.writer(stream)
    w.writerow(headers)
    w.writerows(rows)
    return gzip.compress(stream.getvalue().encode("utf-8"), mtime=0)


def row(gb="B1", el="Ti", z="22", site="0", target="-0.55"):
    return [gb, el, z, site, gb + "-" + site,
            gb + "-" + el + "-" + site, "j-" + gb + "-" + el + "-" + site, target]


class IntakeTests(unittest.TestCase):
    def test_true_unique_groups_and_target_blanks(self):
        raw = fixture([row(), row("B1", "V", "23", "0", ""),
                       row("B2", "Ti", "22", "2", "not-a-number")])
        a = mod.scan_source(raw, expected_rows=3, expected_columns=8)
        self.assertEqual(a["row_count"], 3)
        self.assertEqual(a["boundary_count"], 2)
        self.assertEqual(a["element_count"], 2)
        self.assertEqual(a["boundary_element_groups"], 3)
        self.assertEqual(a["unique_boundary_site_ids"], 2)
        self.assertEqual(a["missing_target_strings"], 1)
        self.assertEqual(a["structural_problems"], [])
        self.assertNotIn("not-a-number", json.dumps(a))

    def test_duplicate_physical_record_identity_is_blocked(self):
        x = [row(), row()]
        x[1][6] = "other-job-name"
        self.assertIn("DUPLICATE_RECORD_IDENTIFIER", mod.scan_source(fixture(x))["structural_problems"])

    def test_atomic_number_conflict_is_blocked(self):
        a = mod.scan_source(fixture([row(), row("B2", "Ti", "23", "1")]))
        self.assertIn("ATOMIC_NUMBER_CONFLICT", a["structural_problems"])

    def test_noninteger_atomic_number_is_blocked(self):
        self.assertIn("ATOMIC_NUMBER_INVALID",
                      mod.scan_source(fixture([row(z="22.5")]))["structural_problems"])

    def test_missing_identifier_fails_closed(self):
        self.assertIn("MISSING_REQUIRED_IDENTITY",
                      mod.scan_source(fixture([row(gb="")]))["structural_problems"])

    def test_record_count_readme_mismatch_fails_closed(self):
        self.assertIn("ROW_COUNT_MISMATCH",
                      mod.scan_source(fixture([row()]), expected_rows=2)["structural_problems"])

    def test_column_count_readme_mismatch_fails_closed(self):
        self.assertIn("COLUMN_COUNT_MISMATCH",
                      mod.scan_source(fixture([row()]), expected_columns=90)["structural_problems"])

    def test_missing_target_column_rejected(self):
        with self.assertRaisesRegex(mod.SourceContractError, "REQUIRED_SOURCE_COLUMNS_MISSING"):
            mod.scan_source(fixture([row()[:-1]], headers=HEADERS[:-1]))

    def test_duplicated_header_rejected(self):
        with self.assertRaisesRegex(mod.SourceContractError, "MISSING_OR_DUPLICATED_HEADERS"):
            mod.scan_source(fixture([row() + ["unused"]], headers=HEADERS + ["GB"]))

    def test_gzip_truncation_is_a_hard_failure(self):
        with self.assertRaisesRegex(mod.SourceContractError, "SOURCE_DECOMPRESSION_OR_CSV_ERROR"):
            mod.scan_source(fixture([row()])[:-6])

    def test_pinned_source_rejects_small_untrusted_fixture(self):
        with self.assertRaisesRegex(mod.SourceContractError, "SOURCE_SIZE_MISMATCH"):
            mod.verify_source_bytes(fixture([row()]))

    def test_pinned_source_rejects_wrong_blob_with_correct_size(self):
        with patch.object(mod, "FILE_SIZE", len(fixture([row()]))):
            with self.assertRaisesRegex(mod.SourceContractError, "SOURCE_GIT_BLOB_MISMATCH"):
                mod.verify_source_bytes(fixture([row()]))

    def test_audit_never_promotes_fixture_to_evaluation(self):
        raw = fixture([row()])
        with patch.object(mod, "verify_source_bytes",
                          return_value={"source_bytes": len(raw),
                                        "source_sha256": "test-only",
                                        "source_git_blob": "test-only"}):
            a = mod.audit(raw)
        self.assertEqual(a["intake_status"], "INTAKE_BLOCKED")
        self.assertFalse(a["scored_validation_allowed"])
        self.assertFalse(a["physical_validation_by_bhs"])
        self.assertFalse(a["claim_of_superiority"])
        self.assertFalse(a["target_magnitudes_inspected"])
        self.assertEqual(a["outcome_free_feature_whitelist"], [])

    def test_row_order_permutation_invariance(self):
        rows = [row(), row("B1", "V", "23", "1"), row("B2", "Ti", "22", "0")]
        a = mod.scan_source(fixture(rows))
        b = mod.scan_source(fixture(list(reversed(rows))))
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
