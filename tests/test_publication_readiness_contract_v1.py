import json
import unittest
from copy import deepcopy
from pathlib import Path
from scripts.publication_readiness_contract_v1 import validate_claim_register

DATA=json.loads(Path('research/PUBLICATION_CLAIMS_REGISTER_V1.json').read_text(encoding='utf-8'))

class PublicationReadinessContractTests(unittest.TestCase):
    def test_baseline_register(self):
        result=validate_claim_register(DATA)
        self.assertEqual(result['claim_count'],6)
        self.assertEqual(result['unsupported_claims'],4)
    def test_holdout_gate(self):
        x=deepcopy(DATA);x['independent_holdout_used']=True
        with self.assertRaises(ValueError):validate_claim_register(x)
    def test_scoring_gate(self):
        x=deepcopy(DATA);x['scored_validation_allowed']=True
        with self.assertRaises(ValueError):validate_claim_register(x)
    def test_superiority_gate(self):
        x=deepcopy(DATA);x['superiority_claim_validated']=True
        with self.assertRaises(ValueError):validate_claim_register(x)
    def test_reject_unsupported_claim_upgrade(self):
        x=deepcopy(DATA);x['claims'][1]['classification']='supported'
        with self.assertRaises(ValueError):validate_claim_register(x)
    def test_reject_count_mismatch(self):
        x=deepcopy(DATA);x['evidence']['campaign_rows']=100
        with self.assertRaises(ValueError):validate_claim_register(x)
    def test_reject_duplicate_claim(self):
        x=deepcopy(DATA);x['claims'][2]['id']=x['claims'][1]['id']
        with self.assertRaises(ValueError):validate_claim_register(x)
    def test_no_holdout_runtime_reference(self):
        source=Path('scripts/publication_readiness_contract_v1.py').read_text(encoding='utf-8')
        self.assertNotIn('make_task(',source)
        self.assertNotIn('run_grid(',source)
    def test_report_marks_no_independent_verification(self):
        report=Path('research/PUBLICATION_READINESS_AUDIT_V1.md').read_text(encoding='utf-8')
        self.assertIn('Not publication-ready',report)
        self.assertIn('10000..10099',report)

if __name__=='__main__':unittest.main()
