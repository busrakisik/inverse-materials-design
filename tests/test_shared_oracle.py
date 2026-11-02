import unittest
from dataclasses import FrozenInstanceError
from scripts.shared_oracle import ControlledOracle,run_synthetic_trial,STATUS

class OracleContractTests(unittest.TestCase):
    def setUp(self):
        self.labels = {'b':1.5,'a':2.0,'c':0.2,'d':3.4}
    def test_only_queried_label_exposed(self):
        o=ControlledOracle(self.labels,budget=2)
        self.assertFalse(hasattr(o.public_view(),'labels'))
        self.assertEqual(o.public_view().observations,())
        o.query('a')
        self.assertEqual([(x.candidate_id,x.value) for x in o.public_view().observations],[('a',2.0)])
    def test_requery_denied(self):
        o=ControlledOracle(self.labels,budget=2);o.query('a')
        with self.assertRaises(ValueError):o.query('a')
    def test_budget_exhaustion(self):
        o=ControlledOracle(self.labels,budget=1);o.query('a')
        with self.assertRaises(ValueError):o.query('b')
    def test_unknown_id(self):
        with self.assertRaises(ValueError):ControlledOracle(self.labels,budget=2).query('missing')
    def test_invalid_budget(self):
        for n in (0,-1,True,5,1.5):
            with self.subTest(n=n),self.assertRaises(ValueError):ControlledOracle(self.labels,budget=n)
    def test_nonfinite_labels(self):
        for value in (float('nan'),float('inf'),True):
            with self.subTest(value=value),self.assertRaises(ValueError):ControlledOracle({'x':value},budget=1)
    def test_public_view_immutable(self):
        v=ControlledOracle(self.labels,budget=1).public_view()
        with self.assertRaises(FrozenInstanceError):v.remaining_budget=999
    def test_sorted_candidate_ids(self):
        self.assertEqual(ControlledOracle(self.labels,budget=1).public_view().candidate_ids,('a','b','c','d'))
    def test_callback_sees_no_oracle(self):
        seen=[]
        def choose(view):
            seen.append(view)
            self.assertFalse(hasattr(view,'query'))
            self.assertFalse(hasattr(view,'labels'))
            return next(i for i in view.candidate_ids if i not in {x.candidate_id for x in view.observations})
        report=run_synthetic_trial(labels=self.labels,budget=3,select=choose)
        self.assertEqual(report['queries_consumed'],3)
        self.assertFalse(report['contains_labels'])
        self.assertEqual(report['status'],STATUS)
        self.assertEqual([x['candidate_id'] for x in report['trace']],['a','b','c'])
        self.assertEqual([v.remaining_budget for v in seen],[3,2,1])
    def test_trace_redacts_values(self):
        report=run_synthetic_trial(labels=self.labels,budget=2,select=lambda v: next(i for i in v.candidate_ids if i not in {x.candidate_id for x in v.observations}))
        self.assertFalse(any('value' in record for record in report['trace']))
    def test_source_mapping_mutation_does_not_change_oracle(self):
        labels=dict(self.labels);o=ControlledOracle(labels,budget=1);labels['a']=999
        self.assertEqual(o.query('a').value,2.0)

if __name__=='__main__': unittest.main()
