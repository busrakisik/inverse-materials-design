"""Test CHGNet adapter behavior using a mocked optimizer, not a physics run.

Real pymatgen Structure objects are used in CI. No CHGNet model, GPU,
relaxation benchmark, stability inference, or material discovery is executed.
"""

import builtins
import sys
from types import ModuleType, SimpleNamespace

import pytest
from pymatgen.core import Lattice, Structure

from bhs.physics.relaxer import PhysicsRelaxationEngine
from bhs.provenance.tags import DataProvenanceType


def _install_fake_chgnet(monkeypatch, *, result=None, failure=None):
    """Replace only the CHGNet API boundary, never the physics result with a claim."""
    package = ModuleType("chgnet")
    package.__path__ = []
    model = ModuleType("chgnet.model")
    model.__path__ = []
    dynamics = ModuleType("chgnet.model.dynamics")

    class FakeOptimizer:
        def relax(self, structure, *, fmax):
            assert fmax == pytest.approx(0.05)
            if failure is not None:
                raise failure
            return result

    dynamics.StructOptimizer = FakeOptimizer
    for name, module in (("chgnet", package), ("chgnet.model", model),
                         ("chgnet.model.dynamics", dynamics)):
        monkeypatch.setitem(sys.modules, name, module)


def _example_structure(n=2):
    positions = [[0, 0, 0], [0.5, 0.5, 0.5]][:n]
    return Structure(Lattice.cubic(4.0), ["Fe"] * n, positions)


def test_total_model_energy_divided_by_actual_atom_count(monkeypatch):
    structure = _example_structure(2)
    result = {"final_structure": structure,
              "trajectory": SimpleNamespace(energies=[-5.0, -12.0])}
    _install_fake_chgnet(monkeypatch, result=result)
    relaxed, metrics = PhysicsRelaxationEngine.run_chgnet_relaxation(structure)
    assert relaxed is structure
    assert metrics["potential_energy_per_atom"].value == pytest.approx(-6.0)
    assert metrics["potential_energy_per_atom"].provenance == DataProvenanceType.DERIVED
    assert "NOT formation energy" in metrics["potential_energy_per_atom"].source_description
    assert metrics["atom_count"].value == 2
    assert "formation_energy" not in metrics
    assert "energy_above_hull" not in metrics


def test_wall_clock_time_is_measurement_not_estimated_gpu_cost(monkeypatch):
    from bhs.physics import relaxer
    structure = _example_structure(1)
    _install_fake_chgnet(monkeypatch, result={"final_structure": structure,
                            "trajectory": SimpleNamespace(energies=[-7.0])})
    clock = iter([100.0, 100.25])
    monkeypatch.setattr(relaxer.time, "perf_counter", lambda: next(clock))
    _, metrics = PhysicsRelaxationEngine.run_chgnet_relaxation(structure)
    assert metrics["relaxation_time"].value == pytest.approx(0.25)
    assert metrics["relaxation_time"].provenance == DataProvenanceType.MEASURED
    assert "gpu_hours_used" not in metrics


def test_missing_chgnet_fails_explicitly(monkeypatch):
    original_import = builtins.__import__

    def block_chgnet(name, *args, **kwargs):
        if name == "chgnet.model.dynamics":
            raise ImportError("CHGNet deliberately absent for this test")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", block_chgnet)
    with pytest.raises(RuntimeError, match="CHGNet is not installed"):
        PhysicsRelaxationEngine.run_chgnet_relaxation(_example_structure(1))


def test_optimizer_failure_does_not_create_placeholder_energy(monkeypatch):
    _install_fake_chgnet(monkeypatch, failure=RuntimeError("optimizer failed"))
    with pytest.raises(RuntimeError, match="No placeholder energy"):
        PhysicsRelaxationEngine.run_chgnet_relaxation(_example_structure(1))


@pytest.mark.parametrize("bad_energy", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_chgnet_energy_rejected(monkeypatch, bad_energy):
    structure = _example_structure(1)
    _install_fake_chgnet(monkeypatch, result={"final_structure": structure,
                            "trajectory": SimpleNamespace(energies=[bad_energy])})
    with pytest.raises(RuntimeError, match="invalid outputs"):
        PhysicsRelaxationEngine.run_chgnet_relaxation(structure)


@pytest.mark.parametrize("bad_result", [
    {},
    {"final_structure": None},
    {"trajectory": SimpleNamespace(energies=[-2.0])},
    {"trajectory": SimpleNamespace(energies=[]), "final_structure": None},
])
def test_incomplete_chgnet_result_rejected(monkeypatch, bad_result):
    _install_fake_chgnet(monkeypatch, result=bad_result)
    with pytest.raises(RuntimeError, match="invalid outputs"):
        PhysicsRelaxationEngine.run_chgnet_relaxation(_example_structure(1))

