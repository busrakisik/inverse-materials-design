"""V12.15 adversarial contract tests on fully artificial identifiers/strings."""
import csv
import gzip
import io
import json
import unittest
from scripts import bhs_v1215_precompute_feature_provenance as a
from scripts.bhs_v1214_group_split_readiness import SplitContractError


FIELDS = (
    "GB", "element", "Z", "site", "GB_site", "GB_element_site", "job_name",
    "E_seg", "structure_unrel", "dist_GB_unrel", "site_z_unrel",
    "VorNN_CoordNo_unrel", "E_seg_unrel", "magmoms_unrel",
    "pure_min_wsep_rigid", "other_column",
)


def row(gb="G1", element="Ni", z="28", site="1", target="SECRET-LABEL",
        geom="SECRET-GEOMETRY", vornn="SECRET-VORONOI"):
    return {
        "GB": gb, "element": element, "Z": z, "site": site,
        "GB_site": gb + "-" + site, "GB_element_site": gb + "-" + element + "-" + site,
        "job_name": "run-" + gb + "-" + element + "-" + site,
        "E_seg": target, "structure_unrel": geom,
        "dist_GB_unrel": "0.01", "site_z_unrel": "0.02",
        "VorNN_CoordNo_unrel": vornn, "E_seg_unrel": "SECRET-ENERGY",
        "magmoms_unrel": "SECRET-MOMENT", "pure_min_wsep_rigid": "SECRET-REFERENCE",
        "other_column": "UNKNOWN",
    }


def source(records, fields=FIELDS):
    out = io.StringIO(newline="")
    w = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(records)
    return gzip.compress(out.getvalue().encode(), mtime=0)


def set_rows():
    return [row("G1", "Ni", "28", "1"),
            row("G1", "Fe", "26", "2", target="", geom=""),
            row("G2", "Ni", "28", "1", vornn=""),
            row("G2", "Fe", "26", "2")]


class FeatureProvenanceTests(unittest.TestCase):
    def report(self, records=None, fields=FIELDS):
        return a.source_feature_availability(source(
            set_rows() if records is None else records, fields), require_original=False)

    def test_denies_all_candidates_even_when_present(self):
        result = self.report()
        self.assertEqual(result["geometry_candidate_column_count"], 4)
        self.assertEqual(result["candidate_voronoi_column_count"], 1)
        self.assertFalse(result["scored_validation_allowed"])
        self.assertFalse(result["precalculation_geometry_certified"])
        self.assertEqual(result["approved_numerical_geometry_predictor_columns"], [])
        self.assertFalse(result["full_4289_row_starting_structure_lineage_verified"])
        self.assertTrue(all(not x["predecision_feature_approved"] for x in
                            result["candidate_column_coverage"].values()))

    def test_source_exposes_blankness_only(self):
        r=self.report()
        self.assertEqual(r["candidate_column_coverage"]["structure_unrel"]["blank_rows"], 1)
        self.assertEqual(r["candidate_column_coverage"]["structure_unrel"]["populated_rows"], 3)
        self.assertEqual(r["candidate_column_coverage"]["VorNN_CoordNo_unrel"]["blank_rows"], 1)
        self.assertEqual(r["target_blank_strings"],1)
        self.assertEqual(r["candidate_column_coverage"]["structure_unrel"]
                         ["paired_target_string_missingness"]["target_blank_and_feature_blank"],1)

    def test_forbidden_outputs_stay_forbidden(self):
        self.assertEqual(a.classify("E_seg_unrel"),"COMPUTED_OR_POSTRUN_DENY")
        self.assertEqual(a.classify("structure"),"COMPUTED_OR_POSTRUN_DENY")
        self.assertEqual(a.classify("magmoms_unrel"),"COMPUTED_OR_POSTRUN_DENY")
        self.assertEqual(a.classify("convergence"),"COMPUTED_OR_POSTRUN_DENY")
        self.assertEqual(a.classify("Wsep_RGS_min"),"COMPUTED_OR_POSTRUN_DENY")
        self.assertEqual(a.classify("DDEC6_ANSBO_min"),"COMPUTED_OR_POSTRUN_DENY")
        self.assertEqual(a.classify("VorNN_CoordNo"),"COMPUTED_OR_UNCERTAIN_DENY")
        self.assertEqual(a.classify("something_unrel"),"COMPUTED_OR_UNCERTAIN_DENY")
        self.assertEqual(a.classify("other_column"),"UNKNOWN_PROVENANCE_DENY")

    def test_identity_never_confused_with_physics(self):
        self.assertEqual(a.classify("element"),"SELECTION_KNOWN_IDENTITY")
        self.assertEqual(a.classify("GB"),"SELECTION_KNOWN_IDENTITY")
        self.assertEqual(a.classify("site"),"IDENTIFIER_ONLY_NO_PREDICTION")
        self.assertEqual(a.classify("GB_site"),"IDENTIFIER_ONLY_NO_PREDICTION")
        self.assertEqual(a.classify("structure_unrel"),
                         "CANDIDATE_UNREL_GEOMETRY_NOT_CERTIFIED")

    def test_report_never_contains_source_values(self):
        dumped=json.dumps(self.report())
        for secret in ("SECRET-LABEL", "SECRET-GEOMETRY", "SECRET-VORONOI",
                       "SECRET-ENERGY", "SECRET-MOMENT", "SECRET-REFERENCE"):
            self.assertNotIn(secret,dumped)

    def test_numerical_or_text_value_substitution_invariant(self):
        before=set_rows()
        after=[dict(x) for x in before]
        for x in after:
            if x["E_seg"]: x["E_seg"]="NEW-TARGET-UNREAD"
            if x["structure_unrel"]: x["structure_unrel"]="CHANGED-UNREAD-STRUCTURE"
            if x["dist_GB_unrel"]: x["dist_GB_unrel"]="CHANGED-UNREAD-DISTANCE"
            if x["VorNN_CoordNo_unrel"]: x["VorNN_CoordNo_unrel"]="NEW-UNREAD-VORONOI"
        self.assertEqual(self.report(before),self.report(after))

    def test_row_order_invariance(self):
        self.assertEqual(self.report(set_rows()), self.report(list(reversed(set_rows()))))

    def test_optional_candidate_not_present_not_imputed(self):
        fields=tuple(x for x in FIELDS if x!="structure_unrel")
        r=self.report(fields=fields)
        self.assertFalse(r["claimed_core_candidate_header_presence"]["structure_unrel"])
        self.assertNotIn("structure_unrel",r["candidate_column_coverage"])
        self.assertFalse(r["scored_validation_allowed"])

    def test_missing_combined_name_not_imputed(self):
        rows=set_rows()
        rows[0]["GB_element_site"]=""
        r=self.report(rows)
        self.assertEqual(r["original_combined_identifier_blanks"],1)

    def test_duplicate_source_key_fails(self):
        rows=set_rows()
        rows.append(dict(rows[0]))
        with self.assertRaisesRegex(SplitContractError,"DUPLICATE_PRIMITIVE_KEY"):
            self.report(rows)

    def test_inconsistent_atomic_number_fails(self):
        rows=set_rows()
        rows[2]["Z"]="29"
        with self.assertRaisesRegex(SplitContractError,"ATOMIC_NUMBER_CONFLICT"):
            self.report(rows)

    def test_missing_mandatory_header_fails(self):
        fields=tuple(x for x in FIELDS if x!="E_seg")
        with self.assertRaisesRegex(SplitContractError,"INVALID_HEADERS"):
            self.report(fields=fields)

    def test_unpinned_original_source_gate_fails(self):
        with self.assertRaises(ValueError):
            a.source_feature_availability(source(set_rows()),require_original=True)

    def test_source_set_contains_author_sample_only_not_full_lineage(self):
        r=self.report()
        self.assertTrue(r["sample_poscar_available_in_upstream_repo"])
        self.assertEqual(len(r["sample_poscar_git_blob"]),40)
        self.assertFalse(r["full_4289_row_starting_structure_lineage_verified"])


if __name__=="__main__":
    unittest.main()
