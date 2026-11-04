import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import zipfile
from scripts import mcts_ablation_audit_v1 as m


def sample_rows():
    rows=[]
    for scenario in m.SCENARIOS:
        for seed in m.SEEDS:
            for budget in m.BUDGETS:
                for variant in m.VARIANTS:
                    rows.append({'status':'EXPLORATORY_DEVELOPMENT_MCTS_COMPARISON_NO_HOLDOUT',
                        'scenario':scenario,'seed':seed,'budget':budget,'variant':variant,
                        'queries':budget,'best_utility':0.5,'simple_regret':0.1,
                        'wall_seconds':0.01,'selected_ids':[f'candidate_{i:03d}' for i in range(budget)],
                        'task_public_sha256':'a'*64,'scored_validation_allowed':False})
    return rows


def sample_manifest():
    return {'development_seeds':list(m.SEEDS),'variants':list(m.VARIANTS),
        'scenarios':list(m.SCENARIOS),'budgets':list(m.BUDGETS),
        'confirmatory':False,'pilot_informed':True,'synthetic_only':True,
        'scored_validation_allowed':False,'n_rows':450}


class AblationAuditTests(unittest.TestCase):
    def setUp(self):
        self.rows=sample_rows()
        self.manifest=sample_manifest()

    def test_expected_full_grid(self):
        pairs=m.validate_rows(self.manifest,self.rows)
        self.assertEqual(len(pairs),75)
        self.assertEqual(len(m.paired_analysis(pairs)),90)

    def test_contrast_count_and_zero_differences(self):
        report=m.paired_analysis(m.validate_rows(self.manifest,self.rows))
        self.assertEqual(sum(r['n_paired'] for r in report),450)
        self.assertTrue(all(r['mean_difference']==0 for r in report))
        self.assertTrue(all(r['ties']==5 for r in report))

    def test_missing_row_rejected(self):
        with self.assertRaisesRegex(ValueError,'row count'):
            m.validate_rows(self.manifest,self.rows[:-1])

    def test_duplicate_row_rejected(self):
        with self.assertRaisesRegex(ValueError,'row count'):
            m.validate_rows(self.manifest,self.rows+[self.rows[0]])

    def test_mismatched_public_hash_rejected(self):
        self.rows[1]['task_public_sha256']='b'*64
        with self.assertRaisesRegex(ValueError,'mismatched'):
            m.validate_rows(self.manifest,self.rows)

    def test_holdout_seed_rejected(self):
        self.rows[0]['seed']=10000
        with self.assertRaisesRegex(ValueError,'unexpected task'):
            m.validate_rows(self.manifest,self.rows)

    def test_changed_exploratory_flag_rejected(self):
        self.manifest['confirmatory']=True
        with self.assertRaisesRegex(ValueError,'invalid exploratory'):
            m.validate_rows(self.manifest,self.rows)

    def test_wrong_query_budget_rejected(self):
        self.rows[0]['queries']+=1
        with self.assertRaisesRegex(ValueError,'query budget'):
            m.validate_rows(self.manifest,self.rows)

    def test_nonfinite_rejected(self):
        self.rows[0]['best_utility']=float('nan')
        with self.assertRaisesRegex(ValueError,'nonfinite'):
            m.validate_rows(self.manifest,self.rows)

    def test_invalid_selected_ids_rejected(self):
        self.rows[0]['selected_ids']=['candidate_000','candidate_000']
        with self.assertRaisesRegex(ValueError,'invalid selected'):
            m.validate_rows(self.manifest,self.rows)

    def test_reject_unpinned_archive_bytes(self):
        with self.assertRaisesRegex(ValueError,'sha256 mismatch'):
            m.unpack_pinned_archive(b'invalid zip')

    def test_explicit_refuses_modified_original_zip(self):
        data=Path(__file__).read_bytes()
        with self.assertRaisesRegex(ValueError,'sha256 mismatch'):
            m.unpack_pinned_archive(data)

    def test_signed_effect_and_wins(self):
        for row in self.rows:
            if row['scenario']=='smooth' and row['budget']==10 and row['variant']=='mcts_32_h3':
                row['best_utility']=0.8
        report=m.paired_analysis(m.validate_rows(self.manifest,self.rows))
        x=next(r for r in report if r['scenario']=='smooth' and r['budget']==10 and r['contrast']=='PUCT-versus-Bayesian')
        self.assertAlmostEqual(x['mean_difference'],0.3)
        self.assertEqual((x['wins'],x['ties'],x['losses']),(5,0,0))

    def test_status_never_claims_confirmation(self):
        self.assertIn('NOT_CONFIRMATORY',m.STATUS)
        self.assertEqual(len(m.SEEDS),5)
        self.assertTrue(set(m.SEEDS).isdisjoint(range(10000,10100)))


if __name__=='__main__':unittest.main()
