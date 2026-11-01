"""Synthetic metadata-contract tests; no downloaded data and no empirical results."""
import copy
import unittest
from bhs.benchmarks.dataset_gate import DatasetGateError, STATUS, validate_manifest

H = "a" * 64
B = "b" * 64
C = "c" * 64
D = "d" * 64
E = "e" * 64

def valid():
    return {"schema_version":"bhs-dataset-gate-v1","dataset":{
        "name":"matbench_expt_gap","version":"matbench_v0.1",
        "source_url":"https://example.org/verified-source","source_record_id":"source-001",
        "license_identifier":"RESEARCH_CHECK_REQUIRED","license_source_url":"https://example.org/licensing","citation":"example citation; NOT genuine dataset metadata",
        "raw_sha256":H,"expected_row_count":4604,"feature_column":"composition", "label_column":"gap expt", "label_unit":"eV"},
        "split":{"strategy":"composition_group_disjoint","train_ids_sha256":B,"validation_ids_sha256":C,"test_ids_sha256":D,"group_definition_sha256":E,"overlap_audit":"PASS_VERIFIED_BY_SPLIT_BUILDER","test_labels_locked":True},
        "trial":{"objective_type":"target_band_gap_distance","target_band_gap_ev":2.0,"target_rationale":"Synthetic contract example only; not adopted scientific target","query_budget":20,"seeds":[1,2,3],"hidden_label_access":"QUERY_ONLY","selection_without_replacement":True,"baseline_policy_status":"NOT_EVALUATED"},
        "real_data_ingested":False,"benchmark_executed":False}

class DatasetGateTests(unittest.TestCase):
    def test_valid_declarations_are_not_claimed_as_verified(self):
        self.assertEqual(validate_manifest(valid())["status"], STATUS)
    def test_missing_source_rejected(self):
        m=valid();del m["dataset"]["source_url"];self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_missing_license_rejected(self):
        m=valid();m["dataset"]["license_identifier"]="";self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_malformed_hash_rejected(self):
        m=valid();m["dataset"]["raw_sha256"]="hash";self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_wrong_unit_rejected(self):
        m=valid();m["dataset"]["label_unit"]="J";self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_missing_split_audit_rejected(self):
        m=valid();m["split"]["overlap_audit"]="NOT_RUN";self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_unlocked_labels_rejected(self):
        m=valid();m["split"]["test_labels_locked"]=False;self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_unapproved_objective_rejected(self):
        m=valid();m["trial"]["objective_type"]="max_energy";self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_missing_target_rationale_rejected(self):
        m=valid();m["trial"]["target_rationale"]="";self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_invalid_budget_rejected(self):
        m=valid();m["trial"]["query_budget"]=0;self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_hidden_labels_rejected(self):
        m=valid();m["trial"]["hidden_label_access"]="FULL_TABLE";self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_fabricated_result_rejected(self):
        m=valid();m["benchmark_executed"]=True;self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_duplicate_seeds_rejected(self):
        m=valid();m["trial"]["seeds"]=[1,1,2];self.assertRaises(DatasetGateError,validate_manifest,m)
    def test_nan_target_rejected(self):
        m=valid();m["trial"]["target_band_gap_ev"]=float("nan");self.assertRaises(DatasetGateError,validate_manifest,m)

if __name__ == '__main__':unittest.main()
