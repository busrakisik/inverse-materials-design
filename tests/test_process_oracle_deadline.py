import time
import unittest
from scripts.process_oracle_deadline import (
    OracleDeadlineError, OracleProtocolError, run_synthetic_deadline_trial,
)

class DeadlineGateTests(unittest.TestCase):
    def test_ordinary_worker(self):
        r = run_synthetic_deadline_trial({'b': 4.0, 'a': 9.0}, 2)
        self.assertEqual([x['candidate_id'] for x in r['query_trace']], ['a', 'b'])
        self.assertFalse(r['real_labels_used'])
        self.assertFalse(r['benchmark_run'])
        self.assertNotIn('9.0', str(r))

    def test_worker_hang_has_deadline(self):
        start = time.monotonic()
        with self.assertRaises(OracleDeadlineError):
            run_synthetic_deadline_trial({'hang': 1.0}, 1, worker_module='tests.oracle_bad_worker', response_timeout_seconds=0.25)
        self.assertLess(time.monotonic() - start, 3)

    def test_worker_exit_rejected(self):
        with self.assertRaises(OracleProtocolError):
            run_synthetic_deadline_trial({'exit': 1.0}, 1, worker_module='tests.oracle_bad_worker')

    def test_invalid_json_rejected(self):
        with self.assertRaises(OracleProtocolError):
            run_synthetic_deadline_trial({'invalid': 1.0}, 1, worker_module='tests.oracle_bad_worker')

    def test_oversize_rejected(self):
        with self.assertRaises(OracleProtocolError):
            run_synthetic_deadline_trial({'oversize': 1.0}, 1, worker_module='tests.oracle_bad_worker')

    def test_unknown_candidate_rejected(self):
        with self.assertRaises(OracleProtocolError):
            run_synthetic_deadline_trial({'unknown': 1.0}, 1, worker_module='tests.oracle_bad_worker')

    def test_invalid_schema_rejected(self):
        with self.assertRaises(OracleProtocolError):
            run_synthetic_deadline_trial({'schema': 1.0}, 1, worker_module='tests.oracle_bad_worker')

    def test_invalid_timeout_rejected(self):
        for val in (0, -1, True, float('nan'), float('inf')):
            with self.subTest(val=val), self.assertRaises(ValueError):
                run_synthetic_deadline_trial({'x': 1.0}, 1, response_timeout_seconds=val)

if __name__ == '__main__':
    unittest.main()
