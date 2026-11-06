"""Check structural scoring with pymatgen; NOT scientific calibration."""

import math
import pytest
from pymatgen.core import Lattice, Structure
from bhs.evidence.likelihoods import LikelihoodEngine
from bhs.provenance.tags import DataProvenanceType


def test_spacious_crystal_has_no_periodic_overlap():
    crystal = Structure(Lattice.cubic(5.0), ["Li"], [[0, 0, 0]])
    result = LikelihoodEngine.calculate_wyckoff_clash_likelihood(crystal)
    assert result.value == pytest.approx(1.0)
    assert result.provenance == DataProvenanceType.DERIVED
    assert "UNCALIBRATED" in result.source_description
    assert result.uncertainty is None


def test_periodic_boundary_neighbors_are_counted_once():
    crystal = Structure(Lattice.cubic(4.0), ["Li", "Li"],
                        [[0.05, 0, 0], [0.95, 0, 0]])
    radius = float(crystal[0].specie.atomic_radius)
    threshold = 0.75 * (2 * radius)
    expected = math.exp(-10.0 * (1.0 - 0.4 / threshold) ** 2)
    result = LikelihoodEngine.calculate_wyckoff_clash_likelihood(crystal)
    assert result.value == pytest.approx(expected, rel=1e-7)
    assert 0.0 < result.value < 1.0


def test_self_images_in_tiny_periodic_cell_are_detected():
    crystal = Structure(Lattice.cubic(1.0), ["Li"], [[0, 0, 0]])
    result = LikelihoodEngine.calculate_wyckoff_clash_likelihood(crystal)
    assert 0.0 <= result.value < 1.0


def test_zero_clash_penalty_multiplier_returns_one():
    crystal = Structure(Lattice.cubic(1.0), ["Li"], [[0, 0, 0]])
    result = LikelihoodEngine.calculate_wyckoff_clash_likelihood(
        crystal, lambda_clash=0.0)
    assert result.value == pytest.approx(1.0)


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), True, "1"])
def test_invalid_eta_rejected(bad):
    crystal = Structure(Lattice.cubic(5.0), ["Li"], [[0, 0, 0]])
    with pytest.raises(ValueError, match="eta"):
        LikelihoodEngine.calculate_wyckoff_clash_likelihood(crystal, eta=bad)


@pytest.mark.parametrize("bad", [-1, float("nan"), float("inf"), True, "10"])
def test_invalid_clash_coefficient_rejected(bad):
    crystal = Structure(Lattice.cubic(5.0), ["Li"], [[0, 0, 0]])
    with pytest.raises(ValueError, match="lambda_clash"):
        LikelihoodEngine.calculate_wyckoff_clash_likelihood(crystal, lambda_clash=bad)


def test_structure_must_be_real_nonempty_pymatgen_structure():
    with pytest.raises(ValueError, match="nonempty pymatgen Structure"):
        LikelihoodEngine.calculate_wyckoff_clash_likelihood(None)


def test_soap_distance_is_only_transformed_not_calculated():
    result = LikelihoodEngine.calculate_soap_novelty_likelihood(0.42, delta=0.5)
    assert result.value == pytest.approx(1 - math.exp(-0.42 / 0.5))
    assert result.provenance == DataProvenanceType.DERIVED
    assert "UNCALIBRATED" in result.source_description
    assert "NOT verified" in result.source_description
    assert result.uncertainty is None


def test_zero_soap_distance_returns_zero_score():
    assert LikelihoodEngine.calculate_soap_novelty_likelihood(0).value == 0.0


@pytest.mark.parametrize("bad", [-0.1, float("nan"), float("inf"), True, "0.5"])
def test_invalid_soap_distance_rejected(bad):
    with pytest.raises(ValueError, match="soap_distance"):
        LikelihoodEngine.calculate_soap_novelty_likelihood(bad)


@pytest.mark.parametrize("bad", [0, -0.5, float("nan"), float("inf"), True, "0.5"])
def test_invalid_soap_scale_rejected(bad):
    with pytest.raises(ValueError, match="delta"):
        LikelihoodEngine.calculate_soap_novelty_likelihood(0.2, delta=bad)

