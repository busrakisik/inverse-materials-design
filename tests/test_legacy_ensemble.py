"""Prevent fictional cross-model validation in the legacy ensemble wrapper.

These tests use a real pymatgen Structure in GitHub CI, but a fake primary
MLFF dependency. No CHGNet weights, second model, GPU job, or physical
benchmark is run. Passing these tests is not evidence of materials stability.
"""

import copy
import json
import socket
import urllib.request

import pytest
from pymatgen.core import Lattice, Structure

from src.imd_pipeline.validation import ensemble_validator as ensemble_module
from src.imd_pipeline.validation.ensemble_validator import MultiMLFFEnsembleValidator


_UNSET = object()


def _structure():
    return Structure(Lattice.cubic(4.0), ["Fe", "O"], [[0, 0, 0], [0.5, 0.5, 0.5]])


def _primary_result(**changes):
    result = {
        "engine": "CHGNet",
        "execution_status": "CHGNET_OPTIMIZER_RETURNED_OUTPUT",
        "model_output_provenance": "MLFF_PREDICTION_NOT_EXPERIMENT",
        "potential_energy_ev_per_atom": -6.0,
        "potential_energy_total_ev": -12.0,
        "e_form": None,
        "formation_energy_ev_per_atom": None,
        "synthesizability_score": None,
        "band_gap_class": None,
        "estimated_gap_eV": None,
        "ensemble_confidence": None,
        "is_ensemble_approved": None,
        "device_requested": "cpu",
        "independent_verification_status": "NOT_VERIFIED",
        "extra_caller_metadata": "preserved",
    }
    result.update(changes)
    return result


def _validator(monkeypatch, *, primary=_UNSET, failure=None, calls=None, use_gpu=False):
    if primary is _UNSET:
        primary = _primary_result()
    if calls is None:
        calls = []

    class FakePrimaryValidator:
        def __init__(self, *, use_gpu):
            calls.append(("init", use_gpu))

        def evaluate_and_relax(self, structure):
            calls.append(("evaluate", structure))
            if failure is not None:
                raise failure
            return primary

    monkeypatch.setattr(ensemble_module, "MLFFValidator", FakePrimaryValidator)
    return MultiMLFFEnsembleValidator(use_gpu=use_gpu), calls


def _evaluate(monkeypatch, *, primary=_UNSET, failure=None, use_gpu=False):
    validator, _ = _validator(
        monkeypatch, primary=primary, failure=failure, use_gpu=use_gpu
    )
    return validator.evaluate_with_ensemble(_structure())


def test_wrapper_instantiates_primary_without_running_optimization(monkeypatch):
    wrapper, calls = _validator(monkeypatch)
    assert isinstance(wrapper, MultiMLFFEnsembleValidator)
    assert calls == [("init", False)]


@pytest.mark.parametrize("flag", [False, True])
def test_cpu_or_cuda_flag_is_forwarded_without_claiming_gpu_execution(monkeypatch, flag):
    wrapper, calls = _validator(monkeypatch, use_gpu=flag)
    assert calls == [("init", flag)]
    result = wrapper.evaluate_with_ensemble(_structure())
    assert result["ensemble_status"] == "NOT_EVALUATED"
    assert "gpu_hours" not in result


def test_primary_is_called_exactly_once(monkeypatch):
    wrapper, calls = _validator(monkeypatch)
    wrapper.evaluate_with_ensemble(_structure())
    assert [name for name, *_ in calls].count("evaluate") == 1


def test_original_structure_is_forwarded_without_regeneration(monkeypatch):
    wrapper, calls = _validator(monkeypatch)
    structure = _structure()
    wrapper.evaluate_with_ensemble(structure)
    assert calls[1][1] is structure


def test_primary_energy_remains_the_reported_model_energy(monkeypatch):
    result = _evaluate(monkeypatch)
    assert result["potential_energy_ev_per_atom"] == pytest.approx(-6.0)
    assert result["potential_energy_total_ev"] == pytest.approx(-12.0)


def test_primary_extra_metadata_is_preserved(monkeypatch):
    assert _evaluate(monkeypatch)["extra_caller_metadata"] == "preserved"


def test_primary_model_is_identified_as_chgnet(monkeypatch):
    result = _evaluate(monkeypatch)
    assert result["primary_model"] == "CHGNet"
    assert result["primary_model_execution_status"] == "CHGNET_OPTIMIZER_RETURNED_OUTPUT"


def test_primary_prediction_does_not_become_experiment(monkeypatch):
    result = _evaluate(monkeypatch)
    assert result["model_output_provenance"] == "MLFF_PREDICTION_NOT_EXPERIMENT"
    assert result["independent_verification_status"] == "NOT_VERIFIED"


def test_no_secondary_models_are_claimed_to_have_run(monkeypatch):
    result = _evaluate(monkeypatch)
    assert result["secondary_models_executed"] == []
    assert result["secondary_model_execution_status"] == "NOT_RUN"


def test_no_cross_model_comparison_claimed(monkeypatch):
    assert _evaluate(monkeypatch)["cross_model_comparison_status"] == "NOT_RUN"


def test_model_disagreement_remains_unknown(monkeypatch):
    assert _evaluate(monkeypatch)["model_disagreement_ev_per_atom"] is None


def test_ensemble_confidence_remains_unknown(monkeypatch):
    assert _evaluate(monkeypatch)["ensemble_confidence"] is None


def test_ensemble_uncertainty_remains_unknown(monkeypatch):
    assert _evaluate(monkeypatch)["ensemble_uncertainty_ev_per_atom"] is None


def test_ensemble_is_not_evaluated(monkeypatch):
    assert _evaluate(monkeypatch)["ensemble_status"] == "NOT_EVALUATED"


def test_ensemble_approval_remains_unknown_not_false_certainty(monkeypatch):
    assert _evaluate(monkeypatch)["is_ensemble_approved"] is None


def test_stability_approval_remains_unevaluated(monkeypatch):
    assert _evaluate(monkeypatch)["stability_approval_status"] == "NOT_EVALUATED"


def test_negative_potential_energy_does_not_prove_stability(monkeypatch):
    result = _evaluate(monkeypatch, primary=_primary_result(potential_energy_ev_per_atom=-100.0))
    assert result["is_ensemble_approved"] is None
    assert result["stability_approval_status"] == "NOT_EVALUATED"


def test_positive_potential_energy_does_not_prove_instability(monkeypatch):
    result = _evaluate(monkeypatch, primary=_primary_result(potential_energy_ev_per_atom=100.0))
    assert result["ensemble_confidence"] is None
    assert result["stability_approval_status"] == "NOT_EVALUATED"


def test_statuses_are_not_numeric_scores(monkeypatch):
    r = _evaluate(monkeypatch)
    for key in ("ensemble_confidence", "ensemble_uncertainty_ev_per_atom",
                "model_disagreement_ev_per_atom", "is_ensemble_approved"):
        assert r[key] is None


def test_no_fake_ensemble_software_name_or_version(monkeypatch):
    result = _evaluate(monkeypatch)
    assert "MACE_version" not in result
    assert "M3GNet_version" not in result
    assert "DFT_energy_ev_per_atom" not in result


def test_interpretation_discloses_missing_secondary_calculations(monkeypatch):
    note = _evaluate(monkeypatch)["scientific_ensemble_interpretation"]
    assert "NO ENSEMBLE COMPARISON PERFORMED" in note
    assert "MACE, M3GNet, or DFT" in note
    assert "no independent" in note


def test_interpretation_does_not_claim_thermal_or_synthesis_success(monkeypatch):
    note = _evaluate(monkeypatch)["scientific_ensemble_interpretation"]
    assert "cannot establish" in note
    assert "synthesis approval" in note


def test_caller_primary_dictionary_is_not_mutated(monkeypatch):
    primary = _primary_result()
    saved = copy.deepcopy(primary)
    output = _evaluate(monkeypatch, primary=primary)
    assert primary == saved
    assert output is not primary
    assert "primary_model" not in primary


def test_fresh_result_cannot_change_original_primary_result(monkeypatch):
    original = _primary_result()
    result = _evaluate(monkeypatch, primary=original)
    result["ensemble_confidence"] = 0.95
    result["secondary_models_executed"].append("fake model")
    assert original["ensemble_confidence"] is None
    assert "secondary_models_executed" not in original


def test_repeated_evaluations_do_not_share_list_instances(monkeypatch):
    primary = _primary_result()
    wrapper, _ = _validator(monkeypatch, primary=primary)
    a = wrapper.evaluate_with_ensemble(_structure())
    b = wrapper.evaluate_with_ensemble(_structure())
    assert a == b
    assert a is not b
    assert a["secondary_models_executed"] is not b["secondary_models_executed"]


def test_existing_false_secondary_execution_claim_is_replaced(monkeypatch):
    primary = _primary_result(secondary_models_executed=["fictional MACE run"])
    out = _evaluate(monkeypatch, primary=primary)
    assert out["secondary_models_executed"] == []
    assert primary["secondary_models_executed"] == ["fictional MACE run"]


def test_existing_false_comparison_metadata_is_replaced(monkeypatch):
    primary = _primary_result(cross_model_comparison_status="PASS",
                              ensemble_status="APPROVED")
    out = _evaluate(monkeypatch, primary=primary)
    assert out["cross_model_comparison_status"] == "NOT_RUN"
    assert out["ensemble_status"] == "NOT_EVALUATED"


def test_primary_failure_propagates_without_fallback(monkeypatch):
    with pytest.raises(RuntimeError, match="CHGNet failed"):
        _evaluate(monkeypatch, failure=RuntimeError("CHGNet failed"))


def test_primary_exception_is_not_recast_as_success(monkeypatch):
    with pytest.raises(ValueError, match="bad model output"):
        _evaluate(monkeypatch, failure=ValueError("bad model output"))


def test_no_network_is_used_by_the_ensemble_wrapper(monkeypatch):
    def forbid(*args, **kwargs):
        raise AssertionError("Network access is not part of the fake primary path")
    monkeypatch.setattr(socket, "create_connection", forbid)
    monkeypatch.setattr(urllib.request, "urlopen", forbid)
    assert _evaluate(monkeypatch)["ensemble_status"] == "NOT_EVALUATED"


def test_status_data_is_json_serializable_without_nan(monkeypatch):
    result = _evaluate(monkeypatch)
    # Excludes Structure, which the actual MLFF primary may return separately.
    json.loads(json.dumps(result, allow_nan=False))


@pytest.mark.parametrize("invalid_structure", [
    None, False, True, 0, 1.5, "FeO", [], {}, (),
])
def test_invalid_structure_is_rejected_before_model_call(monkeypatch, invalid_structure):
    wrapper, calls = _validator(monkeypatch)
    with pytest.raises(ValueError, match="Structure"):
        wrapper.evaluate_with_ensemble(invalid_structure)
    assert calls == [("init", False)]


@pytest.mark.parametrize("invalid_primary", [
    None, [], (), "CHGNet", 123, True, False,
])
def test_invalid_primary_result_rejected(monkeypatch, invalid_primary):
    with pytest.raises(RuntimeError, match="no valid result"):
        _evaluate(monkeypatch, primary=invalid_primary)


@pytest.mark.parametrize("modified", [
    {"engine": "MACE"},
    {"engine": "Quantum ESPRESSO"},
    {"execution_status": "NOT_RUN"},
    {"model_output_provenance": "MEASURED_EXPERIMENT"},
    {"model_output_provenance": "UNVERIFIED"},
    {"execution_status": None},
])
def test_invalid_primary_provenance_rejected(monkeypatch, modified):
    with pytest.raises(RuntimeError, match="verified primary CHGNet"):
        _evaluate(monkeypatch, primary=_primary_result(**modified))


@pytest.mark.parametrize("invalid_energy", [
    None, False, True, float("nan"), float("inf"), -float("inf"),
    "-1.0", "", [], {}, (), 10**1000,
])
def test_invalid_primary_energy_is_rejected(monkeypatch, invalid_energy):
    with pytest.raises(RuntimeError, match="potential energy"):
        _evaluate(
            monkeypatch,
            primary=_primary_result(potential_energy_ev_per_atom=invalid_energy),
        )


@pytest.mark.parametrize("field", [
    "e_form", "formation_energy_ev_per_atom", "synthesizability_score",
    "band_gap_class", "estimated_gap_eV", "ensemble_confidence",
    "is_ensemble_approved",
])
def test_primary_fake_scientific_claim_is_rejected(monkeypatch, field):
    with pytest.raises(RuntimeError, match="unsupported scientific or ensemble"):
        _evaluate(monkeypatch, primary=_primary_result(**{field: 0.75}))

