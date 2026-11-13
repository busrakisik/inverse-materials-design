"""V12.17 audit of pinned runnable BHS entrypoints, not a benchmark.

Only source-code structure and deliberately invented two-hypothesis mathematics
are evaluated. No source measurements or scientific objective values are read.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_BLOBS = {
    "src/imd_pipeline/agents/hypothesis_engine.py": "0ac39a960fecff27031769589ae5b467be526f84",
    "bhs/search/bayesian_engine.py": "f656a5f66f27048ff564b53ce36e30508800d555",
    "src/imd_pipeline/agents/bayesian_reasoner.py": "771dfc6482d2e77f4b0f91d3a8ae2e59286cd48f",
    "bhs/evidence/likelihoods.py": "8453b20c02527f55e357ef66d9a3ac100565ce47",
    "scripts/mcts_puct_policy_v1.py": "7dfcbe6a18f4d459f691406adb79b29a54fc99dc",
    "src/imd_pipeline/agents/search_planner.py": "e5152ac9bbf49f8f011832aa94ada371568ecbbc",
    "scripts/policy_worker_v1.py": "1f3f55aeaf27fea41156e02678dfb267c262d5c9",
    "scripts/synthetic_policy_worker.py": "c2bd437930dd900672bcf4ddcdcc85fd5ec8863e",
    "scripts/bhs_replicate_pool_v11.py": "65044ae33514020f55fe6cb10f62b03a9e955a05",
    "scripts/uci_concrete_v5.py": "5f98093426ac9cf4c4fc431f0d4f9aeada6d462f",
    "src/imd_pipeline/agents/consensus_engine.py": "410cba88136764aefd4bb79f300485ab21ebfb5f",
}
SUPPLIED_V11_DESCRIPTORS = ("n", "theta", "r", "t")
V11_RECORDED_MEAN_REGRET_J = {
    "gp_ard_ei": 7.363,
    "rf_ucb": 8.983,
    "bhs_v5_kernel_portfolio_ei": 9.368,
    "random": 15.951,
}
NO_GO = {
    "development_only": True,
    "scored_validation_allowed": False,
    "full_bhs_fair_comparison_ready": False,
    "per_feature_origin_timing_access_certified": False,
    "independent_holdout_used": False,
    "physical_validation_by_bhs": False,
    "claim_of_superiority": False,
    "real_savings_measured": False,
    "laboratory_action_allowed": False,
}


class ReadinessError(ValueError):
    pass


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def verify_pinned_sources(root: Path = ROOT) -> dict:
    checked = {}
    for path, expected in sorted(SOURCE_BLOBS.items()):
        file = root / path
        if not file.is_file():
            raise ReadinessError("PINNED_SOURCE_MISSING: " + path)
        raw = file.read_bytes()
        actual = git_blob_sha1(raw)
        if actual != expected:
            raise ReadinessError("PINNED_SOURCE_CHANGED: " + path)
        try:
            ast.parse(raw.decode("utf-8"), filename=path)
        except (SyntaxError, UnicodeError) as exc:
            raise ReadinessError("SOURCE_PYTHON_SYNTAX_ERROR: " + path) from exc
        checked[path] = {"git_blob_sha1": actual, "sha256": hashlib.sha256(raw).hexdigest()}
    return checked


def _check_source_program(root: Path) -> dict:
    source = {path: (root / path).read_text(encoding="utf-8")
              for path in SOURCE_BLOBS}
    trees = {path: ast.parse(body) for path, body in source.items()}

    def has_import(path: str, module: str, imported: str) -> bool:
        return any(
            isinstance(node, ast.ImportFrom) and node.module == module
            and any(a.name == imported for a in node.names)
            for node in ast.walk(trees[path])
        )

    def class_method(path: str, cls: str, method: str) -> bool:
        return any(
            isinstance(node, ast.ClassDef) and node.name == cls
            and any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and n.name == method for n in node.body)
            for node in trees[path].body
        )

    requirements = {
        "illustrative_registry_method": class_method(
            "src/imd_pipeline/agents/hypothesis_engine.py",
            "HypothesisAndExplainabilityEngine", "evaluate_competing_hypotheses"),
        "posterior_update_method": class_method(
            "bhs/search/bayesian_engine.py",
            "BayesianHypothesisSearchEngine", "accumulate_evidence"),
        "unimplemented_uct_interface": (
            class_method("bhs/search/bayesian_engine.py",
                         "BayesianHypothesisSearchEngine", "compute_uct")
            and "raise NotImplementedError" in source["bhs/search/bayesian_engine.py"]),
        "uncalibrated_source_heuristics": (
            "UNCALIBRATED" in source["bhs/evidence/likelihoods.py"]
            and "NOT a measured Bayesian likelihood" in source["bhs/evidence/likelihoods.py"]),
        "open_loop_candidate_id_tree": (
            class_method("scripts/mcts_puct_policy_v1.py", "OpenLoopPUCTPolicyV1", "choose")
            and "node.path + (cid,)" in source["scripts/mcts_puct_policy_v1.py"]
            and "branches on candidate IDs, NOT on observed responses"
            in source["scripts/mcts_puct_policy_v1.py"]),
        "legacy_budget_unallocated": (
            class_method("src/imd_pipeline/agents/search_planner.py",
                         "AdaptiveBudgetPlanner", "allocate_and_evaluate")
            and '"budget_status": "NOT_ALLOCATED"'
            in source["src/imd_pipeline/agents/search_planner.py"]),
        "runtime_worker_bayesian_scalar_only": has_import(
            "scripts/policy_worker_v1.py",
            "scripts.bayesian_only_policy_v1", "BayesianOnlyPolicyV1"),
        "placeholder_first_unqueried_worker": (
            "return next(x for x in ids if x not in queried)"
            in source["scripts/synthetic_policy_worker.py"]),
        "v11_calls_statistical_portfolio_not_full_hypothesis": has_import(
            "scripts/bhs_replicate_pool_v11.py",
            "scripts.uci_concrete_v5", "choose_next"),
        "statistical_portfolio_selector_exists": (
            "def choose_next(" in source["scripts/uci_concrete_v5.py"]
            and '"kernel_portfolio_ei"' in source["scripts/uci_concrete_v5.py"]),
        "consensus_is_supplied_arithmetic_only": (
            "DESCRIPTIVE ARITHMETIC ONLY"
            in source["src/imd_pipeline/agents/consensus_engine.py"]),
    }
    if not all(requirements.values()):
        raise ReadinessError(
            "CURRENT_CAPABILITY_EVIDENCE_CHANGED: " +
            ",".join(k for k, v in requirements.items() if not v))
    return requirements


def check_runtime_contracts() -> dict:
    """Only evaluate illustrative mathematical/historical-interface contracts."""
    from bhs.search.bayesian_engine import BayesianHypothesisSearchEngine
    from src.imd_pipeline.agents.hypothesis_engine import HypothesisAndExplainabilityEngine
    from src.imd_pipeline.agents.search_planner import AdaptiveBudgetPlanner

    hypotheses = HypothesisAndExplainabilityEngine.evaluate_competing_hypotheses(
        ["illustrative property"])
    if (hypotheses["selection_status"] != "NOT_EVALUATED"
            or hypotheses["chosen_hypothesis"] is not None
            or hypotheses["candidate_generation_status"] != "NOT_RUN"
            or any(x.get("chosen") for x in hypotheses["competing_hypotheses"])):
        raise ReadinessError("UNVERIFIED_HYPOTHESES_PRESENTED_AS_SELECTED")

    engine = BayesianHypothesisSearchEngine(initial_priors={"H0": 0.5, "H1": 0.5})
    result = engine.accumulate_evidence(
        step_name="explicit-manufactured-test-likelihoods",
        likelihoods={"H0": 0.75, "H1": 0.25})
    post = {name: float(v.value) for name, v in result["posteriors"].items()}
    if (abs(post["H0"]-0.75) > 1e-12 or abs(post["H1"]-0.25) > 1e-12
            or result["evidence_verification_status"] != "NOT_VERIFIED"):
        raise ReadinessError("BAYES_MATH_RUNTIME_CONTRACT_CHANGED")
    try:
        engine.compute_uct("H0")
    except NotImplementedError:
        pass
    else:
        raise ReadinessError("UNVERIFIED_PHYSICAL_TREE_SCORE_PRESENT")

    budget = AdaptiveBudgetPlanner.allocate_and_evaluate(0.5)
    if (budget["budget_status"] != "NOT_ALLOCATED"
            or budget["model_execution_status"] != "NOT_RUN"
            or budget["allocated_compute"] is not None):
        raise ReadinessError("UNVERIFIED_RESOURCE_EXECUTION_PRESENT")
    return {
        "illustrative_registry_no_physical_hypothesis_selected": True,
        "manufactured_likelihood_posterior_test": {
            "inputs": {"H0": 0.75, "H1": 0.25},
            "starting_priors": {"H0": 0.5, "H1": 0.5},
            "posteriors": post,
            "physical_likelihood_calibrated": False,
            "scientific_benchmark_score": None,
        },
        "legacy_uct_score_not_implemented": True,
        "legacy_planner_allocated_compute": False,
        "physical_calculations_executed": False,
    }


def audit(root: Path = ROOT) -> dict:
    sources = verify_pinned_sources(root)
    structure = _check_source_program(root)
    runtime = check_runtime_contracts()
    v11 = V11_RECORDED_MEAN_REGRET_J
    return {
        "schema": "BHS-V12.17-FULL-SYSTEM-READINESS",
        "purpose": "source_and_mathematical_contracts_only_no_new_scored_experiment",
        "pinned_code_scope": "11_examined_historical_default_entrypoints_not_exhaustive",
        "historical_default_commit": "af882913f867c42bbc16794e4e53ffe2fea4fbba",
        "source_module_count": len(sources),
        "source_integrity": sources,
        "structural_contracts": structure,
        "runtime_contracts": runtime,
        "verified_component_capabilities": {
            "illustrative_hypothesis_registry": True,
            "mathematical_bayesian_update_from_supplied_likelihoods": True,
            "open_loop_scalar_synthetic_tree_search": True,
            "historical_statistical_kernel_selector": True,
            "source_issued_physical_hypothesis_selection": False,
            "physically_calibrated_evidence_likelihoods": False,
            "observation_contingent_full_hypothesis_planner": False,
            "live_scientific_computation_budget_allocation": False,
            "single_end_to_end_full_bhs_policy_in_checked_entrypoints": False,
        },
        "v11_existing_measured_source_result": {
            "scope": "kernel_portfolio_component_only_retrospective_development",
            "original_source_record_kind": "600_geometries_three_measured_toughness_replicates_each",
            "identical_budget_distinct_geometries": 16,
            "identical_budget_historical_responses": 48,
            "development_seeds": [7, 13, 23, 31, 43],
            "reported_mean_simple_regret_j": v11,
            "bhs_minus_gp_ard_regret_j": round(
                v11["bhs_v5_kernel_portfolio_ei"] - v11["gp_ard_ei"], 3),
            "bhs_minus_rf_regret_j": round(
                v11["bhs_v5_kernel_portfolio_ei"] - v11["rf_ucb"], 3),
            "full_hypothesis_centric_bhs_performance_evaluated": False,
            "new_scientific_outcomes_read": False,
        },
        "v11_input_feature_passport": {
            key: {
                "source": "original_3d_printed_crossed_barrel_design_parameters",
                "pre_measurement": "public_design_parameter_before_printing_or_testing",
                "policy_time": "passed_to_all_v11_replayed_selection_methods",
                "full_bhs_policy_has_used_field": False,
                "independent_prospective_holdout_verified": False,
            } for key in SUPPLIED_V11_DESCRIPTORS
        },
        "dft_input_geometry_passport_status": "V12.16_ORIGINAL_INPUT_MISMATCH_NO_MODEL_USE",
        "next_required_scientific_work": [
            "operational_competing_falsifiable_domain_hypotheses",
            "verified_physical_likelihood_and_update_model",
            "end_to_end_action_selection_with_heldout_outcomes_hidden",
            "accurate_observation_contingent_lookahead_or_declared_nonadaptive_variant",
            "equal_time_appropriate_feature_and_budget_access_to_reference_methods",
            "fully_separate_independent_test_and_external_physical_validation",
        ],
        "status": "FULL_BHS_NOT_EVALUABLE_YET_EXISTING_COMPONENT_RESULT_NEGATIVE",
        "new_scientific_performance_experiment_run": False,
        **NO_GO,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print("Implementation scope:", result["source_module_count"], "pinned modules")
    print("Bayes math:", result["runtime_contracts"]["manufactured_likelihood_posterior_test"]["posteriors"])
    print("Historical v11 component performance: GP", V11_RECORDED_MEAN_REGRET_J["gp_ard_ei"],
          "BHS", V11_RECORDED_MEAN_REGRET_J["bhs_v5_kernel_portfolio_ei"])
    print("Full BHS fair-scored readiness:", result["full_bhs_fair_comparison_ready"])
    print("No measured source outcomes or new benchmark scoring.")


if __name__ == "__main__":
    main()
