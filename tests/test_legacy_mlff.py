"""Software correctness at a mocked CHGNet boundary, never a physical study.

CI uses real pymatgen objects but deliberately substitutes a fake CHGNet API.
No actual model weights are loaded and no experimental, DFT or MLFF
benchmark claims may be inferred from passing these tests.
"""

import builtins
import copy
import math
import sys
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest
from pymatgen.core import Lattice, Structure

from src.imd_pipeline.validation.mlff_validator import MLFFValidator


def _structure(n=2, *, species=None):
    if species is None:
        species = ["Fe", "O"][:n]
    coords = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]][:n]
    return Structure(Lattice.cubic(4.0), species, coords)


def _model_result(structure, *, energies=None, forces=None):
    if energies is None:
        energies = [-3.0, -12.0]
    trajectory = SimpleNamespace(energies=energies)
    if forces is not None:
        trajectory.forces = forces
    return {"final_structure": structure, "trajectory": trajectory}


def _fake_chgnet(monkeypatch, *, result=None, failure=None, recorder=None):
    """Install a strictly local fake of the dependency's public API."""
    pkg = ModuleType("chgnet")
    pkg.__path__ = []
    model_pkg = ModuleType("chgnet.model")
    model_pkg.__path__ = []
    dynamics_pkg = ModuleType("chgnet.model.dynamics")

    class FakeOptimizer:
        def __init__(self, *, use_device):
            if recorder is not None:
                recorder.append(("init", use_device))

        def relax(self, structure, *, fmax, steps, relax_cell, verbose):
            if recorder is not None:
                recorder.append(("relax", fmax, steps, relax_cell, verbose))
            if failure is not None:
                raise failure
            return result

    dynamics_pkg.StructOptimizer = FakeOptimizer
    for key, value in (
        ("chgnet", pkg), ("chgnet.model", model_pkg),
        ("chgnet.model.dynamics", dynamics_pkg),
    ):
        monkeypatch.setitem(sys.modules, key, value)


def _run_fake(monkeypatch, *, structure=None, energies=None, forces=None,
              result=None, failure=None, use_gpu=False):
    if structure is None:
        structure = _structure()
    if result is None and failure is None:
        result = _model_result(structure, energies=energies, forces=forces)
    _fake_chgnet(monkeypatch, result=result, failure=failure)
    return MLFFValidator(use_gpu=use_gpu).evaluate_and_relax(structure)


def test_initialization_never_downloads_or_loads_models():
    engine = MLFFValidator()
    assert engine.model is None
    assert engine.optimizer is None
    assert engine.use_gpu is False


def test_gpu_flag_is_stored_without_allocating_a_gpu():
    engine = MLFFValidator(use_gpu=True)
    assert engine.use_gpu is True
    assert engine.model is None


@pytest.mark.parametrize("invalid", [None, 0, 1, "cuda", [], {}])
def test_nonboolean_gpu_flag_rejected(invalid):
    with pytest.raises(ValueError, match="use_gpu"):
        MLFFValidator(use_gpu=invalid)


def test_actual_mocked_total_energy_is_divided_by_atom_count(monkeypatch):
    result = _run_fake(monkeypatch)
    assert result["potential_energy_total_ev"] == pytest.approx(-12.0)
    assert result["potential_energy_ev_per_atom"] == pytest.approx(-6.0)
    assert result["relaxed_structure"] is not None


def test_energy_values_depend_on_given_model_output(monkeypatch):
    result = _run_fake(monkeypatch, energies=[-1.0, -8.0])
    assert result["potential_energy_total_ev"] == pytest.approx(-8.0)
    assert result["potential_energy_ev_per_atom"] == pytest.approx(-4.0)


def test_negative_energy_does_not_imply_stability(monkeypatch):
    result = _run_fake(monkeypatch)
    assert result["converged"] is None
    assert result["has_overlap"] is None
    assert result["independent_verification_status"] == "NOT_VERIFIED"


def test_formation_energy_is_never_synthesized(monkeypatch):
    result = _run_fake(monkeypatch)
    assert result["e_form"] is None
    assert result["formation_energy_ev_per_atom"] is None
    assert result["formation_energy_status"] == "NOT_CALCULATED"


def test_unsupported_properties_are_never_fabricated(monkeypatch):
    result = _run_fake(monkeypatch)
    for key in (
        "band_gap_class", "estimated_gap_eV", "synthesizability_score",
        "max_stress", "stress_tensor", "raw_energy",
    ):
        assert result[key] is None
    assert result["band_gap_status"] == "NOT_CALCULATED"


def test_provenance_explicitly_identifies_model_prediction(monkeypatch):
    result = _run_fake(monkeypatch)
    assert result["engine"] == "CHGNet"
    assert result["model_output_provenance"] == "MLFF_PREDICTION_NOT_EXPERIMENT"
    assert result["execution_status"] == "CHGNET_OPTIMIZER_RETURNED_OUTPUT"
    assert "NOT_VERIFIED" == result["convergence_status"]


def test_scientific_interpretation_does_not_claim_formation_energy(monkeypatch):
    statement = _run_fake(monkeypatch)["scientific_interpretation"]
    assert "No formation energy" in statement
    assert "No" in statement
    assert "empirical" in statement


def test_cpu_device_is_passed_to_optimizer(monkeypatch):
    structure = _structure()
    records = []
    _fake_chgnet(monkeypatch, result=_model_result(structure), recorder=records)
    result = MLFFValidator().evaluate_and_relax(structure)
    assert records[0] == ("init", "cpu")
    assert records[1] == ("relax", 0.1, 100, True, False)
    assert result["device_requested"] == "cpu"


def test_requested_cuda_is_not_claimed_as_verified_gpu_execution(monkeypatch):
    structure = _structure()
    records = []
    _fake_chgnet(monkeypatch, result=_model_result(structure), recorder=records)
    result = MLFFValidator(use_gpu=True).evaluate_and_relax(structure)
    assert records[0] == ("init", "cuda")
    assert result["device_requested"] == "cuda"
    assert "gpu_hours" not in result


def test_caller_fmax_and_steps_are_forwarded(monkeypatch):
    structure = _structure()
    records = []
    _fake_chgnet(monkeypatch, result=_model_result(structure), recorder=records)
    MLFFValidator().evaluate_and_relax(structure, fmax=0.03, steps=250)
    assert records[1] == ("relax", 0.03, 250, True, False)


def test_missing_force_trajectory_remains_unknown(monkeypatch):
    result = _run_fake(monkeypatch)
    assert result["forces"] is None
    assert result["max_force"] is None


def test_final_force_vectors_are_used_only_when_supplied(monkeypatch):
    force_history = [
        np.zeros((2, 3)),
        np.array([[3.0, 4.0, 0.0], [0.0, 0.0, 1.0]]),
    ]
    result = _run_fake(monkeypatch, forces=force_history)
    assert result["max_force"] == pytest.approx(5.0)
    assert result["forces"] == force_history[-1].tolist()


def test_periodic_distance_is_a_geometric_observation_only():
    d = MLFFValidator._compute_minimum_interatomic_distance(_structure())
    assert d == pytest.approx(math.sqrt(3) * 2)


def test_single_site_has_no_distinct_pair_distance():
    assert MLFFValidator._compute_minimum_interatomic_distance(_structure(1)) is None


@pytest.mark.parametrize("invalid", [None, 123, "structure", {}])
def test_bad_structure_rejected_before_model_import(invalid):
    with pytest.raises(ValueError, match="Structure"):
        MLFFValidator().evaluate_and_relax(invalid)


@pytest.mark.parametrize("invalid", [None, False, True, 0, -0.01, float("nan"),
                                       float("inf"), -float("inf"), "0.1", [], 10**1000])
def test_invalid_force_tolerance_is_rejected(invalid):
    with pytest.raises(ValueError, match="fmax"):
        MLFFValidator().evaluate_and_relax(_structure(), fmax=invalid)


@pytest.mark.parametrize("invalid", [None, False, True, 0, -1, 1.5, "100", []])
def test_invalid_steps_is_rejected(invalid):
    with pytest.raises(ValueError, match="steps"):
        MLFFValidator().evaluate_and_relax(_structure(), steps=invalid)


def test_missing_chgnet_cannot_trigger_fake_fallback(monkeypatch):
    original_import = builtins.__import__

    def fail_chgnet(name, *args, **kwargs):
        if name == "chgnet.model.dynamics":
            raise ImportError("CHGNet intentionally unavailable")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_chgnet)
    with pytest.raises(RuntimeError, match="No fallback energy"):
        MLFFValidator().evaluate_and_relax(_structure())


def test_old_fallback_method_explicitly_fails():
    with pytest.raises(RuntimeError, match="Synthetic MLFF fallback disabled"):
        MLFFValidator._fallback_physics_evaluation(_structure())


def test_unjustified_formation_energy_method_explicitly_fails():
    with pytest.raises(NotImplementedError, match="Formation energy requires"):
        MLFFValidator._calculate_dynamic_e_form(_structure(), -3.0)


def test_optimizer_exception_cannot_be_swallowed_into_fake_energy(monkeypatch):
    with pytest.raises(RuntimeError, match="No placeholder energy"):
        _run_fake(monkeypatch, failure=RuntimeError("relaxation failed"))


def test_no_final_structure_is_rejected(monkeypatch):
    with pytest.raises(RuntimeError, match="invalid outputs"):
        _run_fake(monkeypatch, result={"trajectory": SimpleNamespace(energies=[-12.0])})


def test_no_trajectory_is_rejected(monkeypatch):
    with pytest.raises(RuntimeError, match="invalid outputs"):
        _run_fake(monkeypatch, result={"final_structure": _structure()})


def test_no_energies_are_rejected(monkeypatch):
    with pytest.raises(RuntimeError, match="invalid outputs"):
        _run_fake(monkeypatch, result=_model_result(_structure(), energies=[]))


@pytest.mark.parametrize("invalid_energy", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_model_energy_is_rejected(monkeypatch, invalid_energy):
    with pytest.raises(RuntimeError, match="No placeholder energy"):
        _run_fake(monkeypatch, energies=[invalid_energy])


@pytest.mark.parametrize("invalid_forces", [
    [], [np.ones((2, 2))], [np.full((2, 3), float("nan"))],
    [np.full((2, 3), float("inf"))],
])
def test_missing_or_malformed_force_vectors_are_rejected(monkeypatch, invalid_forces):
    with pytest.raises(RuntimeError, match="invalid outputs"):
        _run_fake(monkeypatch, forces=invalid_forces)


def test_changed_atom_count_is_rejected(monkeypatch):
    with pytest.raises(RuntimeError, match="invalid outputs"):
        _run_fake(monkeypatch, result=_model_result(_structure(1)))


def test_changed_composition_is_rejected(monkeypatch):
    changed = _structure(2, species=["Fe", "Fe"])
    with pytest.raises(RuntimeError, match="invalid outputs"):
        _run_fake(monkeypatch, result=_model_result(changed))


def test_output_is_not_a_fake_ensemble(monkeypatch):
    result = _run_fake(monkeypatch)
    assert "ensemble_confidence" not in result
    assert "is_ensemble_approved" not in result
    assert "model_disagreement" not in result


def test_energy_was_not_assigned_a_fake_model_version(monkeypatch):
    result = _run_fake(monkeypatch)
    assert "model_version" not in result
    assert "calibrated_uncertainty" not in result

