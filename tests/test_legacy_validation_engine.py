"""Geometry screening and optional-CHGNet software safety, not materials research.

The CI suite uses real pymatgen objects and a mocked primary MLFF adapter.
No DFT, trained CHGNet model, experimental measurement, relaxation benchmark,
or independently verified thermodynamic stability is tested here.
"""

import json
import math
import socket
import urllib.request

import pytest
from pymatgen.core import Lattice, Structure

from src.imd_pipeline.validation import validation_engine as validation_module
from src.imd_pipeline.validation.validation_engine import (
    ValidationEngine,
    ValidationFinding,
)


def _structure(distance=2.0):
    """Two distinct sites along x, with a transparent periodic separation."""
    return Structure(
        Lattice.cubic(4.0),
        ["Fe", "O"],
        [[0.0, 0.0, 0.0], [distance / 4.0, 0.0, 0.0]],
    )


def _one_site():
    return Structure(Lattice.cubic(4.0), ["Li"], [[0.0, 0.0, 0.0]])


def _primary_result(**changes):
    result = {
        "engine": "CHGNet",
        "execution_status": "CHGNET_OPTIMIZER_RETURNED_OUTPUT",
        "model_output_provenance": "MLFF_PREDICTION_NOT_EXPERIMENT",
        "potential_energy_ev_per_atom": -5.5,
        "e_form": None,
        "formation_energy_ev_per_atom": None,
        "synthesizability_score": None,
        "band_gap_class": None,
        "estimated_gap_eV": None,
        "converged": None,
        "relaxed_structure": None,
    }
    result.update(changes)
    return result


_UNSET = object()


def _install_fake(monkeypatch, *, result=_UNSET, failure=None, records=None):
    """Replace the MLFF boundary; do not load any model weights or network."""
    if records is None:
        records = []
    if result is _UNSET:
        result = _primary_result()

    class FakeMLFF:
        def __init__(self):
            records.append("init")

        def evaluate_and_relax(self, structure):
            records.append(("evaluate", structure))
            if failure is not None:
                raise failure
            return result

    monkeypatch.setattr(validation_module, "MLFFValidator", FakeMLFF)
    return records


def _run_model(monkeypatch, *, result=_UNSET, failure=None, threshold=0.35,
               structure=None):
    _install_fake(monkeypatch, result=result, failure=failure)
    engine = ValidationEngine(use_mlff=True, e_form_threshold=threshold)
    return engine.run_all(_structure() if structure is None else structure)


def test_finding_retains_legacy_fields():
    f = ValidationFinding("validator", "INFO", "message", {"a": 2})
    assert (f.validator, f.severity, f.message, f.details) == (
        "validator", "INFO", "message", {"a": 2}
    )


def test_finding_defaults_to_independent_empty_details():
    a = ValidationFinding("a", "INFO", "a")
    b = ValidationFinding("b", "INFO", "b")
    a.details["x"] = 1
    assert b.details == {}


def test_disabled_engine_has_no_primary_validator():
    engine = ValidationEngine(use_mlff=False)
    assert engine.mlff_validator is None
    assert engine._chgnet_model is None


def test_enabled_engine_constructs_adapter_but_no_run(monkeypatch):
    records = _install_fake(monkeypatch)
    engine = ValidationEngine(use_mlff=True)
    assert engine.mlff_validator is not None
    assert engine._chgnet_model is None
    assert records == ["init"]


def test_engine_default_requests_mlff(monkeypatch):
    records = _install_fake(monkeypatch)
    engine = ValidationEngine()
    assert engine.use_mlff is True
    assert records == ["init"]


def test_legacy_threshold_is_stored_but_not_claimed_as_stability_rule():
    engine = ValidationEngine(use_mlff=False, e_form_threshold=-3.5)
    assert engine.e_form_threshold == -3.5


@pytest.mark.parametrize("invalid", [None, 0, 1, "yes", [], {}, 0.0])
def test_nonboolean_use_mlff_flag_rejected(invalid):
    with pytest.raises(ValueError, match="use_mlff"):
        ValidationEngine(use_mlff=invalid)


@pytest.mark.parametrize("invalid", [
    None, True, False, [], {}, "0.35", "", float("nan"),
    float("inf"), -float("inf"), 10 ** 1000,
])
def test_invalid_formation_energy_threshold_rejected(invalid):
    with pytest.raises(ValueError, match="e_form_threshold"):
        ValidationEngine(use_mlff=False, e_form_threshold=invalid)


@pytest.mark.parametrize("valid", [-1000.0, -1.0, -0.0, 0, 0.35, 100.0])
def test_finite_legacy_threshold_accepted_but_not_used_for_approval(valid):
    findings = ValidationEngine(use_mlff=False, e_form_threshold=valid).run_all(
        _structure()
    )
    assert findings[1].details["e_form_threshold_application"] == "NOT_APPLIED"
    assert findings[1].details["stability_status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("invalid", [None, False, True, 0, 1.5, "FeO", [], {}, ()])
def test_invalid_structures_rejected_before_geometry_and_mlff(invalid):
    with pytest.raises(ValueError, match="Structure"):
        ValidationEngine(use_mlff=False).run_all(invalid)


def test_geometry_normal_pair_reports_measured_distance():
    geometry = ValidationEngine(use_mlff=False).run_all(_structure())[0]
    assert geometry.validator == "GeometricDistanceScreen"
    assert geometry.severity == "INFO"
    assert geometry.details["minimum_pair_distance_angstrom"] == pytest.approx(2.0)


def test_geometry_without_short_pairs_does_not_claim_stability():
    result = ValidationEngine(use_mlff=False).run_all(_structure())[0]
    assert result.details["screening_status"] == "NO_SHORT_PAIRS_AT_CUTOFF"
    assert result.details["short_pairs"] == []
    assert result.details["physical_stability_status"] == "NOT_EVALUATED"


def test_geometry_screening_is_distinct_site_periodic_heuristic():
    result = ValidationEngine(use_mlff=False).run_all(_structure())[0]
    assert result.details["screening_method"] == "DISTINCT_SITE_PBC_DISTANCE_HEURISTIC"
    assert result.details["cutoff_angstrom"] == pytest.approx(1.1)
    assert result.details["structure_provenance"] == "CALLER_SUPPLIED_NOT_VERIFIED"


def test_short_pair_is_flagged_for_review_not_rejected_as_unstable():
    geometry = ValidationEngine(use_mlff=False).run_all(_structure(0.5))[0]
    assert geometry.severity == "REVIEW"
    assert geometry.details["screening_status"] == "REVIEW"
    assert geometry.details["physical_stability_status"] == "NOT_EVALUATED"


def test_short_pair_has_site_indices_and_distance():
    geometry = ValidationEngine(use_mlff=False).run_all(_structure(0.5))[0]
    assert len(geometry.details["short_pairs"]) == 1
    pair = geometry.details["short_pairs"][0]
    assert pair["site_indices"] == [0, 1]
    assert pair["distance_angstrom"] == pytest.approx(0.5)
    assert len(pair["species"]) == 2


@pytest.mark.parametrize("distance,expected", [
    (0.01, "REVIEW"), (0.5, "REVIEW"), (1.099, "REVIEW"),
    (1.1001, "INFO"), (1.11, "INFO"), (1.75, "INFO"),
])
def test_geometry_cutoff_is_a_declared_heuristic(distance, expected):
    result = ValidationEngine(use_mlff=False).run_all(_structure(distance))[0]
    assert result.severity == expected
    assert result.details["physical_stability_status"] == "NOT_EVALUATED"


def test_single_site_has_no_distinct_site_pair():
    geometry = ValidationEngine(use_mlff=False).run_all(_one_site())[0]
    assert geometry.details["minimum_pair_distance_angstrom"] is None
    assert geometry.details["short_pairs"] == []
    assert geometry.severity == "INFO"


def test_structure_is_not_modified_by_geometry_check():
    structure = _structure(0.5)
    copy = structure.copy()
    ValidationEngine(use_mlff=False).run_all(structure)
    assert structure == copy


def test_geometry_contains_no_invented_energy_or_convergence_claim():
    result = ValidationEngine(use_mlff=False).run_all(_structure(0.5))[0]
    for key in ("e_form", "potential_energy_ev_per_atom", "forces_zeroed", "converged"):
        assert key not in result.details


def test_disabled_mlff_does_not_invoke_any_adapter(monkeypatch):
    records = _install_fake(monkeypatch)
    result = ValidationEngine(use_mlff=False).run_all(_structure())
    assert records == []
    assert result[1].severity == "NOT_RUN"


def test_disabled_mlff_returns_no_fake_energy():
    result = ValidationEngine(use_mlff=False).run_all(_structure())[1]
    assert result.details["potential_energy_ev_per_atom"] is None
    assert result.details["e_form"] is None
    assert result.details["formation_energy_status"] == "NOT_CALCULATED"


def test_disabled_mlff_no_relaxation_or_zero_force_claim():
    result = ValidationEngine(use_mlff=False).run_all(_structure())[1]
    assert result.details["execution_status"] == "NOT_RUN"
    assert result.details["forces_zeroed"] is None
    assert result.details["convergence_status"] == "NOT_VERIFIED"
    assert result.details["stability_status"] == "NOT_EVALUATED"


def test_disabled_mlff_returns_exactly_geometry_and_mlff_status():
    result = ValidationEngine(use_mlff=False).run_all(_structure())
    assert len(result) == 2
    assert [f.validator for f in result] == ["GeometricDistanceScreen", "MLFFValidator"]


def test_primary_model_called_once_on_original_structure(monkeypatch):
    records = _install_fake(monkeypatch)
    engine = ValidationEngine(use_mlff=True)
    structure = _structure()
    engine.run_all(structure)
    assert records[0] == "init"
    assert records[1][0] == "evaluate"
    assert records[1][1] is structure
    assert len(records) == 2


def test_primary_failure_returns_explicit_error_not_fake_energy(monkeypatch):
    result = _run_model(monkeypatch, failure=RuntimeError("CHGNet missing"))
    assert result[1].severity == "ERROR"
    assert result[1].details["execution_status"] == "FAILED"
    assert result[1].details["potential_energy_ev_per_atom"] is None
    assert result[1].details["e_form"] is None


@pytest.mark.parametrize("error", [
    ImportError("CHGNet absent"), OSError("weights absent"),
    ValueError("prediction malformed"), RuntimeError("device unavailable"),
])
def test_primary_exceptions_are_disclosed_without_fallback(monkeypatch, error):
    output = _run_model(monkeypatch, failure=error)[1]
    assert output.severity == "ERROR"
    assert output.details["error_type"] == type(error).__name__
    assert output.details["forces_zeroed"] is None
    assert output.details["stability_status"] == "NOT_EVALUATED"
    assert output.details["e_form_threshold_application"] == "NOT_APPLIED"


def test_primary_failure_preserves_geometry_review_finding(monkeypatch):
    output = _run_model(
        monkeypatch, failure=RuntimeError("offline"), structure=_structure(0.5)
    )
    assert output[0].severity == "REVIEW"
    assert output[1].severity == "ERROR"


def test_primary_failure_does_not_claim_convergence(monkeypatch):
    output = _run_model(monkeypatch, failure=RuntimeError("offline"))[1]
    assert output.details["convergence_status"] == "NOT_VERIFIED"
    assert output.details["formation_energy_status"] == "NOT_CALCULATED"


def test_valid_primary_reports_actual_model_potential_energy(monkeypatch):
    result = _run_model(monkeypatch, result=_primary_result())[1]
    assert result.severity == "INFO"
    assert result.details["potential_energy_ev_per_atom"] == pytest.approx(-5.5)
    assert result.details["execution_status"] == "CHGNET_OPTIMIZER_RETURNED_OUTPUT"


def test_valid_primary_discloses_prediction_not_experiment(monkeypatch):
    output = _run_model(monkeypatch)[1]
    assert output.details["model_output_provenance"] == "MLFF_PREDICTION_NOT_EXPERIMENT"
    assert "model-predicted" in output.message


def test_valid_primary_does_not_infer_formation_energy(monkeypatch):
    output = _run_model(monkeypatch)[1]
    assert output.details["e_form"] is None
    assert output.details["formation_energy_status"] == "NOT_CALCULATED"
    assert output.details["stability_status"] == "NOT_EVALUATED"


def test_valid_primary_does_not_infer_zeroed_forces(monkeypatch):
    output = _run_model(monkeypatch)[1]
    assert output.details["forces_zeroed"] is None
    assert output.details["convergence_status"] == "NOT_VERIFIED"


@pytest.mark.parametrize("energy,threshold", [
    (-100.0, -1000.0), (-5.5, -10.0), (-5.5, 0.35),
    (0.0, 0.0), (100.0, 1.0),
])
def test_primary_potential_energy_never_becomes_stability_pass(monkeypatch, energy, threshold):
    result = _run_model(
        monkeypatch, result=_primary_result(potential_energy_ev_per_atom=energy),
        threshold=threshold,
    )[1]
    assert result.severity == "INFO"
    assert result.details["e_form_threshold_application"] == "NOT_APPLIED"
    assert result.details["stability_status"] == "NOT_EVALUATED"


def test_result_is_always_two_findings_for_success(monkeypatch):
    result = _run_model(monkeypatch)
    assert len(result) == 2
    assert result[0].validator == "GeometricDistanceScreen"
    assert result[1].validator == "MLFFValidator"


def test_success_preserves_relaxed_structure_if_supplied(monkeypatch):
    relaxed = _one_site()
    result = _run_model(monkeypatch, result=_primary_result(relaxed_structure=relaxed))
    assert result[1].details["relaxed_structure"] is relaxed
    assert result[1].details["convergence_status"] == "NOT_VERIFIED"


def test_engine_does_not_mutate_primary_result(monkeypatch):
    primary = _primary_result()
    _run_model(monkeypatch, result=primary)
    assert primary == _primary_result()


def test_valid_results_do_not_trigger_network_calls(monkeypatch):
    def forbid(*args, **kwargs):
        raise AssertionError("No network access is permitted by mock")
    monkeypatch.setattr(socket, "create_connection", forbid)
    monkeypatch.setattr(urllib.request, "urlopen", forbid)
    _run_model(monkeypatch)


@pytest.mark.parametrize("bad", [None, False, 0, "CHGNet", [], (), 123])
def test_invalid_primary_container_cannot_be_published(monkeypatch, bad):
    with pytest.raises(RuntimeError, match="Invalid CHGNet provenance"):
        _run_model(monkeypatch, result=bad)


@pytest.mark.parametrize("change", [
    {"engine": "MACE"},
    {"engine": "DFT"},
    {"engine": "NOT_RUN"},
    {"execution_status": "NOT_RUN"},
    {"execution_status": "FAILED"},
    {"execution_status": None},
    {"model_output_provenance": "MEASURED_EXPERIMENT"},
    {"model_output_provenance": "UNKNOWN"},
])
def test_invalid_primary_provenance_fails_closed(monkeypatch, change):
    with pytest.raises(RuntimeError, match="Invalid CHGNet provenance"):
        _run_model(monkeypatch, result=_primary_result(**change))


@pytest.mark.parametrize("bad", [
    None, False, True, "-1.0", "", [], {}, (),
    float("nan"), float("inf"), -float("inf"), 10 ** 1000,
])
def test_missing_or_invalid_potential_energy_rejected(monkeypatch, bad):
    with pytest.raises(RuntimeError, match="potential energy"):
        _run_model(monkeypatch, result=_primary_result(potential_energy_ev_per_atom=bad))


@pytest.mark.parametrize("field", [
    "e_form", "formation_energy_ev_per_atom", "synthesizability_score",
    "band_gap_class", "estimated_gap_eV", "converged",
])
def test_unsupported_scientific_claim_is_not_accepted(monkeypatch, field):
    with pytest.raises(RuntimeError, match="Unsupported physical claim"):
        _run_model(monkeypatch, result=_primary_result(**{field: 0.95}))


def test_missing_model_energy_is_not_synthesized_from_geometry(monkeypatch):
    result = _primary_result()
    result.pop("potential_energy_ev_per_atom")
    with pytest.raises(RuntimeError, match="Missing CHGNet potential energy"):
        _run_model(monkeypatch, result=result, structure=_structure(0.5))


def test_primary_does_not_replace_geometry_finding(monkeypatch):
    output = _run_model(monkeypatch, structure=_structure(0.5))
    assert output[0].severity == "REVIEW"
    assert output[1].severity == "INFO"
    assert output[1].details["stability_status"] == "NOT_EVALUATED"


def test_legacy_synthetic_relaxation_helper_is_explicitly_disabled():
    engine = ValidationEngine(use_mlff=False)
    with pytest.raises(NotImplementedError, match="Legacy formation-energy"):
        engine._relax_and_evaluate(_structure(), 1.7)


def test_metadata_is_json_serializable_without_nan_when_mlff_disabled():
    findings = ValidationEngine(use_mlff=False).run_all(_structure())
    assert json.loads(json.dumps(
        [{"severity": f.severity, "details": f.details} for f in findings],
        allow_nan=False,
    ))[1]["details"]["potential_energy_ev_per_atom"] is None


