import tempfile, unittest
from scripts.paired_benchmark_pilot_v1 import evaluate,build_pilot,summarize,write_outputs,STATUS
class PilotTests(unittest.TestCase):
 def test_random_budget(self):self.assertEqual(evaluate(1,'smooth',10,'random')['queries'],10)
 def test_greedy_budget(self):self.assertEqual(evaluate(1,'smooth',5,'greedy')['queries'],5)
 def test_bayesian_budget(self):self.assertEqual(evaluate(1,'smooth',2,'bayesian_only')['queries'],2)
 def test_status(self):self.assertEqual(evaluate(1,'smooth',1,'random')['status'],STATUS)
 def test_nonnegative_regret(self):self.assertGreaterEqual(evaluate(2,'mismatched',10,'bayesian_only')['simple_regret'],0)
 def test_deterministic_trace(self):
  a=evaluate(3,'multimodal',5,'bayesian_only');b=evaluate(3,'multimodal',5,'bayesian_only')
  self.assertEqual(a['trace'],b['trace'])
 def test_task_matching(self):
  self.assertEqual(evaluate(2,'smooth',5,'random')['task_public_sha256'],evaluate(2,'smooth',5,'bayesian_only')['task_public_sha256'])
 def test_scenarios(self):
  for s in ('smooth','multimodal','uninformative','mismatched','duplicates'):
   self.assertEqual(evaluate(0,s,1,'random')['scenario'],s)
 def test_unpaired_seed_rejected(self):
  with self.assertRaises(ValueError):build_pilot([1,1])
 def test_bad_policy_rejected(self):
  with self.assertRaises(ValueError):evaluate(1,'smooth',1,'bad')
 def test_pilot_cardinality(self):self.assertEqual(len(build_pilot(range(2))),120)
 def test_summary_cardinality(self):self.assertEqual(len(summarize(build_pilot(range(2)))),40)
 def test_manifest(self):
  rows=build_pilot(range(2))
  with tempfile.TemporaryDirectory() as d:
   m=write_outputs(d,rows,summarize(rows));self.assertTrue(m['synthetic_only']);self.assertFalse(m['confirmatory']);self.assertEqual(m['n_rows'],120)
if __name__=='__main__':unittest.main()
