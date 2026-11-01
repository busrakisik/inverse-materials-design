"""Synthetic protocol contract tests: no CHGNet, no materials performance claims."""
import unittest

from bhs.benchmarks.offline_harness import (
    Candidate, Oracle, Observation, PublicFeatureRanking, RandomWithoutReplacement,
    STATUS, run_trial, synthetic_example,
)


class OfflineHarnessTests(unittest.TestCase):
    def setUp(self):
        self.candidates = (Candidate("A", 0.2), Candidate("B", 0.8), Candidate("C", 0.5))
        self.oracle = Oracle({"A": 5.0, "B": 1.0, "C": 3.0})

    def test_query_budget_and_distinct_queries(self):
        result = run_trial(self.candidates, self.oracle, RandomWithoutReplacement(9), budget=3, seed=9)
        self.assertEqual(result["query_count"], 3)
        self.assertEqual(len({r["candidate_id"] for r in result["query_log"]}), 3)
        self.assertEqual(result["status"], STATUS)

    def test_policy_cannot_observe_future_labels(self):
        class Inspector:
            def choose(self, view):
                self_fields = set(view.__dataclass_fields__)
                assert self_fields == {"remaining", "observations", "queries_left"}
                assert all(isinstance(c, Candidate) for c in view.remaining)
                assert all(isinstance(o, Observation) for o in view.observations)
                assert len(view.observations) + len(view.remaining) == 3
                return view.remaining[0].identifier
        result = run_trial(self.candidates, self.oracle, Inspector(), budget=3, seed=1)
        self.assertEqual(result["query_count"], 3)

    def test_repeatable_seed(self):
        first = run_trial(self.candidates, self.oracle, RandomWithoutReplacement(2), budget=2, seed=2)
        second = run_trial(self.candidates, self.oracle, RandomWithoutReplacement(2), budget=2, seed=2)
        self.assertEqual(first, second)

    def test_requery_and_unknown_rejected(self):
        class Requery:
            def choose(self, view): return "A"
        with self.assertRaises(ValueError):
            run_trial(self.candidates, self.oracle, Requery(), budget=2, seed=1)

    def test_budget_validation(self):
        for n in (0, 4, True, -1):
            with self.subTest(n=n), self.assertRaises(ValueError):
                run_trial(self.candidates, self.oracle, PublicFeatureRanking(), budget=n, seed=2)

    def test_reject_mismatched_identifiers(self):
        with self.assertRaises(ValueError):
            run_trial((Candidate("X", 0.0),), self.oracle, PublicFeatureRanking(), budget=1, seed=2)

    def test_history_best_so_far(self):
        result = run_trial(self.candidates, self.oracle, PublicFeatureRanking(), budget=3, seed=1)
        self.assertEqual([x["candidate_id"] for x in result["query_log"]], ["B", "C", "A"])
        self.assertEqual([x["best_so_far"] for x in result["query_log"]], [1.0, 3.0, 5.0])

    def test_synthetic_only(self):
        example = synthetic_example()
        self.assertEqual(set(example), {"random", "public_feature_ranking"})
        self.assertTrue(all(v["status"] == STATUS for v in example.values()))


if __name__ == "__main__":
    unittest.main()
