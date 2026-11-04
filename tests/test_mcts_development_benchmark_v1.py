"""Contract tests for exploratory development-only MCTS comparisons."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import mcts_development_benchmark_v1 as b


class DevelopmentBenchmarkTests(unittest.TestCase):
    def test_reject_holdout_and_other_unseen_seeds(self):
        for value in (10000, 10099, 30, -1, True, 0.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                b.validate_seeds([value])

    def test_reject_duplicate_or_empty_seeds(self):
        for values in ([], [0, 0]):
            with self.assertRaises(ValueError):
                b.validate_seeds(values)

    def test_allow_known_pilot_seeds(self):
        self.assertEqual(b.validate_seeds([0, 7, 29]), (0, 7, 29))

    def test_seed_derivation_matches_original_pilot_for_bayesian(self):
        scenario, seed = "smooth", 7
        digest = hashlib.sha256(f"policy:{seed}:{scenario}:bayesian_only".encode()).digest()
        self.assertEqual(b.policy_seed(scenario, seed, "bayesian_only"),
                         int.from_bytes(digest[:8], "big"))

    def test_variants_are_distinct(self):
        self.assertEqual(set(b.VARIANTS), {"random", "greedy", "bayesian_only",
                          "mcts_32_h1", "mcts_32_h3", "mcts_96_h3"})

    def test_policy_factory_configuration(self):
        self.assertEqual((b.create_policy("mcts_32_h1", 1).simulations,
                          b.create_policy("mcts_32_h1", 1).horizon), (32, 1))
        self.assertEqual((b.create_policy("mcts_96_h3", 1).simulations,
                          b.create_policy("mcts_96_h3", 1).horizon), (96, 3))

    def test_unknown_variant_rejected(self):
        with self.assertRaises(ValueError):
            b.create_policy("not-a-policy", 1)

    def test_evaluate_rejects_holdout_before_task_construction(self):
        with patch.object(b, "make_task") as fake:
            with self.assertRaises(ValueError):
                b.evaluate_one("smooth", 10000, 5, "mcts_32_h1")
            fake.assert_not_called()

    def test_evaluate_one_budget_is_exact(self):
        row = b.evaluate_one("smooth", 7, 1, "mcts_32_h1")
        self.assertEqual(row["queries"], 1)
        self.assertEqual(len(row["selected_ids"]), 1)
        self.assertFalse(row["scored_validation_allowed"])

    def test_pairing_on_same_public_task(self):
        rows = b.run_development([0], scenarios=["smooth"], budgets=[1])
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({r["task_public_sha256"] for r in rows}), 1)
        self.assertEqual({r["variant"] for r in rows}, set(b.VARIANTS))

    def test_missing_pair_rejected(self):
        rows = b.run_development([0], scenarios=["smooth"], budgets=[1])
        with self.assertRaises(ValueError):
            b.summarize(rows[:-1])

    def test_duplicate_pair_rejected(self):
        rows = b.run_development([0], scenarios=["smooth"], budgets=[1])
        with self.assertRaises(ValueError):
            b.summarize(rows + rows[:1])

    def test_summary_has_all_three_comparators(self):
        rows = b.run_development([0], scenarios=["smooth"], budgets=[1])
        summary = b.summarize(rows)
        self.assertEqual(len(summary), 9)
        self.assertEqual({r["comparator"] for r in summary},
                         {"random", "greedy", "bayesian_only"})

    def test_manifest_fail_closed_and_checksum(self):
        rows = b.run_development([0], scenarios=["smooth"], budgets=[1])
        with tempfile.TemporaryDirectory() as directory:
            manifest = b.write_outputs(directory, rows, b.summarize(rows), (0,))
            self.assertFalse(manifest["scored_validation_allowed"])
            self.assertFalse(manifest["confirmatory"])
            self.assertTrue(manifest["pilot_informed"])
            p = Path(directory) / "development_manifest.json"
            sha = Path(directory, "development_manifest.sha256").read_text().split()[0]
            self.assertEqual(sha, hashlib.sha256(p.read_bytes()).hexdigest())
            self.assertEqual(json.loads(p.read_text())["n_rows"], 6)

    def test_reject_duplicate_budget(self):
        with self.assertRaises(ValueError):
            b.run_development([0], scenarios=["smooth"], budgets=[1, 1])

    def test_output_deterministic_except_timing(self):
        a = b.evaluate_one("smooth", 7, 5, "mcts_32_h3")
        c = b.evaluate_one("smooth", 7, 5, "mcts_32_h3")
        a.pop("wall_seconds")
        c.pop("wall_seconds")
        self.assertEqual(a, c)


if __name__ == "__main__":
    unittest.main()
