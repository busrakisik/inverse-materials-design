"""Tests of non-fabrication and input validation; NOT material science benchmarks."""

import copy
import socket
import urllib.request

import pytest

from src.imd_pipeline.agents.hypothesis_engine import (
    HypothesisAndExplainabilityEngine,
    ILLUSTRATIVE_FAMILIES,
)


def _evaluate(targets=None):
    if targets is None:
        targets = ["fast charging", "thermal stability"]
    return HypothesisAndExplainabilityEngine.evaluate_competing_hypotheses(targets)


def _explain(data=None):
    return HypothesisAndExplainabilityEngine.explain_why_selected(
        {} if data is None else data
    )


def test_three_illustrative_families_listed():
    assert len(_evaluate()["competing_hypotheses"]) == 3


def test_candidate_ids_match_explicit_templates():
    ids = [c["id"] for c in _evaluate()["competing_hypotheses"]]
    assert ids == ["HYP-A", "HYP-B", "HYP-C"]


def test_candidate_labels_match_template_registry():
    actual = [(c["id"], c["family"]) for c in _evaluate()["competing_hypotheses"]]
    assert actual == list(ILLUSTRATIVE_FAMILIES)


def test_candidate_provenance_always_illustrative():
    assert all(
        c["candidate_provenance"] == "ILLUSTRATIVE_TEMPLATE"
        for c in _evaluate()["competing_hypotheses"]
    )


def test_no_hypothesis_is_selected():
    result = _evaluate()
    assert result["chosen_hypothesis"] is None
    assert result["selection_status"] == "NOT_EVALUATED"
    assert all(c["chosen"] is False for c in result["competing_hypotheses"])


def test_no_unsupported_confidence_or_uncertainty():
    for candidate in _evaluate()["competing_hypotheses"]:
        assert candidate["confidence_score"] is None
        assert candidate["confidence_std"] is None


def test_no_unverified_pros_cons_or_selection_reason():
    for candidate in _evaluate()["competing_hypotheses"]:
        assert candidate["pros"] is None
        assert candidate["cons"] is None
        assert candidate["selection_reason"] is None


def test_physical_claims_remain_unverified():
    assert all(
        c["physical_evidence_status"] == "NOT_VERIFIED"
        for c in _evaluate()["competing_hypotheses"]
    )


def test_candidates_never_claim_comparative_evaluation():
    assert all(
        c["comparison_status"] == "NOT_EVALUATED"
        for c in _evaluate()["competing_hypotheses"]
    )


def test_no_candidate_generation_or_pareto_runs_claimed():
    result = _evaluate()
    assert result["candidate_generation_status"] == "NOT_RUN"
    assert result["pareto_optimization_status"] == "NOT_RUN"


def test_research_targets_always_caller_supplied_and_unverified():
    result = _evaluate(["electrolyte compatibility"])
    assert result["research_targets"] == ["electrolyte compatibility"]
    assert result["targets_provenance"] == "CALLER_SUPPLIED_NOT_VERIFIED"


def test_targets_trimmed_and_order_preserved():
    result = _evaluate(["  objective one  ", " objective two ", "third"])
    assert result["research_targets"] == ["objective one", "objective two", "third"]

def test_evaluation_never_mutates_caller_targets():
    targets = ["  target  ", "another"]
    before = copy.deepcopy(targets)
    _evaluate(targets)
    assert targets == before


def test_selection_narrative_explicitly_says_no_selection():
    narrative = _evaluate()["selection_narrative"]
    assert "NO HYPOTHESIS HAS BEEN SELECTED" in narrative
    assert "No validated performance comparison" in narrative


def test_repeat_evaluation_deterministic_without_shared_results():
    a, b = _evaluate(), _evaluate()
    assert a == b
    assert a is not b
    assert a["competing_hypotheses"] is not b["competing_hypotheses"]


def test_mutating_one_evaluation_does_not_taint_later_calls():
    first = _evaluate()
    first["competing_hypotheses"][0]["chosen"] = True
    first["competing_hypotheses"][0]["confidence_score"] = 0.99
    first["research_targets"].append("fabricated result")
    second = _evaluate()
    assert all(c["chosen"] is False for c in second["competing_hypotheses"])
    assert all(c["confidence_score"] is None for c in second["competing_hypotheses"])
    assert second["research_targets"] == ["fast charging", "thermal stability"]


def test_explain_returns_explicit_nonselection_not_fabricated_reasons():
    lines = _explain()
    assert len(lines) == 5
    assert lines[0].startswith("NOT_EVALUATED")
    assert sum(line.startswith("NOT_RUN") for line in lines) == 3
    assert lines[-1].startswith("NOT_CHECKED")

def test_explanation_does_not_repeat_unverified_caller_claims():
    fake = {
        "novelty_score": "89.4%",
        "patent_prior_art": {"status": "CLEAR"},
        "e_form": -9.999,
        "confidence_score": 0.99,
    }
    reasons = _explain(fake)
    text = " ".join(reasons)
    assert "89.4%" not in text
    assert "CLEAR" not in text
    assert "-9.999" not in text
    assert "0.99" not in text
    assert "NOT_CHECKED" in text


def test_explanation_works_with_empty_dict():
    assert _explain({}) == _explain()


def test_explanation_does_not_mutate_candidate_data():
    candidate = {"a": {"score": 0.99}, "b": ["unverified"]}
    before = copy.deepcopy(candidate)
    _explain(candidate)
    assert candidate == before

def test_no_network_is_needed_to_register_illustrative_hypotheses(monkeypatch):
    def forbid(*args, **kwargs):
        raise AssertionError("No literature, model, or network lookup is allowed")
    monkeypatch.setattr(socket, "create_connection", forbid)
    monkeypatch.setattr(urllib.request, "urlopen", forbid)
    result = _evaluate()
    assert result["chosen_hypothesis"] is None


@pytest.mark.parametrize("bad_targets", [
    None, [], {}, (), set(), "", "research goal", 42, True,
    [" "], ["\t\n"], ["A", None], ["A", 1], ["A", True],
    ["A", " A "], ["A", "A"], [["nested"]], ["A", {}],
])
def test_invalid_targets_are_rejected(bad_targets):
    with pytest.raises(ValueError):
        HypothesisAndExplainabilityEngine.evaluate_competing_hypotheses(bad_targets)


@pytest.mark.parametrize("bad_candidate_data", [
    None, "", "unverified claim", [], (), 100, True, 0.2,
])
def test_invalid_explanation_inputs_rejected(bad_candidate_data):
    with pytest.raises(ValueError):
        HypothesisAndExplainabilityEngine.explain_why_selected(bad_candidate_data)

