import copy
import json
import unittest
from pathlib import Path
from scripts.real_world_feasibility_v1 import validate_registry, REQUIRED_IDS

class RealWorldFeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads(Path('research/REAL_WORLD_DATASET_CANDIDATES_V1.json').read_text())
    def test_reference_registry(self):
        self.assertEqual(validate_registry(self.registry)['dataset_candidates'],4)
    def test_pilot_is_nist(self):
        self.assertEqual(validate_registry(self.registry)['first_pilot_candidate'],'nist_fe_co_ni')
    def test_full_dataset_inventory(self):
        self.assertEqual(tuple(x['id'] for x in self.registry['datasets']),REQUIRED_IDS)
    def test_no_holdout(self):
        self.assertFalse(validate_registry(self.registry)['independent_holdout_used'])
    def test_no_materials_claim(self):
        self.assertFalse(validate_registry(self.registry)['physical_validation'])
    def test_no_scored_validation(self):
        self.assertFalse(validate_registry(self.registry)['scored_validation_allowed'])
    def test_reject_claimed_download(self):
        x=copy.deepcopy(self.registry);x['datasets'][0]['data_downloaded']=True
        with self.assertRaises(ValueError):validate_registry(x)
    def test_reject_claimed_compatibility(self):
        x=copy.deepcopy(self.registry);x['datasets'][0]['compatible_with_current_bhs']=True
        with self.assertRaises(ValueError):validate_registry(x)
    def test_reject_claimed_license(self):
        x=copy.deepcopy(self.registry);x['datasets'][0]['data_license_cleared_for_redistribution']=True
        with self.assertRaises(ValueError):validate_registry(x)
    def test_reject_incomplete_gates(self):
        x=copy.deepcopy(self.registry);x['pilot_prerequisites'].pop()
        with self.assertRaises(ValueError):validate_registry(x)
    def test_reject_duplicate_dataset(self):
        x=copy.deepcopy(self.registry);x['datasets'][1]['id']=x['datasets'][0]['id']
        with self.assertRaises(ValueError):validate_registry(x)
    def test_reject_unsupported_status(self):
        x=copy.deepcopy(self.registry);x['status']='VALIDATED'
        with self.assertRaises(ValueError):validate_registry(x)
    def test_reject_bad_url(self):
        x=copy.deepcopy(self.registry);x['datasets'][1]['url']='http://example.com'
        with self.assertRaises(ValueError):validate_registry(x)
    def test_no_execution_imports(self):
        s=Path('scripts/real_world_feasibility_v1.py').read_text()
        self.assertNotIn('make_task(',s)
        self.assertNotIn('run_grid(',s)
        self.assertNotIn('requests.',s)
        self.assertNotIn('urlopen(',s)

if __name__=='__main__':unittest.main()
