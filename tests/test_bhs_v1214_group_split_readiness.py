"""V12.14 grouping-only fold audit tests. All fixtures are artificial and outcome-free."""
import csv
import gzip
import io
import json
import unittest
from unittest.mock import patch

from scripts import bhs_v1214_group_split_readiness as v


HEADERS = ("GB", "element", "Z", "site", "GB_site",
           "GB_element_site", "job_name", "E_seg")


def example(rows):
    s = io.StringIO(newline="")
    w = csv.writer(s)
    w.writerow(HEADERS)
    w.writerows(rows)
    return gzip.compress(s.getvalue().encode(), mtime=0)


def source_row(gb="B1", element="Ti", z="22.0", site="1", target="2.314"):
    return (gb, element, z, site, gb + "-" + site,
            gb + "-" + element + "-" + site,
            "job-" + gb + "-" + element + "-" + site, target)


def grid():
    return [source_row(g, e, str(z), site, "SECRET-OUTCOME")
            for g in ("B1", "B2")
            for e, z in (("Ti", 22), ("V", 23))
            for site in ("1", "2")]


def metadata(rows):
    return v.extract_metadata(example(rows), require_original=False)


class GroupSplitReadinessTests(unittest.TestCase):
    def test_source_only_grid_and_count(self):
        r = metadata(grid())
        self.assertEqual(len(r), 8)
        out = v.evaluate_metadata(r)
        self.assertEqual(out["gb_count"], 2)
        self.assertEqual(out["element_count"], 2)
        self.assertEqual(out["gb_site_count"], 4)
        self.assertEqual(out["fold_counts"],
                         {"leave_one_gb_out": 2,
                          "leave_one_element_out": 2,
                          "crossed_gb_element": 4})
        self.assertNotIn("SECRET-OUTCOME", json.dumps(out))

    def test_crossed_embargo_excludes_both_axes(self):
        r = metadata(grid())
        f = v.one_fold(r, "crossed_gb_element", gb="B1", element="Ti")
        self.assertEqual(f["train"]["rows"], 2)
        self.assertEqual(f["test"]["rows"], 2)
        self.assertEqual(f["embargo"]["rows"], 4)
        self.assertEqual(f["shared_gb_site_identifiers_train_test"], 0)

    def test_leave_element_out_retains_shared_structure_warning(self):
        f = v.one_fold(metadata(grid()), "leave_one_element_out", element="Ti")
        self.assertEqual(f["shared_gb_site_identifiers_train_test"], 4)
        self.assertFalse(f["group_disjoint"])
        self.assertEqual(f["embargo"]["rows"], 0)

    def test_leave_gb_out_has_zero_site_overlap(self):
        f = v.one_fold(metadata(grid()), "leave_one_gb_out", gb="B1")
        self.assertEqual(f["shared_gb_site_identifiers_train_test"], 0)
        self.assertTrue(f["group_disjoint"])

    def test_untested_group_is_not_a_valid_fold(self):
        with self.assertRaisesRegex(v.SplitContractError, "EMPTY_TRAIN_OR_TEST"):
            v.one_fold(metadata(grid()), "leave_one_gb_out", gb="missing")

    def test_malformed_combo_in_fold_rejected(self):
        with self.assertRaisesRegex(v.SplitContractError, "INVALID_FOLD_ID"):
            v.one_fold(metadata(grid()), "leave_one_gb_out", gb="B1", element="Ti")

    def test_row_order_does_not_change_report(self):
        rows = grid()
        a = v.evaluate_metadata(metadata(rows))
        b = v.evaluate_metadata(metadata(list(reversed(rows))))
        self.assertEqual(a, b)

    def test_target_magnitudes_never_change_report(self):
        rows = grid()
        a = v.evaluate_metadata(metadata(rows))
        rows = [r[:-1] + ("OTHER-UNREAD-VALUE",) for r in rows]
        b = v.evaluate_metadata(metadata(rows))
        self.assertEqual(a, b)
        self.assertFalse(a["scored_validation_allowed"])

    def test_target_missingness_is_preserved(self):
        rows = grid()
        rows[0] = rows[0][:-1] + ("",)
        a = v.evaluate_metadata(metadata(rows))
        self.assertEqual(a["source_target_blank_rows"], 1)
        self.assertEqual(a["source_target_nonblank_rows"], 7)
        self.assertEqual(a["crossed_test_target_all_blank_folds"], 0)

    def test_repeated_primitive_key_fails(self):
        rows = grid()
        rows[-1] = rows[0]
        with self.assertRaisesRegex(v.SplitContractError, "DUPLICATE_PRIMITIVE_KEY"):
            metadata(rows)

    def test_conflicting_atomic_number_fails(self):
        rows = grid()
        x = list(rows[2])
        x[2] = "99"
        rows[2] = tuple(x)
        with self.assertRaisesRegex(v.SplitContractError, "ATOMIC_NUMBER_CONFLICT"):
            metadata(rows)

    def test_decimal_nonintegral_atomic_number_fails(self):
        with self.assertRaisesRegex(v.SplitContractError, "INVALID_ATOMIC_NUMBER"):
            metadata([source_row(z="22.9")])

    def test_missing_identity_fails(self):
        with self.assertRaisesRegex(v.SplitContractError, "BAD_PRIMITIVE_IDENTITY"):
            metadata([source_row(gb="")])

    def test_unpinned_arbitrary_gzip_rejected_by_source_verification(self):
        raw = example(grid())
        with self.assertRaises(ValueError):
            v.extract_metadata(raw, require_original=True)

    def test_feature_gate_remains_closed(self):
        out = v.evaluate_metadata(metadata(grid()))
        self.assertEqual(out["eligible_numeric_predecision_features"], ["Z"])
        self.assertIn("E_seg", out["banned_free_prediction_columns"])
        self.assertIn("E_seg_unrel", out["banned_free_prediction_columns"])
        self.assertTrue(out["unverified_fidelity_cost"])
        self.assertFalse(out["scored_validation_allowed"])
        self.assertFalse(out["physical_validation_by_bhs"])
        self.assertFalse(out["claim_of_superiority"])

    def test_hash_identity_uses_tuple_not_joined_string(self):
        a=[{"id":("A-B", "C", "D"),"gb_site":"A","target_blank":False}]
        b=[{"id":("A", "B-C", "D"),"gb_site":"B","target_blank":False}]
        self.assertNotEqual(v.canonical_digest(a), v.canonical_digest(b))


if __name__ == "__main__":
    unittest.main()
