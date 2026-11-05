import copy
import io
import math
import unittest
from unittest.mock import patch

import numpy as np
from scipy.io import savemat
from scripts import nist_dataset_inspection_v1 as ins


def fixture():
    return {"C": np.array([[.2,.3,.5],[.4,.1,.5],[np.nan,.5,.5],[.3,.3,.4]]),
            "XRD": np.ones((4, 4)), "TTH": np.arange(4).reshape(1,4),
            "Coer": np.array([[1.],[np.nan],[3.],[4.]]),
            "Kerr": np.array([[.1],[.2],[.3],[.4]])}


class NistInspectionTests(unittest.TestCase):
    def test_expected_fields(self): self.assertEqual(len(ins.FIELDS),5)
    def test_source_commit_pinned(self): self.assertEqual(len(ins.SOURCE_COMMIT),40)
    def test_source_blob_pinned(self): self.assertEqual(len(ins.SOURCE_GIT_BLOB),40)
    def test_blob_hash_reference(self):
        raw=b"hello"
        self.assertEqual(ins.git_blob_sha1(raw),"b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")
    def test_reject_size(self):
        with self.assertRaises(ValueError): ins.validate_source(b"untrusted")
    def test_reject_wrong_blob_even_matching_size(self):
        with self.assertRaises(ValueError): ins.validate_source(b"0"*ins.SOURCE_SIZE)
    def test_sample_count(self): self.assertEqual(ins.inspect_arrays(fixture())["composition"]["inferred_sample_count"],4)
    def test_nan_count(self): self.assertEqual(ins.inspect_arrays(fixture())["fields"]["Coer"]["nan"],1)
    def test_composition_complete(self): self.assertEqual(ins.inspect_arrays(fixture())["composition"]["complete_rows"],3)
    def test_composition_sums(self): self.assertEqual(ins.inspect_arrays(fixture())["composition"]["sum_near_one_rows"],3)
    def test_transposed_composition(self):
        d=fixture();d["C"]=d["C"].T
        self.assertEqual(ins.inspect_arrays(d)["composition"]["orientation"],"three_rows_by_samples")
    def test_unresolved_composition(self):
        d=fixture();d["C"]=np.ones((4,5))
        self.assertIsNone(ins.inspect_arrays(d)["composition"]["inferred_sample_count"])
    def test_missing_field_rejected(self):
        d=fixture();d.pop("XRD")
        with self.assertRaises(ValueError): ins.inspect_arrays(d)
    def test_extra_field_rejected(self):
        d=fixture();d["new"] = np.ones((2,))
        with self.assertRaises(ValueError): ins.inspect_arrays(d)
    def test_nonarray_rejected(self):
        d=fixture();d["Kerr"]=0
        with self.assertRaises(ValueError): ins.inspect_arrays(d)
    def test_no_claim_upgrades(self):
        r=ins.inspect_arrays(fixture())
        for k in ("scored_validation_allowed", "dataset_ready_for_bhs",
                  "real_data_experiment_executed", "claim_of_superiority",
                  "physical_validation", "independent_holdout_used"):
            self.assertIs(r[k],False)
    def test_unknown_noise_and_cost(self):
        r=ins.inspect_arrays(fixture())
        self.assertIs(r["measured_experiment_costs_verified"],False)
        self.assertFalse(r["targets"]["Coer"]["measurement_error_per_row_documented"])
    def test_fixture_mat_parse(self):
        stream=io.BytesIO();savemat(stream,fixture())
        self.assertEqual(set(ins.loadmat(io.BytesIO(stream.getvalue())))-{
            "__header__","__version__","__globals__"},set(ins.FIELDS))
    def test_nan_and_inf_are_counted(self):
        d=fixture();d["Coer"][0,0]=float("inf")
        r=ins.inspect_arrays(d)
        self.assertEqual(r["fields"]["Coer"]["nan"],1)
        self.assertEqual(r["fields"]["Coer"]["posinf"],1)
    def test_refuses_complex(self):
        d=fixture();d["XRD"]=np.array([1+2j])
        self.assertFalse(ins.inspect_arrays(d)["fields"]["XRD"]["numeric"])

if __name__ == "__main__": unittest.main()
