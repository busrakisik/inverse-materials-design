"""Outcome-free source identity attribution tests on manufactured records."""
import csv
import gzip
import io
import unittest
from unittest.mock import patch

from scripts import bhs_v1213_identity_diagnostic as mod


def example(rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["GB", "element", "Z", "site", "GB_site", "GB_element_site", "job_name", "E_seg"])
    writer.writerows(rows)
    return gzip.compress(stream.getvalue().encode("utf-8"), mtime=0)


def record(gb="B1", element="V", z="23", site="3", energy="2.5"):
    return [gb, element, z, site, gb + "-" + site, gb + "-" + element + "-" + site,
            "job-" + element + "-" + site, energy]


class IdentityDiagnosticTests(unittest.TestCase):
    def diagnose_example(self, rows):
        raw = example(rows)
        with patch.object(mod, "verify_source_bytes", return_value={
                "source_git_blob": "example", "source_sha256": "example",
                "source_bytes": len(raw)}):
            return mod.diagnose(raw)

    def test_two_independent_identity_missing_patterns(self):
        a = record()
        b = record(site="")
        b[4] = "B1-x"
        c = record(gb="", energy="")
        report = self.diagnose_example([a, b, c])
        self.assertEqual(report["total_records"], 3)
        self.assertEqual(report["complete_identifier_records"], 1)
        self.assertEqual(report["missing_identifier_records"], 2)
        self.assertEqual(report["missing_identifier_columns"]["site"], 1)
        self.assertEqual(report["missing_identifier_columns"]["GB"], 1)
        self.assertEqual(report["missing_target_strings"], 1)

    def test_multiple_missing_fields_are_one_record(self):
        r = record(site="")
        r[4] = ""
        a = self.diagnose_example([r])
        self.assertEqual(a["missing_identifier_records"], 1)
        self.assertEqual(sum(a["missing_identifier_columns"].values()), 2)

    def test_no_real_target_value_appears_in_report(self):
        a = self.diagnose_example([record(energy="SECRET-PHYSICAL-VALUE")])
        self.assertNotIn("SECRET-PHYSICAL-VALUE", str(a))
        self.assertFalse(a["target_magnitudes_inspected"])
        self.assertFalse(a["next_stage_eligible"])

    def test_all_complete_records_still_do_not_unlock_validation(self):
        a = self.diagnose_example([record()])
        self.assertEqual(a["missing_identifier_records"], 0)
        self.assertFalse(a["scored_validation_allowed"])
        self.assertFalse(a["physical_validation_by_bhs"])
        self.assertFalse(a["independent_holdout_used"])
        self.assertEqual(a["audit_status"], "DIAGNOSTIC_ONLY_NO_GO")

    def test_blank_target_count_does_not_score_values(self):
        a = self.diagnose_example([record(energy="NaN"), record(site="4", energy="3")])
        self.assertEqual(a["missing_target_strings"], 1)
        self.assertFalse(a["outcome_score_calculated"])


if __name__ == "__main__":
    unittest.main()
