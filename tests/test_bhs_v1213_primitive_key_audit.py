"""Exact source identity tests using constructed, non-scored records."""
import csv
import gzip
import io
import unittest
from unittest.mock import patch

from scripts import bhs_v1213_primitive_key_audit as mod


def packed(rows):
    stream = io.StringIO(newline="")
    w = csv.writer(stream)
    w.writerow(("GB", "element", "site", "job_name", "GB_site", "GB_element_site", "E_seg"))
    w.writerows(rows)
    return gzip.compress(stream.getvalue().encode(), mtime=0)


def item(gb="G1", el="Ni", site="1", combined=None, target="secret-value"):
    return (gb, el, site, f"job-{gb}-{el}-{site}", f"{gb}-{site}",
            combined if combined is not None else f"{gb}-{el}-{site}", target)


class PrimitiveIdentityTests(unittest.TestCase):
    def inspect(self, data):
        raw=packed(data)
        with patch.object(mod, "verify_source_bytes", return_value={
                "source_bytes": len(raw), "source_git_blob": "test",
                "source_sha256": "test"}):
            return mod.assess_keys(raw)

    def test_unique_primitives_do_not_restore_missing_source_value(self):
        one = list(item())
        one[5] = ""
        s = self.inspect([one, item(site="2")])
        self.assertEqual(s["primitive_key_cardinality"], 2)
        self.assertTrue(s["primitive_key_identifiable"])
        self.assertEqual(s["missing_original_combined_identifiers"], 1)
        self.assertFalse(s["raw_combined_identifiers_repaired"])
        self.assertFalse(s["scored_benchmark_eligible"])

    def test_repeated_primitive_is_not_collapsed(self):
        s=self.inspect([item(), item()])
        self.assertEqual(s["total_source_records"], 2)
        self.assertEqual(s["duplicate_primitive_key_excess_rows"], 1)
        self.assertEqual(s["duplicate_job_name_excess_rows"], 1)
        self.assertFalse(s["primitive_key_identifiable"])

    def test_missing_primitive_blocks_key_reconstruction(self):
        s=self.inspect([item(site="")])
        self.assertFalse(s["primitive_key_identifiable"])
        self.assertEqual(s["missing_primitive_fields"]["site"], 1)

    def test_target_missingness_is_only_boolean(self):
        a=list(item())
        a[5]=""
        a[6]="nan"
        s=self.inspect([a,item(site="2",target="4.12")])
        self.assertEqual(s["missing_target_strings_total"],1)
        self.assertEqual(s["missing_target_strings_with_missing_combined_id"],1)
        self.assertNotIn("4.12",str(s))

    def test_no_success_state_from_perfect_source(self):
        s=self.inspect([item()])
        self.assertFalse(s["scored_validation_allowed"])
        self.assertFalse(s["physical_validation_by_bhs"])
        self.assertFalse(s["claim_of_superiority"])
        self.assertFalse(s["independent_holdout_used"])
        self.assertEqual(s["audit_status"], "IDENTIFIER_RECOVERY_DIAGNOSTIC_ONLY")

    def test_row_order_invariance(self):
        x=[item(site="3"), item(site="4"),item(site="5")]
        self.assertEqual(self.inspect(x),self.inspect(list(reversed(x))))


if __name__ == "__main__":
    unittest.main()
