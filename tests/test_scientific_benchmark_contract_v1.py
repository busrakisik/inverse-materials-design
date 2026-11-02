import unittest
from scripts.scientific_benchmark_contract_v1 import (STATUS,make_task,MeteredEvaluator,UniformWithoutReplacement,DescriptorGreedy)

class BenchmarkContracts(unittest.TestCase):
    def test_scenarios(self):
        for s in ('smooth','multimodal','uninformative','mismatched','duplicates'):
            self.assertEqual(len(make_task(s,42).public_view()),20)
    def test_reproducible(self):
        self.assertEqual(make_task('smooth',42).fingerprint(),make_task('smooth',42).fingerprint())
    def test_random_unique_budget(self):
        x=MeteredEvaluator(make_task('smooth',10),10).run(UniformWithoutReplacement(5))
        self.assertEqual(len({v['candidate_id'] for v in x['trace']}),10)
    def test_random_reproducible(self):
        t=make_task('smooth',10)
        self.assertEqual(MeteredEvaluator(t,10).run(UniformWithoutReplacement(5)),MeteredEvaluator(t,10).run(UniformWithoutReplacement(5)))
    def test_greedy_unique(self):
        r=MeteredEvaluator(make_task('duplicates',1),10).run(DescriptorGreedy())
        self.assertEqual(len(set(x['candidate_id'] for x in r['trace'])),10)
    def test_budget_limit(self):
        for b in (0,-1,True,21):
            with self.subTest(b=b),self.assertRaises(ValueError):MeteredEvaluator(make_task('smooth',1),b)
    def test_repeated_rejected(self):
        class Bad:
            def choose(self,p,o):return 'candidate_000'
        with self.assertRaises(ValueError):MeteredEvaluator(make_task('smooth',1),2).run(Bad())
    def test_unknown_rejected(self):
        class Bad:
            def choose(self,p,o):return 'unknown'
        with self.assertRaises(ValueError):MeteredEvaluator(make_task('smooth',1),1).run(Bad())
    def test_task_invalid(self):
        with self.assertRaises(ValueError):make_task('bad',1)
    def test_status_not_scored(self):
        r=MeteredEvaluator(make_task('smooth',1),1).run(DescriptorGreedy())
        self.assertEqual(r['status'],STATUS);self.assertFalse(r['scored_benchmark']);self.assertFalse(r['real_labels_used'])
    def test_policy_sees_no_full_label_mapping(self):
        class Spy:
            def choose(self,p,o):
                self_values=repr(p)+repr(o)
                self_inner='candidate_000'
                self.self_test.assertNotIn('_labels',self_values)
                return self_inner
        sp=Spy();sp.self_test=self
        MeteredEvaluator(make_task('smooth',1),1).run(sp)
    def test_invalid_n_seed(self):
        for params in ({'seed':True},{'seed':1,'n':9}):
            with self.assertRaises(ValueError):make_task('smooth',**params)

if __name__=='__main__':unittest.main()
