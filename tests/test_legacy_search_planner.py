# BEGIN OF COMPLETE BHS LEGACY SEARCH PLANNER SAFETY TESTS — CHECK THIS LINE ON GITHUB
"""Software-safety tests: no actual GPU reservation, MLFF, or DFT calculations."""

import json
import math
import socket
import urllib.request

import pytest

from src.imd_pipeline.agents.search_planner import AdaptiveBudgetPlanner


def _plan(value=0.015):
    return AdaptiveBudgetPlanner.allocate_and_evaluate(value)


def test_input_is_caller_supplied_and_not_verified():
    result = _plan(0.02)
    assert result["input_candidate_uncertainty"] == pytest.approx(0.02)
    assert result["uncertainty_provenance"] == "CALLER_SUPPLIED_NOT_VERIFIED"
    assert result["uncertainty_calibration_status"] == "NOT_VERIFIED"


def test_no_uncertainty_unit_is_invented():
    assert _plan()["uncertainty_unit"] is None


def test_no_execution_tier_is_invented():
    result = _plan()
    assert result["execution_tier"] is None
    assert result["tier_selection_status"] == "NOT_EVALUATED"


def test_no_compute_engines_are_claimed_active():
    result = _plan()
    assert result["active_engines"] == []
    assert result["model_execution_status"] == "NOT_RUN"


def test_no_gpu_hours_are_manufactured():
    result = _plan()
    assert result["allocated_compute"] is None
    assert result["allocated_gpu_hours"] is None


def test_no_resources_are_reported_as_allocated():
    result = _plan()
    assert result["budget_status"] == "NOT_ALLOCATED"
    assert result["compute_reservation_status"] == "NOT_REQUESTED"
    assert result["resource_estimate_status"] == "NOT_EVALUATED"


def test_no_scientific_or_gpu_result_is_present_as_a_number():
    result = _plan()
    assert isinstance(result["input_candidate_uncertainty"], float)
    other_numbers = [
        value for key, value in result.items()
        if key != "input_candidate_uncertainty"
        and isinstance(value, (float, int))
        and not isinstance(value, bool)
    ]
    assert other_numbers == []


def test_output_contains_only_documented_status_and_metadata_fields():
    assert set(_plan()) == {
        "input_candidate_uncertainty",
        "uncertainty_provenance",
        "uncertainty_calibration_status",
        "uncertainty_unit",
        "execution_tier",
        "tier_selection_status",
        "active_engines",
        "model_execution_status",
        "allocated_compute",
        "allocated_gpu_hours",
        "budget_status",
        "compute_reservation_status",
        "resource_estimate_status",
        "reasoning",
    }


def test_reasoning_discloses_missing_runtime_and_calibration_evidence():
    reasoning = _plan()["reasoning"]
    assert "NO COMPUTE WAS ALLOCATED OR EXECUTED" in reasoning
    assert "no verified unit or calibration" in reasoning
    assert "measured" in reasoning
    assert "runtime estimates" in reasoning


def test_reasoning_does_not_assert_model_execution():
    reasoning = _plan()["reasoning"]
    assert "not sufficient to select CHGNet, MACE, M3GNet, DFT" in reasoning
def test_successful_result_is_serializable_and_contains_null_gpu_budget():
    result = _plan()
    parsed = json.loads(json.dumps(result, allow_nan=False))
    assert parsed["allocated_gpu_hours"] is None
    assert parsed["execution_tier"] is None


def test_results_are_fresh_and_do_not_leak_mutations_between_calls():
    first = _plan()
    first["active_engines"].append("pretend-GPU-engine")
    first["budget_status"] = "CHANGED_BY_TEST"
    second = _plan()
    assert second["active_engines"] == []
    assert second["budget_status"] == "NOT_ALLOCATED"


def test_independent_calls_are_deterministic_for_same_input():
    a = _plan(0.0123)
    b = _plan(0.0123)
    assert a == b
    assert a is not b
def test_a_different_input_does_not_change_the_nonexecution_claims():
    low = _plan(0.005)
    high = _plan(9.0)
    assert low["input_candidate_uncertainty"] != high["input_candidate_uncertainty"]
    for result in (low, high):
        assert result["allocated_compute"] is None
        assert result["model_execution_status"] == "NOT_RUN"
        assert result["budget_status"] == "NOT_ALLOCATED"


def test_no_network_request_is_required(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("A budget status reader must not access the network")
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    assert _plan()["compute_reservation_status"] == "NOT_REQUESTED"


def test_missing_uncertainty_fails_explicitly():
    with pytest.raises(TypeError):
        AdaptiveBudgetPlanner.allocate_and_evaluate()


def test_unexpected_keywords_do_not_create_a_compute_job():
    with pytest.raises(TypeError):
        AdaptiveBudgetPlanner.allocate_and_evaluate(0.01, gpu_hours=8.4)


@pytest.mark.parametrize("uncertainty", [
    0,
    -0.0,
    1e-300,
    0.014999,
    0.015,
    0.034999,
    0.035,
    1.0,
    1e308,
])
def test_finite_nonnegative_inputs_never_trigger_unverified_tier(uncertainty):
    result = _plan(uncertainty)
    assert math.isfinite(result["input_candidate_uncertainty"])
    assert result["execution_tier"] is None
    assert result["active_engines"] == []
    assert result["allocated_gpu_hours"] is None
    assert result["model_execution_status"] == "NOT_RUN"


@pytest.mark.parametrize("invalid", [
    None,
    True,
    False,
    -0.001,
    -1.0,
    float("nan"),
    float("inf"),
    -float("inf"),
    "0.01",
    "",
    [],
    {},
    (),
    10**1000,
])

def test_invalid_uncertainty_is_rejected(invalid):
    with pytest.raises(ValueError):
        _plan(invalid)

# END OF COMPLETE BHS LEGACY SEARCH PLANNER SAFETY TESTS — CHECK THIS LINE ON GITHUB
