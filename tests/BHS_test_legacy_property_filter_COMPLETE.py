# BEGIN OF COMPLETE BHS LEGACY PROPERTY FILTER SAFETY TESTS — CHECK THIS LINE ON GITHUB
"""Safety checks for legacy material-property reporting, NOT property prediction.

These tests use real pymatgen structures in GitHub Actions. No electronic-
structure calculation, experimental measurement, synthesis experiment, or
MLFF/DFT benchmark is performed by this test suite.
"""

import json
import math
import socket
import urllib.request

import pytest
from pymatgen.core import Lattice, Structure

from src.imd_pipeline.validation.property_filter import PropertyFilter


def _structure(species=None, coords=None):
    if species is None:
        species = ["Fe", "O"]
    if coords is None:
        coords = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]]
    return Structure(Lattice.cubic(4.0), species, coords)


def _single_site():
    return _structure(["Li"], [[0.0, 0.0, 0.0]])


def test_synthesis_assessment_is_not_evaluated():
    r = PropertyFilter.assess_synthesizability(_structure())
    assert r["synthesizability_status"] == "NOT_EVALUATED"
    assert r["synthesizability_score"] is None


def test_synthesis_experiment_is_not_claimed():
    assert PropertyFilter.assess_synthesizability(_structure())[
        "synthesis_experiment_status"] == "NOT_RUN"


def test_synthesis_calibration_not_fabricated():
    assert PropertyFilter.assess_synthesizability(_structure())[
        "calibrated_prediction_status"] == "NOT_AVAILABLE"


def test_synthesis_assessment_expected_metadata_only():
    assert set(PropertyFilter.assess_synthesizability(_structure())) == {
        "synthesizability_score", "synthesizability_status",
        "synthesis_experiment_status", "calibrated_prediction_status",
        "scientific_interpretation",
    }


def test_synthesis_interpretation_reports_missing_evidence():
    note = PropertyFilter.assess_synthesizability(_structure())[
        "scientific_interpretation"]
    assert "NO SYNTHESIZABILITY ASSESSMENT PERFORMED" in note
    assert "No validated" in note
    assert "experimental evidence" in note


def test_legacy_synthesis_estimate_returns_unknown_not_zero():
    assert PropertyFilter.estimate_synthesizability(_structure()) is None


def test_one_site_does_not_create_synthesis_probability():
    assert PropertyFilter.estimate_synthesizability(_single_site()) is None


def test_element_identity_cannot_manufacture_synthesis_score():
    for s in (_single_site(), _structure(),
              _structure(["Li", "F"], [[0, 0, 0], [0.4, 0.4, 0.4]])):
        assert PropertyFilter.estimate_synthesizability(s) is None


def test_very_close_atoms_do_not_manufacture_synthesis_score():
    s = _structure(["Fe", "O"], [[0, 0, 0], [0.0001, 0, 0]])
    assert PropertyFilter.estimate_synthesizability(s) is None


def test_synthesis_result_repeatable_and_not_shared():
    a = PropertyFilter.assess_synthesizability(_structure())
    b = PropertyFilter.assess_synthesizability(_structure())
    assert a == b
    assert a is not b


def test_changing_previous_synthesis_result_does_not_leak():
    a = PropertyFilter.assess_synthesizability(_structure())
    a["synthesizability_score"] = 0.99
    b = PropertyFilter.assess_synthesizability(_structure())
    assert b["synthesizability_score"] is None


def test_classify_band_gap_without_eform_returns_null():
    r = PropertyFilter.classify_band_gap(_structure())
    assert r["band_gap_class"] is None
    assert r["estimated_gap_eV"] is None


def test_band_gap_status_is_not_calculated():
    assert PropertyFilter.classify_band_gap(_structure())[
        "band_gap_status"] == "NOT_CALCULATED"


def test_electronic_structure_calculation_not_claimed():
    r = PropertyFilter.classify_band_gap(_structure())
    assert r["electronic_structure_method"] is None
    assert r["electronic_structure_calculation_status"] == "NOT_RUN"


def test_band_gap_uncertainty_not_fabricated():
    assert PropertyFilter.classify_band_gap(_structure())[
        "band_gap_uncertainty_eV"] is None


def test_not_provided_formation_energy_label():
    assert PropertyFilter.classify_band_gap(_structure())[
        "input_e_form_provenance"] == "NOT_PROVIDED"


def test_provided_formation_energy_is_not_verified():
    r = PropertyFilter.classify_band_gap(_structure(), -2.0)
    assert r["input_e_form_provenance"] == "CALLER_SUPPLIED_NOT_VERIFIED"


def test_formation_energy_does_not_drive_band_gap():
    for e in (-10.0, -2.0, 0.0, 10.0):
        r = PropertyFilter.classify_band_gap(_structure(), e)
        assert r["input_e_form_used_for_gap_prediction"] is False
        assert r["band_gap_class"] is None
        assert r["estimated_gap_eV"] is None


def test_band_gap_interpretation_discloses_missing_calculation():
    note = PropertyFilter.classify_band_gap(_structure())[
        "scientific_interpretation"]
    assert "NO BAND-GAP CALCULATION PERFORMED" in note
    assert "traceable measurement" in note
    assert "metallic character" in note


def test_band_gap_output_schema_explicit():
    assert set(PropertyFilter.classify_band_gap(_structure())) == {
        "band_gap_class", "estimated_gap_eV", "band_gap_status",
        "electronic_structure_method",
        "electronic_structure_calculation_status", "band_gap_uncertainty_eV",
        "input_e_form_provenance", "input_e_form_used_for_gap_prediction",
        "scientific_interpretation",
    }


def test_single_site_has_no_invented_band_gap():
    r = PropertyFilter.classify_band_gap(_single_site())
    assert r["estimated_gap_eV"] is None
    assert r["band_gap_class"] is None


def test_metal_composition_not_auto_labeled_metallic():
    r = PropertyFilter.classify_band_gap(_single_site())
    assert r["band_gap_class"] is None
    assert r["estimated_gap_eV"] is None


def test_oxide_composition_not_auto_labeled_semiconductor():
    r = PropertyFilter.classify_band_gap(_structure())
    assert r["band_gap_class"] is None
    assert r["estimated_gap_eV"] is None


def test_synthesis_and_gap_results_are_json_serializable_without_nan():
    both = {
        "synthesis": PropertyFilter.assess_synthesizability(_structure()),
        "gap": PropertyFilter.classify_band_gap(_structure()),
    }
    recovered = json.loads(json.dumps(both, allow_nan=False))
    assert recovered["synthesis"]["synthesizability_score"] is None
    assert recovered["gap"]["estimated_gap_eV"] is None


def test_band_gap_results_repeatable_without_sharing_dictionary():
    a = PropertyFilter.classify_band_gap(_structure(), -1.0)
    b = PropertyFilter.classify_band_gap(_structure(), -1.0)
    assert a == b
    assert a is not b


def test_changing_previous_gap_result_does_not_leak():
    a = PropertyFilter.classify_band_gap(_structure())
    a["estimated_gap_eV"] = 1.8
    b = PropertyFilter.classify_band_gap(_structure())
    assert b["estimated_gap_eV"] is None


def test_network_is_not_accessed_for_property_estimation(monkeypatch):
    def block(*args, **kwargs):
        raise AssertionError("No network or model call should occur")
    monkeypatch.setattr(socket, "create_connection", block)
    monkeypatch.setattr(urllib.request, "urlopen", block)
    s = _structure()
    assert PropertyFilter.estimate_synthesizability(s) is None
    assert PropertyFilter.classify_band_gap(s)["estimated_gap_eV"] is None


@pytest.mark.parametrize("valid_eform", [
    0, -0.0, -1.8, 1.8, 10.0, -1e300, 1e300,
])
def test_finite_eform_never_becomes_band_gap(valid_eform):
    result = PropertyFilter.classify_band_gap(_structure(), valid_eform)
    assert result["band_gap_status"] == "NOT_CALCULATED"
    assert result["estimated_gap_eV"] is None
    assert result["band_gap_class"] is None
    assert result["input_e_form_provenance"] == "CALLER_SUPPLIED_NOT_VERIFIED"


@pytest.mark.parametrize("invalid_eform", [
    True, False, "1.8", "", [], {}, (),
    float("nan"), float("inf"), -float("inf"), 10**1000,
])
def test_invalid_eform_fails_closed(invalid_eform):
    with pytest.raises(ValueError, match="e_form"):
        PropertyFilter.classify_band_gap(_structure(), invalid_eform)


@pytest.mark.parametrize("invalid_structure", [
    None, False, 0, 0.0, "FeO", [], {}, (),
])
def test_invalid_structure_is_rejected_by_synthesis_and_gap_methods(invalid_structure):
    with pytest.raises(ValueError, match="Structure"):
        PropertyFilter.assess_synthesizability(invalid_structure)
    with pytest.raises(ValueError, match="Structure"):
        PropertyFilter.estimate_synthesizability(invalid_structure)
    with pytest.raises(ValueError, match="Structure"):
        PropertyFilter.classify_band_gap(invalid_structure)

# END OF COMPLETE BHS LEGACY PROPERTY FILTER SAFETY TESTS — CHECK THIS LINE ON GITHUB
