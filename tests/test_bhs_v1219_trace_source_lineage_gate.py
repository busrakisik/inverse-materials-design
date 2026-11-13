"""V12.19 synthetic-only trace archival identity and anti-leakage tests."""
import hashlib
import io
import json
from pathlib import Path
import zipfile
import unittest

from scripts import bhs_v1219_trace_source_lineage_gate as a


def row(group, replicate, *, timestamp="2020-01-15T10:30:00+00:00"):
    return {
        "experiment_id": f"MANUFACTURED-{group}-{replicate}",
        "design_group_id": f"GROUP-{group}",
        "n": (group % 100) + 1,
        "theta_deg": group // 100 + 20,
        "r_mm": 2.5,
        "t_mm": 0.7,
        "curve_file": f"fake-{group}-{replicate}.csv",
        "acquisition_timestamp": timestamp,
    }


def fixture(groups=2, *, payload=None):
    rows = [row(g, r) for g in range(groups) for r in range(3)]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for r in rows:
            z.writestr(r["curve_file"],
                       b"fabricated-force, fabricated-displacement\n"
                       if payload is None else payload)
    raw = buf.getvalue()
    manifest = {
        "source_dataset_id": a.ORIGINAL_ID,
        "experiment_rows": rows,
        "declared_archive_sha256": hashlib.sha256(raw).hexdigest(),
    }
    return manifest, raw


class TraceSourceTests(unittest.TestCase):
    def test_source_catalog_is_no_go(self):
        report = a.audit_catalog()
        self.assertEqual(report["source_entry_count"], 4)
        self.assertEqual(report["status"], "NO_GO_ORIGINAL_2020_TRACE_MAPPING_UNVERIFIED")
        self.assertFalse(report["scored_validation_allowed"])
        self.assertFalse(report["original_2020_per_replicate_curve_matching_proven"])
        self.assertFalse(report["raw_2020_trace_bytes_verified"])
        self.assertFalse(report["source_measurements_read"])

    def test_catalog_has_exact_distinct_study_ids(self):
        r = a.audit_catalog()
        self.assertEqual(set(r["source_ids"]), a.EXPECTED_IDS)
        self.assertTrue(r["separate_2021_2022_2024_sources_not_conflated"])

    def test_catalog_cannot_claim_raw_source_verified(self):
        cat=json.loads(a.CATALOG.read_text())
        cat["entries"][0]["raw_archive_bytes_downloaded"]=True
        with self.assertRaisesRegex(a.SourceTraceError,"ORIGINAL_SOURCE_PROVENANCE_ASSERTION_UNSUPPORTED"):
            a.audit_catalog(json.dumps(cat).encode())

    def test_catalog_any_other_source_cannot_be_scored(self):
        cat=json.loads(a.CATALOG.read_text())
        cat["entries"][2]["score_use_authorized"]=True
        with self.assertRaisesRegex(a.SourceTraceError,"OTHER_SOURCE_AUTOMATICALLY_APPROVED"):
            a.audit_catalog(json.dumps(cat).encode())

    def test_consistent_fabricated_three_replicate_group_shape(self):
        manifest, archive=fixture()
        r=a.audit_trial_archive(manifest, archive, original_grid_scope=False)
        self.assertEqual(r["trial_count"],6)
        self.assertEqual(r["distinct_design_group_count"],2)
        self.assertEqual(r["curve_file_count"],6)
        self.assertTrue(r["matches_manifest_declared_digest"])
        self.assertFalse(r["real_2020_physical_curve_dataset_authenticated"])
        self.assertFalse(r["archive_digest_independently_authenticated"])
        self.assertFalse(r["physical_curve_content_read"])
        self.assertFalse(r["scored_validation_allowed"])

    def test_historical_original_requires_1800_rows(self):
        manifest, archive=fixture()
        with self.assertRaisesRegex(a.SourceTraceError,"ORIGINAL_V11_GRID_REPLICATE_COUNT_MISMATCH"):
            a.audit_trial_archive(manifest, archive)

    def test_full_manufactured_600x3_schema_not_physical_proof(self):
        manifest, archive=fixture(groups=600)
        r=a.audit_trial_archive(manifest, archive)
        self.assertEqual((r["trial_count"],r["distinct_design_group_count"]),(1800,600))
        self.assertFalse(r["raw_2020_replicate_join_verified"])
        self.assertFalse(r["archive_digest_independently_authenticated"])
        self.assertFalse(r["physical_mechanism_hypotheses_validated"])

    def test_cross_study_archive_mapping_forbidden(self):
        m, archive=fixture()
        m["source_dataset_id"]="ADTS_2024_SEPARATE"
        with self.assertRaisesRegex(a.SourceTraceError,"CROSS_STUDY_DATASET_JOIN_BLOCKED"):
            a.audit_trial_archive(m, archive, original_grid_scope=False)

    def test_missing_curve_member_fails(self):
        m, raw=fixture()
        m["experiment_rows"][0]["curve_file"]="absent.csv"
        with self.assertRaisesRegex(a.SourceTraceError,"ARCHIVE_MEMBER_AND_EXPERIMENT_MAPPING_DIFFER"):
            a.audit_trial_archive(m, raw, original_grid_scope=False)

    def test_duplicate_experiment_id_fails(self):
        m, raw=fixture()
        m["experiment_rows"][1]["experiment_id"]=m["experiment_rows"][0]["experiment_id"]
        with self.assertRaisesRegex(a.SourceTraceError,"DUPLICATE_TRIAL_ID_OR_CURVE_MAPPING"):
            a.audit_trial_archive(m, raw, original_grid_scope=False)

    def test_duplicate_file_mapping_fails(self):
        m, raw=fixture()
        m["experiment_rows"][1]["curve_file"]=m["experiment_rows"][0]["curve_file"]
        with self.assertRaisesRegex(a.SourceTraceError,"DUPLICATE_TRIAL_ID_OR_CURVE_MAPPING"):
            a.audit_trial_archive(m, raw, original_grid_scope=False)

    def test_inconsistent_design_for_same_group_fails(self):
        m, raw=fixture()
        m["experiment_rows"][1]["theta_deg"]=60
        with self.assertRaisesRegex(a.SourceTraceError,"GROUP_HAS_INCONSISTENT_PUBLIC_DESIGN"):
            a.audit_trial_archive(m, raw, original_grid_scope=False)

    def test_group_not_triple_is_rejected(self):
        m, raw=fixture()
        m["experiment_rows"][1]["design_group_id"]="SPOOF-GROUP"
        with self.assertRaisesRegex(a.SourceTraceError,"REPLICATES_NOT_TRIPLETS"):
            a.audit_trial_archive(m, raw, original_grid_scope=False)

    def test_missing_timezone_is_rejected(self):
        m, raw=fixture()
        m["experiment_rows"][0]["acquisition_timestamp"]="2020-01-15T10:30:00"
        with self.assertRaisesRegex(a.SourceTraceError,"TIMEZONE_MISSING"):
            a.audit_trial_archive(m, raw, original_grid_scope=False)

    def test_measured_outcome_cannot_appear_in_design_manifest(self):
        m, raw=fixture()
        m["experiment_rows"][0]["toughness_j"]=30
        with self.assertRaisesRegex(a.SourceTraceError,"ROW_FIELDS_MISSING_OR_LEAKED"):
            a.audit_trial_archive(m, raw, original_grid_scope=False)

    def test_duplicate_zip_member_name_fails(self):
        m, raw=fixture()
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,"w") as z:
            z.writestr("same.csv",b"A")
            z.writestr("same.csv",b"B")
        with self.assertRaisesRegex(a.SourceTraceError,"DUPLICATED_ZIP_MEMBER_NAMES"):
            a.audit_trial_archive(m,buf.getvalue(),original_grid_scope=False)

    def test_directory_traversal_member_blocked(self):
        m,raw=fixture()
        b=io.BytesIO()
        with zipfile.ZipFile(b,"w") as z:
            z.writestr("../out.csv",b"fake")
        with self.assertRaisesRegex(a.SourceTraceError,"INVALID_ARCHIVE_MEMBER_PATH"):
            a.audit_trial_archive(m,b.getvalue(),original_grid_scope=False)

    def test_local_zip_digest_change_detected(self):
        m,raw=fixture()
        alt=fixture(payload=b"DIFFERENT SYNTHETIC BYTES")[1]
        with self.assertRaisesRegex(a.SourceTraceError,"DECLARED_ARCHIVE_DIGEST_MISMATCH"):
            a.audit_trial_archive(m,alt,original_grid_scope=False)

    def test_archive_body_not_parsed_as_curve(self):
        m,raw=fixture(payload=b"SECRET-FAKE-PHYSICAL-VALUES-DO-NOT-READ")
        r=a.audit_trial_archive(m,raw,original_grid_scope=False)
        serialized=json.dumps(r)
        self.assertFalse(r["numeric_force_displacement_values_parsed"])
        self.assertNotIn("SECRET-FAKE",serialized)
        self.assertFalse(r["original_creator_experiment_id_mapping_authenticated"])

    def test_original_curve_provenance_cannot_be_self_certified(self):
        m,raw=fixture()
        m["externally_verified"]=True
        with self.assertRaisesRegex(a.SourceTraceError,"MANIFEST_SCHEMA_INVALID"):
            a.audit_trial_archive(m,raw,original_grid_scope=False)

    def test_unverified_external_digest_rejected(self):
        m,raw=fixture()
        m["declared_archive_sha256"]=""
        with self.assertRaisesRegex(a.SourceTraceError,"NO_VALID_DECLARED_ARCHIVE_DIGEST"):
            a.audit_trial_archive(m,raw,original_grid_scope=False)

    def test_invalid_premeasurement_features_fail(self):
        for fix in ({"n":8.5},{"n":False},{"theta_deg":181},
                    {"t_mm":4},{"r_mm":float("nan")}):
            with self.subTest(fix=fix):
                m,raw=fixture()
                m["experiment_rows"][0].update(fix)
                with self.assertRaises(a.SourceTraceError):
                    a.audit_trial_archive(m,raw,original_grid_scope=False)

    def test_no_real_data_download_or_unzipping(self):
        import ast
        source=Path(a.__file__).read_text()
        tree=ast.parse(source)
        imports=[n.module or "" for n in ast.walk(tree)
                 if isinstance(n,ast.ImportFrom)]
        imports += [alias.name for n in ast.walk(tree)
                    if isinstance(n,ast.Import) for alias in n.names]
        self.assertFalse(any(i.startswith(("requests","urllib","socket","subprocess"))
                             for i in imports))
        self.assertNotIn("z.read(",source)
        self.assertNotIn("extractall(",source)
        self.assertNotIn("read_csv(",source)

    def test_repeated_source_catalog_report_deterministic(self):
        self.assertEqual(a.audit_catalog(),a.audit_catalog())


if __name__=="__main__":
    unittest.main()
