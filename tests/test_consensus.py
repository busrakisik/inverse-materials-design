# BEGIN OF COMPLETE BHS CONSENSUS SAFETY TESTS — CHECK THIS LINE ON GITHUB
"""Safety and arithmetic tests; no real MLFF/DFT inference is performed."""

import copy
import math

import pytest

from src.imd_pipeline.agents.consensus_engine import MultiModelConsensusEngine


def _record(value, *, model_version="v1", calculation_id="run-A", structure_id="sample-1"):
    return {
        "value_ev_per_atom": value,
        "model_version": model_version,
        "calculation_id": calculation_id,
        "structure_id": structure_id,
    }


def _inputs(a=-6.0, b=-4.0):
    return {"model_predictions": {
        "A": _record(a),
        "B": _record(b, model_version="v2", calculation_id="run-B"),
    }}


def test_two_supplied_energies_produce_only_descriptive_statistics():
    result = MultiModelConsensusEngine.evaluate_ensemble(_inputs())
    assert result["model_count"] == 2
    assert result["arithmetic_mean_of_supplied_values_ev_per_atom"] == pytest.approx(-5.0)
    assert result["population_std_of_supplied_values_ev_per_atom"] == pytest.approx(1.0)
    assert result["range_of_supplied_values_ev_per_atom"] == pytest.approx(2.0)
    assert result["input_values_ev_per_atom"]["A"]["calculation_id"] == "run-A"
    assert result["input_values_ev_per_atom"]["B"]["model_version"] == "v2"


def test_three_supplied_energies_use_population_not_sample_spread():
    payload = _inputs(-3.0, -4.0)
    payload["model_predictions"]["C"] = _record(
        -5.0, model_version="v3", calculation_id="run-C"
    )
    result = MultiModelConsensusEngine.evaluate_ensemble(payload)
    assert result["model_count"] == 3
    assert result["arithmetic_mean_of_supplied_values_ev_per_atom"] == pytest.approx(-4.0)
    assert result["population_std_of_supplied_values_ev_per_atom"] == pytest.approx(
        math.sqrt(2 / 3)
    )
    assert result["range_of_supplied_values_ev_per_atom"] == pytest.approx(2.0)


def test_equal_supplied_energies_have_zero_spread_without_consensus_claim():
    result = MultiModelConsensusEngine.evaluate_ensemble(_inputs(-5.0, -5.0))
    assert result["population_std_of_supplied_values_ev_per_atom"] == 0.0
    assert result["range_of_supplied_values_ev_per_atom"] == 0.0
    assert result["scientific_consensus_score"] is None


def test_callers_input_is_not_mutated():
    payload = _inputs()
    before = copy.deepcopy(payload)
    MultiModelConsensusEngine.evaluate_ensemble(payload)
    assert payload == before


def test_order_does_not_change_arithmetic_summary():
    payload = _inputs()
    original = MultiModelConsensusEngine.evaluate_ensemble(payload)
    payload["model_predictions"] = dict(reversed(list(payload["model_predictions"].items())))
    reversed_result = MultiModelConsensusEngine.evaluate_ensemble(payload)
    for key in (
        "arithmetic_mean_of_supplied_values_ev_per_atom",
        "population_std_of_supplied_values_ev_per_atom",
        "range_of_supplied_values_ev_per_atom",
    ):
        assert reversed_result[key] == pytest.approx(original[key])


def test_all_scientific_validation_fields_remain_unverified():
    result = MultiModelConsensusEngine.evaluate_ensemble(_inputs())
    assert result["formation_energy_ev_per_atom"] is None
    assert result["calibrated_model_uncertainty_ev_per_atom"] is None
    assert result["scientific_consensus_score"] is None
    assert result["independent_execution_verification"] == "NOT_VERIFIED"
    assert result["inter_model_energy_reference_alignment"] == "NOT_VERIFIED"
    assert "No model was executed" in result["scientific_interpretation"]


@pytest.mark.parametrize("invalid", [
    None,
    [],
    {},
    {"model_predictions": None},
    {"model_predictions": []},
    {"model_predictions": {}},
    {"model_predictions": {"A": _record(-5.0)}},
    {"model_predictions": {}, "unverified_extra": True},
])
def test_missing_or_wrong_input_schema_is_rejected(invalid):
    with pytest.raises(ValueError):
        MultiModelConsensusEngine.evaluate_ensemble(invalid)


@pytest.mark.parametrize("bad_value", [
    None, True, "5.0", float("nan"), float("inf"), -float("inf"), 10 ** 1000
])
def test_nonfinite_or_non_numeric_energy_is_rejected(bad_value):
    with pytest.raises(ValueError):
        MultiModelConsensusEngine.evaluate_ensemble(_inputs(a=bad_value))


@pytest.mark.parametrize("field, replacement", [
    ("model_version", ""),
    ("model_version", None),
    ("calculation_id", "   "),
    ("calculation_id", 123),
    ("structure_id", ""),
    ("structure_id", 123),
])
def test_missing_required_metadata_is_rejected(field, replacement):
    payload = _inputs()
    payload["model_predictions"]["A"][field] = replacement
    with pytest.raises(ValueError):
        MultiModelConsensusEngine.evaluate_ensemble(payload)


@pytest.mark.parametrize("change", ["missing_field", "extra_field", "not_a_dict"])
def test_incomplete_or_unexpected_prediction_record_rejected(change):
    payload = _inputs()
    if change == "missing_field":
        del payload["model_predictions"]["A"]["model_version"]
    elif change == "extra_field":
        payload["model_predictions"]["A"]["fake_confidence"] = 0.98
    else:
        payload["model_predictions"]["A"] = None
    with pytest.raises(ValueError):
        MultiModelConsensusEngine.evaluate_ensemble(payload)


@pytest.mark.parametrize("bad_name", ["", "   ", 12])
def test_invalid_model_name_is_rejected(bad_name):
    payload = _inputs()
    payload["model_predictions"][bad_name] = payload["model_predictions"].pop("A")
    with pytest.raises(ValueError):
        MultiModelConsensusEngine.evaluate_ensemble(payload)


def test_duplicate_calculation_ids_rejected():
    payload = _inputs()
    payload["model_predictions"]["B"]["calculation_id"] = "run-A"
    with pytest.raises(ValueError, match="Duplicate calculation_id"):
        MultiModelConsensusEngine.evaluate_ensemble(payload)


def test_different_structure_identifiers_rejected():
    payload = _inputs()
    payload["model_predictions"]["B"]["structure_id"] = "different-sample"
    with pytest.raises(ValueError, match="structure_id"):
        MultiModelConsensusEngine.evaluate_ensemble(payload)


def test_arithmetic_overflow_fails_explicitly_not_with_fabricated_score():
    with pytest.raises(ValueError, match="Energy summary"):
        MultiModelConsensusEngine.evaluate_ensemble(_inputs(1e308, -1e308))

def test_one_model_would_not_count_as_cross_model_consensus():
    with pytest.raises(ValueError, match="At least two"):
        MultiModelConsensusEngine.evaluate_ensemble(
            {"model_predictions": {"A": _record(-5.0)}}
        )

# END OF COMPLETE BHS CONSENSUS SAFETY TESTS — CHECK THIS LINE ON GITHUB
