"""V12.17 implementation contracts: no real observation, cost or model score."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import bhs_v1217_architecture_readiness as a


class BHSArchitectureReadinessTests(unittest.TestCase):
    def test_git_blob_sha_uses_correct_git_object_format(self):
        raw=b"sample"
        expected=hashlib.sha1(b"blob 6\0sample").hexdigest()
        self.assertEqual(a.git_blob_sha1(raw), expected)

    def test_pinned_original_entrypoints_are_unchanged(self):
        result=a.verify_pinned_sources()
        self.assertEqual(len(result),11)
        for path, expected in a.SOURCE_BLOBS.items():
            self.assertEqual(result[path]["git_blob_sha1"], expected)
            self.assertEqual(len(result[path]["sha256"]),64)

    def test_changed_source_is_refused_not_renamed(self):
        with tempfile.TemporaryDirectory() as dirname:
            root=Path(dirname)
            for path in a.SOURCE_BLOBS:
                f=root/path
                f.parent.mkdir(parents=True,exist_ok=True)
                f.write_bytes((a.ROOT/path).read_bytes())
            altered=root/"scripts/bhs_replicate_pool_v11.py"
            altered.write_bytes(altered.read_bytes()+b"\n# tampered\n")
            with self.assertRaisesRegex(a.ReadinessError,"PINNED_SOURCE_CHANGED"):
                a.verify_pinned_sources(root)

    def test_missing_source_is_refused(self):
        with tempfile.TemporaryDirectory() as dirname:
            with self.assertRaisesRegex(a.ReadinessError,"PINNED_SOURCE_MISSING"):
                a.verify_pinned_sources(Path(dirname))

    def test_source_ast_hypothesis_registry_present(self):
        flags=a._check_source_program(a.ROOT)
        self.assertTrue(flags["illustrative_registry_method"])
        self.assertTrue(flags["posterior_update_method"])
        self.assertTrue(flags["unimplemented_uct_interface"])
        self.assertTrue(flags["uncalibrated_source_heuristics"])

    def test_source_ast_proves_actual_worker_and_historical_selector(self):
        flags=a._check_source_program(a.ROOT)
        self.assertTrue(flags["runtime_worker_bayesian_scalar_only"])
        self.assertTrue(flags["v11_calls_statistical_portfolio_not_full_hypothesis"])
        self.assertTrue(flags["statistical_portfolio_selector_exists"])
        self.assertTrue(flags["placeholder_first_unqueried_worker"])

    def test_source_ast_proves_nonexecuting_budget_and_open_loop(self):
        flags=a._check_source_program(a.ROOT)
        self.assertTrue(flags["open_loop_candidate_id_tree"])
        self.assertTrue(flags["legacy_budget_unallocated"])
        self.assertTrue(flags["consensus_is_supplied_arithmetic_only"])

    def test_synthetic_math_only_posteriors(self):
        result=a.check_runtime_contracts()
        fixture=result["manufactured_likelihood_posterior_test"]
        self.assertEqual(fixture["posteriors"],{"H0":0.75,"H1":0.25})
        self.assertFalse(fixture["physical_likelihood_calibrated"])
        self.assertIsNone(fixture["scientific_benchmark_score"])

    def test_legacy_mcts_raises_not_implemented(self):
        from bhs.search.bayesian_engine import BayesianHypothesisSearchEngine
        engine=BayesianHypothesisSearchEngine({"H0":0.5,"H1":0.5})
        with self.assertRaises(NotImplementedError):
            engine.compute_uct("H0")

    def test_bayes_likelihood_validation_blocks_malformed_values(self):
        from bhs.search.bayesian_engine import BayesianHypothesisSearchEngine
        engine=BayesianHypothesisSearchEngine({"H0":0.5,"H1":0.5})
        for invalid in ({"H0":0.9},{"H0":0.8,"H1":float("nan")},
                        {"H0":1.0,"H1":-1.0}):
            with self.assertRaises(ValueError):
                engine.accumulate_evidence("synthetic",invalid)
            self.assertEqual(engine.priors,{"H0":0.5,"H1":0.5})

    def test_hypothesis_registry_is_illustrative_without_selection(self):
        from src.imd_pipeline.agents.hypothesis_engine import HypothesisAndExplainabilityEngine
        out=HypothesisAndExplainabilityEngine.evaluate_competing_hypotheses(["unmeasured goal"])
        self.assertIsNone(out["chosen_hypothesis"])
        self.assertEqual(out["selection_status"],"NOT_EVALUATED")
        self.assertEqual(out["pareto_optimization_status"],"NOT_RUN")
        self.assertTrue(all(not h["chosen"] and h["confidence_score"] is None
                            for h in out["competing_hypotheses"]))

    def test_legacy_budget_never_runs_expensive_calculation(self):
        from src.imd_pipeline.agents.search_planner import AdaptiveBudgetPlanner
        r=AdaptiveBudgetPlanner.allocate_and_evaluate(1.0)
        self.assertEqual(r["budget_status"],"NOT_ALLOCATED")
        self.assertEqual(r["model_execution_status"],"NOT_RUN")
        self.assertIsNone(r["allocated_gpu_hours"])

    def test_scoring_gate_remains_closed(self):
        r=a.audit()
        self.assertEqual(r["status"],
                         "FULL_BHS_NOT_EVALUABLE_YET_EXISTING_COMPONENT_RESULT_NEGATIVE")
        self.assertFalse(r["scored_validation_allowed"])
        self.assertFalse(r["new_scientific_performance_experiment_run"])
        self.assertFalse(r["full_bhs_fair_comparison_ready"])
        self.assertFalse(r["claim_of_superiority"])

    def test_executed_capability_not_misnamed_full_system(self):
        r=a.audit()["verified_component_capabilities"]
        self.assertTrue(r["mathematical_bayesian_update_from_supplied_likelihoods"])
        self.assertTrue(r["open_loop_scalar_synthetic_tree_search"])
        self.assertFalse(r["source_issued_physical_hypothesis_selection"])
        self.assertFalse(r["single_end_to_end_full_bhs_policy_in_checked_entrypoints"])
        self.assertFalse(r["physically_calibrated_evidence_likelihoods"])

    def test_inherited_real_component_negative_evidence_preserved(self):
        v=a.audit()["v11_existing_measured_source_result"]
        self.assertEqual(v["identical_budget_distinct_geometries"],16)
        self.assertEqual(v["identical_budget_historical_responses"],48)
        self.assertEqual(v["bhs_minus_gp_ard_regret_j"],2.005)
        self.assertEqual(v["bhs_minus_rf_regret_j"],0.385)
        self.assertFalse(v["full_hypothesis_centric_bhs_performance_evaluated"])
        self.assertFalse(v["new_scientific_outcomes_read"])

    def test_design_time_passport_complete_and_not_full_system(self):
        info=a.audit()["v11_input_feature_passport"]
        self.assertEqual(set(info),{"n","theta","r","t"})
        for d in info.values():
            self.assertIn("before_printing_or_testing",d["pre_measurement"])
            self.assertFalse(d["full_bhs_policy_has_used_field"])
            self.assertFalse(d["independent_prospective_holdout_verified"])

    def test_source_reports_are_digest_invariant_without_new_scores(self):
        one=a.audit()
        two=a.audit()
        self.assertEqual(json.dumps(one,sort_keys=True),json.dumps(two,sort_keys=True))
        self.assertNotIn("selected_new_material",json.dumps(one))

    def test_no_physical_labels_are_generated_by_audit(self):
        data=json.dumps(a.audit())
        self.assertNotIn("new_test_regret",data)
        self.assertNotIn("sampled_physical_response",data)
        self.assertFalse(a.NO_GO["physical_validation_by_bhs"])
        self.assertFalse(a.NO_GO["laboratory_action_allowed"])


if __name__ == "__main__":
    unittest.main()
