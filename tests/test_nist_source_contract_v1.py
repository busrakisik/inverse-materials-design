import copy
import json
import unittest
from pathlib import Path
from scripts.nist_source_contract_v1 import FAIL_CLOSED, FIELD_UNITS, validate

DATA=json.loads(Path('research/NIST_FE_CO_NI_SOURCE_CONTRACT_V1.json').read_text())

class NistSourceContractTests(unittest.TestCase):
    def test_valid_source(self):
        self.assertEqual(validate(DATA)['documented_fields'],5)
    def test_no_dataset_ready_claim(self):
        self.assertFalse(validate(DATA)['dataset_ready_for_bhs'])
    def test_no_holdout(self):
        self.assertFalse(validate(DATA)['independent_holdout_used'])
    def test_no_physical_claim(self):
        self.assertFalse(validate(DATA)['physical_validation'])
    def test_no_scored_validation(self):
        self.assertFalse(validate(DATA)['scored_validation_allowed'])
    def test_field_units(self):
        self.assertEqual(DATA['fields']['Coer']['unit'],'mT')
        self.assertEqual(DATA['fields']['Kerr']['unit'],'mrad')
    def test_exact_five_fields(self):
        self.assertEqual(set(DATA['fields']),set(FIELD_UNITS))
    def test_reject_missing_field(self):
        x=copy.deepcopy(DATA);del x['fields']['Kerr']
        with self.assertRaises(ValueError):validate(x)
    def test_reject_invented_units(self):
        x=copy.deepcopy(DATA);x['fields']['Coer']['unit']='Tesla'
        with self.assertRaises(ValueError):validate(x)
    def test_reject_unknown_source(self):
        x=copy.deepcopy(DATA);x['source_repository']='other/repo'
        with self.assertRaises(ValueError):validate(x)
    def test_reject_wrong_blob(self):
        x=copy.deepcopy(DATA);x['source_git_blob_sha']='abc'
        with self.assertRaises(ValueError):validate(x)
    def test_reject_wrong_size(self):
        x=copy.deepcopy(DATA);x['source_file_size_bytes']=0
        with self.assertRaises(ValueError):validate(x)
    def test_reject_claim_upgrades(self):
        for key in FAIL_CLOSED:
            with self.subTest(key=key):
                x=copy.deepcopy(DATA);x[key]=True
                with self.assertRaises(ValueError):validate(x)
    def test_deterministic(self):
        self.assertEqual(validate(DATA),validate(copy.deepcopy(DATA)))

if __name__=='__main__':unittest.main()
