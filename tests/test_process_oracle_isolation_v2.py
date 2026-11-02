import unittest, time
from scripts.process_oracle_isolation_v2 import run_synthetic_isolation_trial,IsolationDeadlineError,IsolationProtocolError
class IsolationV2Tests(unittest.TestCase):
 def test_normal(self):
  r=run_synthetic_isolation_trial({'b':2.,'a':1.},2)
  self.assertEqual([x['candidate_id'] for x in r['query_trace']],['a','b']);self.assertFalse(r['real_labels_used'])
 def test_redaction(self):
  r=run_synthetic_isolation_trial({'x':987654.125},1)
  self.assertNotIn('987654.125',str(r));self.assertFalse(r['benchmark_run'])
 def test_hung_worker(self):
  with self.assertRaises(IsolationDeadlineError):run_synthetic_isolation_trial({'hang':1.},1,worker_module='tests.isolation_bad_worker',timeout_seconds=.3)
 def test_descendant_group(self):
  t=time.monotonic()
  with self.assertRaises(IsolationDeadlineError):run_synthetic_isolation_trial({'descendant':1.},1,worker_module='tests.isolation_bad_worker',timeout_seconds=.3)
  self.assertLess(time.monotonic()-t,3)
 def test_early_exit(self):
  with self.assertRaises(IsolationProtocolError):run_synthetic_isolation_trial({'exit':1.},1,worker_module='tests.isolation_bad_worker')
 def test_malformed(self):
  with self.assertRaises(IsolationProtocolError):run_synthetic_isolation_trial({'malformed':1.},1,worker_module='tests.isolation_bad_worker')
 def test_oversize(self):
  with self.assertRaises(IsolationProtocolError):run_synthetic_isolation_trial({'oversize':1.},1,worker_module='tests.isolation_bad_worker')
 def test_unknown(self):
  with self.assertRaises(IsolationProtocolError):run_synthetic_isolation_trial({'unknown':1.},1,worker_module='tests.isolation_bad_worker')
 def test_schema(self):
  with self.assertRaises(IsolationProtocolError):run_synthetic_isolation_trial({'schema':1.},1,worker_module='tests.isolation_bad_worker')
 def test_bad_timeout(self):
  for x in (0,-1,True,float('nan'),float('inf')):
   with self.subTest(x=x),self.assertRaises(ValueError):run_synthetic_isolation_trial({'x':1.},1,timeout_seconds=x)
if __name__=='__main__':unittest.main()
