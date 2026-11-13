"""Source-element cardinality diagnosis tests on manufactured, outcome-free rows."""
import csv
import gzip
import io
import unittest
from scripts.bhs_v1214_element_cardinality_diagnostic import audit_element_coverage


def make(rows):
    b=io.StringIO(newline="")
    w=csv.writer(b)
    w.writerow(("GB","element","Z","site","GB_element_site","E_seg"))
    w.writerows(rows)
    return gzip.compress(b.getvalue().encode(), mtime=0)


class ElementAuditTests(unittest.TestCase):
    def test_elements_in_missing_combined_group(self):
        rows=[("G1","Ni","28","1","G1_Ni_1","3.2"),
              ("G1","Ni","28","2","","missing"),
              ("G2","Xe","54","1","","not-used")]
        x=audit_element_coverage(make(rows),verify=False)
        self.assertEqual(x["full_element_count"],2)
        self.assertEqual(x["complete_combined_id_element_count"],1)
        self.assertEqual(x["elements_only_in_incomplete_id_subset"],["Xe"])
        self.assertEqual(x["rows_for_elements_only_in_incomplete_subset"]["Xe"],1)
        self.assertEqual(x["missing_target_strings"],0)
        self.assertNotIn("not-used",str(x))
        self.assertFalse(x["scored_validation_allowed"])
        self.assertFalse(x["scientific_outcomes_inspected"])

    def test_target_value_changes_do_not_change_report(self):
        a=make([("G1","Ni","28","1","G1_Ni_1","9.1")])
        b=make([("G1","Ni","28","1","G1_Ni_1","SOME-SECRET")])
        self.assertEqual(audit_element_coverage(a,False),audit_element_coverage(b,False))

    def test_row_order_invariance(self):
        rows=[("G1","Ni","28","1","G1_Ni_1","0"),
              ("G2","Xe","54","1","","1")]
        self.assertEqual(audit_element_coverage(make(rows),False),
                         audit_element_coverage(make(list(reversed(rows))),False))

    def test_no_approval_even_without_missing_ids(self):
        a=audit_element_coverage(make([("G1","Ni","28","1","G1_Ni_1","1")]),False)
        self.assertFalse(a["scored_validation_allowed"])
        self.assertFalse(a["claim_of_superiority"])
        self.assertFalse(a["physical_validation_by_bhs"])

    def test_blank_element_rejected(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_PRIMITIVE_GROUP_BLANK"):
            audit_element_coverage(make([("G1","","28","1","","")]),False)


if __name__=="__main__":
    unittest.main()
