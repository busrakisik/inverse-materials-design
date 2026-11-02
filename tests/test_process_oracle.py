import unittest
from scripts.process_oracle import _frame,run_synthetic_isolated_trial,STATUS
from scripts.synthetic_policy_worker import choose

class ProcessOracleTests(unittest.TestCase):
    def test_two_queries(self):
        r=run_synthetic_isolated_trial({'b':0.4,'a':3.1,'c':1.4},2)
        self.assertEqual([x['candidate_id'] for x in r['query_trace']],['a','b'])
    def test_budget_one(self):
        self.assertEqual(run_synthetic_isolated_trial({'x':1.0},1)['budget_used'],1)
    def test_no_labels_in_report(self):
        r=run_synthetic_isolated_trial({'a':987654.5,'b':2.0},2)
        self.assertNotIn('987654.5',str(r));self.assertFalse(r['real_labels_used'])
    def test_reproducible(self):
        a={'z':3.,'x':2.,'y':1.}
        self.assertEqual(run_synthetic_isolated_trial(a),run_synthetic_isolated_trial(a))
    def test_invalid_budget(self):
        for x in (0,-1,True,1.5):
            with self.subTest(x=x),self.assertRaises(ValueError):run_synthetic_isolated_trial({'x':1.},x)
    def test_budget_pool(self):
        with self.assertRaises(ValueError):run_synthetic_isolated_trial({'x':1.},2)
    def test_nan_rejected(self):
        with self.assertRaises(ValueError):run_synthetic_isolated_trial({'x':float('nan')})
    def test_boolean_label_rejected(self):
        with self.assertRaises(ValueError):run_synthetic_isolated_trial({'x':True})
    def test_message_size(self):
        with self.assertRaises(ValueError):_frame({'x':'a'*20000})
    def test_worker_avoids_requeries(self):
        msg={'candidate_ids':['a','b'],'remaining_budget':1,'observations':[{'candidate_id':'a','value':1.,'step':1}]}
        self.assertEqual(choose(msg),'b')
    def test_worker_does_not_receive_all_labels(self):
        msg={'candidate_ids':['a'],'remaining_budget':1,'observations':[]}
        self.assertNotIn('labels',msg);self.assertEqual(choose(msg),'a')
    def test_invalid_worker_contract(self):
        with self.assertRaises(ValueError):choose({'candidate_ids':['a']})

if __name__=='__main__':unittest.main()
