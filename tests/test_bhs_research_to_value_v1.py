import math
import unittest
from scripts.bhs_research_to_value_v1 import (
    BUDGET, MODELS, VARIANTS, task, run_one, run_grid, policy_action,
)


class ResearchToValueTests(unittest.TestCase):
    def test_task_reproducible(self):
        self.assertEqual(task('linear','flat','low',0),task('linear','flat','low',0))

    def test_task_outcomes_differ_with_mechanism(self):
        self.assertNotEqual(task('linear','flat','low',0)[2],task('quadratic','flat','low',0)[2])

    def test_task_must_use_fixed_development_grid(self):
        with self.assertRaises(ValueError):task('linear','flat','low',10000)
        with self.assertRaises(ValueError):task('linear','flat','low',2)
        with self.assertRaises(ValueError):task('other','flat','low',0)

    def test_all_policies_budget_safe(self):
        for v in VARIANTS:
            with self.subTest(v=v):
                r=run_one('quadratic','heterogeneous','low',0,v)
                self.assertLessEqual(r['spent_units'],BUDGET)
                self.assertEqual(len(r['selected_ids']),len(set(r['selected_ids'])))
                self.assertGreater(r['n_observations'],0)

    def test_eig_vs_cost_aware_distinct(self):
        a=run_one('quadratic','heterogeneous','moderate',0,'eig')
        b=run_one('quadratic','heterogeneous','moderate',0,'eig_per_cost')
        self.assertTrue(a['selected_ids'] != b['selected_ids'] or a['spent_units']!=b['spent_units'])

    def test_numeric_ranges(self):
        for variant in VARIANTS:
            r=run_one('oscillatory','flat','moderate',1,variant)
            self.assertTrue(math.isfinite(r['true_model_log_loss']))
            self.assertGreaterEqual(r['true_model_log_loss'],0)
            self.assertTrue(0<=r['true_model_probability']<=1)

    def test_grid_counts(self):
        r=run_grid()
        self.assertEqual(r['manifest']['fixed_development_cases'],24)
        self.assertEqual(r['manifest']['n_rows'],96)
        self.assertEqual(r['manifest']['n_paired_comparisons'],72)
        self.assertEqual(len(r['summary']),4)

    def test_common_outcome_per_candidate(self):
        p,plan,out=task('linear','flat','low',1)
        self.assertEqual(out,task('linear','flat','low',1)[2])
        self.assertEqual(len(out),len(p))

    def test_flags_fail_closed(self):
        r=run_grid()
        self.assertFalse(r['manifest']['scored_validation_allowed'])
        self.assertFalse(r['manifest']['independent_holdout_used'])
        self.assertFalse(r['manifest']['claim_of_superiority'])
        self.assertTrue(all(not row['scored_validation_allowed'] for row in r['rows']))

    def test_cannot_select_unsupported_policy(self):
        with self.assertRaises(ValueError):run_one('linear','flat','low',0,'unregistered')

    def test_reproducible_campaign(self):
        a=run_one('linear','flat','low',0,'random')
        b=run_one('linear','flat','low',0,'random')
        self.assertEqual(a,b)

    def test_affordability_constraint_rejects_empty(self):
        with self.assertRaises(ValueError):
            policy_action('random',{'a':(1.,)}, {'a':{'cost':1}},[],[],key=1)

    def test_no_hidden_labels_in_public(self):
        public,plan,_=task('linear','flat','low',0)
        self.assertEqual(set(public),set(plan))
        self.assertTrue(all(isinstance(v,tuple) and len(v)==1 for v in public.values()))

    def test_paired_groups_unique(self):
        r=run_grid()
        keys={(x['true_model'],x['cost_profile'],x['noise_profile'],x['development_repeat'],x['variant']) for x in r['rows']}
        self.assertEqual(len(keys),96)

    def test_all_model_families_present(self):
        r=run_grid()
        self.assertEqual({x['true_model'] for x in r['rows']},set(MODELS))


if __name__=='__main__':unittest.main()
