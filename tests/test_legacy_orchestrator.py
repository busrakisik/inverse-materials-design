# BEGIN OF COMPLETE BHS LEGACY ORCHESTRATOR SAFETY TESTS — CHECK THIS LINE ON GITHUB
"""Legacy orchestration software and provenance tests, NOT materials validation.

The workflow uses real pymatgen Structure and Composition objects, while
replacing the CHGNet adapter with a fake. No CHGNet weights, DFT, experiments,
Bayesian search, or autonomous crystal generation are run by these tests.
Passing them does NOT establish novel discovery or physical stability.
"""

import copy
import dataclasses
import math
import socket
import urllib.request

import pytest
from pymatgen.core import Lattice, Structure

from src.imd_pipeline.pipeline import orchestrator as orchestrator_module
from src.imd_pipeline.pipeline.orchestrator import DiscoveryResult, Orchestrator


_UNSET = object()


def _structure(species=None, coords=None):
    if species is None:
        species = ["Fe", "O"]
    if coords is None:
        coords = [[0, 0, 0], [0.5, 0.5, 0.5]]
    return Structure(Lattice.cubic(4.0), species, coords)


def _model_result(structure, **changes):
    result = {
        "engine": "CHGNet",
        "execution_status": "CHGNET_OPTIMIZER_RETURNED_OUTPUT",
        "model_output_provenance": "MLFF_PREDICTION_NOT_EXPERIMENT",
        "relaxed_structure": structure.copy(),
        "potential_energy_ev_per_atom": -6.0,
        "potential_energy_total_ev": -6.0 * len(structure),
        "max_force": 0.11,
        "min_distance": 2.0,
        "e_form": None,
        "formation_energy_ev_per_atom": None,
        "converged": None,
        "synthesizability_score": None,
        "band_gap_class": None,
        "estimated_gap_eV": None,
        "max_stress": None,
        "has_overlap": None,
        "ensemble_confidence": None,
        "is_ensemble_approved": None,
    }
    result.update(changes)
    return result


def _fake_primary(monkeypatch, *, prediction=_UNSET, error=None, records=None):
    if records is None:
        records = []

    class FakeMLFFValidator:
        def __init__(self, use_gpu=False):
            records.append(("init", use_gpu))

        def evaluate_and_relax(self, structure, *, fmax, steps):
            records.append(("relax", structure, fmax, steps))
            if error is not None:
                raise error
            if prediction is _UNSET:
                return _model_result(structure)
            return prediction

    monkeypatch.setattr(orchestrator_module, "MLFFValidator", FakeMLFFValidator)
    return records


def _run(monkeypatch, *, formula="FeO", initial=_UNSET, use_mlff=True,
         max_iterations=5, e_form_threshold=0.25, prediction=_UNSET,
         error=None, use_gpu=False):
    records = _fake_primary(monkeypatch, prediction=prediction, error=error)
    engine = Orchestrator(
        use_mlff=use_mlff,
        max_iterations=max_iterations,
        e_form_threshold=e_form_threshold,
        use_gpu=use_gpu,
    )
    if initial is _UNSET:
        initial = _structure()
    return engine.run_discovery_loop(formula, initial_structure=initial), records


def test_discovery_record_retains_legacy_compatibility_fields():
    fields = {f.name for f in dataclasses.fields(DiscoveryResult)}
    assert {"target_formula", "is_stable", "iterations_taken",
            "final_structure", "history"}.issubset(fields)


def test_discovery_record_new_fields_fail_closed_by_default():
    record = DiscoveryResult("FeO", False, 0, None)
    assert record.execution_status == "NOT_RUN"
    assert record.stability_status == "NOT_EVALUATED"
    assert record.convergence_status == "NOT_VERIFIED"
    assert record.candidate_generation_status == "NOT_RUN"
    assert record.history == []


def test_discovery_records_do_not_share_history_lists():
    a = DiscoveryResult("FeO", False, 0, None)
    b = DiscoveryResult("FeO", False, 0, None)
    a.history.append({"iteration": 1})
    assert b.history == []


def test_constructor_does_not_trigger_model_evaluation(monkeypatch):
    records = _fake_primary(monkeypatch)
    Orchestrator()
    assert records == [("init", False)]


@pytest.mark.parametrize("flag", [False, True])
def test_constructor_forwards_device_preference_without_gpu_claim(monkeypatch, flag):
    records = _fake_primary(monkeypatch)
    engine = Orchestrator(use_gpu=flag)
    assert engine.use_gpu is flag
    assert records == [("init", flag)]


@pytest.mark.parametrize("bad", [None, False, True, 0, -1, 2.3, "5", [], {}, ()])
def test_bad_iteration_configuration_is_rejected(bad):
    with pytest.raises(ValueError, match="max_iterations"):
        Orchestrator(max_iterations=bad)


@pytest.mark.parametrize("bad", [None, 0, 1, "yes", [], {}, 0.0])
def test_nonboolean_mlff_configuration_is_rejected(bad):
    with pytest.raises(ValueError, match="use_mlff"):
        Orchestrator(use_mlff=bad)


@pytest.mark.parametrize("bad", [None, 0, 1, "cuda", [], {}, 0.0])
def test_nonboolean_gpu_configuration_is_rejected(bad):
    with pytest.raises(ValueError, match="use_gpu"):
        Orchestrator(use_gpu=bad)


@pytest.mark.parametrize("bad", [
    None, True, False, "0.25", "", [], {}, (),
    float("nan"), float("inf"), -float("inf"), 10**1000,
])
def test_bad_formation_threshold_configuration_is_rejected(bad):
    with pytest.raises(ValueError, match="e_form_threshold"):
        Orchestrator(e_form_threshold=bad)


@pytest.mark.parametrize("threshold", [-100.0, -1.0, 0.0, 0.25, 1.0, 100.0])
def test_legacy_threshold_is_retained_but_never_used_to_approve(monkeypatch, threshold):
    result, _ = _run(monkeypatch, e_form_threshold=threshold)
    assert result.is_stable is False
    assert result.stability_status == "NOT_EVALUATED"
    assert result.history[0]["stability_status"] == "NOT_EVALUATED"
    assert result.history[0]["e_form"] is None


@pytest.mark.parametrize("bad", [None, False, True, 0, 1.3, [], {}, (), ""])
def test_invalid_formula_type_or_empty_is_rejected(bad):
    with pytest.raises(ValueError, match="target_formula"):
        Orchestrator._parse_target_formula(bad)


@pytest.mark.parametrize("bad", ["???", "Fe(", "@@@", "A" * 257])
def test_unparseable_or_oversized_formula_is_rejected(bad):
    with pytest.raises(ValueError, match="target_formula"):
        Orchestrator._parse_target_formula(bad)


def test_formula_parser_supports_a_normal_chemical_formula():
    comp = Orchestrator._parse_target_formula("FeO")
    assert comp.reduced_formula == "FeO"
    assert comp.num_atoms == pytest.approx(2)


def test_formula_parser_accepts_explicit_stoichiometric_multiple():
    target = Orchestrator._parse_target_formula("Fe2O2")
    reference = Orchestrator._parse_target_formula("FeO")
    assert target.reduced_composition == reference.reduced_composition


def test_no_supplied_candidate_is_not_misrepresented_as_discovery(monkeypatch):
    result, records = _run(monkeypatch, initial=None)
    assert result.execution_status == "NOT_RUN"
    assert result.candidate_generation_status == "NOT_IMPLEMENTED"
    assert result.is_stable is False
    assert result.iterations_taken == 0
    assert result.final_structure is None
    assert result.history == []
    assert len(records) == 1


def test_no_supplied_candidate_discloses_no_generator(monkeypatch):
    result, _ = _run(monkeypatch, initial=None)
    assert "NO MATERIALS DISCOVERY PERFORMED" in result.scientific_interpretation
    assert result.convergence_status == "NOT_VERIFIED"


@pytest.mark.parametrize("bad", [False, True, 0, 1.0, "FeO", [], {}, ()])
def test_invalid_supplied_candidate_is_rejected(monkeypatch, bad):
    with pytest.raises(ValueError, match="Structure"):
        _run(monkeypatch, initial=bad)


def test_mismatched_formula_and_candidate_is_rejected(monkeypatch):
    with pytest.raises(ValueError, match="composition"):
        _run(monkeypatch, formula="LiFePO4")


def test_element_order_does_not_create_a_false_formula_mismatch(monkeypatch):
    result, _ = _run(monkeypatch, formula="OFe", use_mlff=False)
    assert result.execution_status == "NOT_RUN"
    assert result.candidate_generation_status == "CALLER_SUPPLIED"


def test_formula_stoichiometric_multiple_matches_reduced_composition(monkeypatch):
    result, _ = _run(monkeypatch, formula="Fe2O2", use_mlff=False)
    assert result.execution_status == "NOT_RUN"


def test_real_candidate_is_never_replaced_by_a_default_lifepo4(monkeypatch):
    result, records = _run(monkeypatch, formula="FeO", initial=_structure())
    assert result.candidate_generation_status == "CALLER_SUPPLIED"
    assert result.target_formula == "FeO"
    assert result.final_structure.composition.reduced_formula == "FeO"
    assert records[1][1].composition.reduced_formula == "FeO"


def test_autonomous_candidate_generation_is_explicitly_unimplemented():
    with pytest.raises(NotImplementedError, match="No LLM"):
        Orchestrator._generate_initial_candidate("FeO")


def test_autonomous_refinement_is_explicitly_unimplemented():
    with pytest.raises(NotImplementedError, match="No verified feedback"):
        Orchestrator._perturb_structure_for_retry(_structure(), 2)


def test_mlff_off_does_not_call_model_even_when_structure_supplied(monkeypatch):
    result, records = _run(monkeypatch, use_mlff=False)
    assert records == [("init", False)]
    assert result.execution_status == "NOT_RUN"
    assert result.iterations_taken == 0
    assert result.history == []
    assert result.final_structure is None


def test_mlff_off_does_not_invent_energy_force_or_stability(monkeypatch):
    result, _ = _run(monkeypatch, use_mlff=False)
    assert result.is_stable is False
    assert result.stability_status == "NOT_EVALUATED"
    assert "no relaxation" in result.scientific_interpretation


def test_model_runs_exactly_one_candidate_even_if_max_iterations_is_large(monkeypatch):
    result, records = _run(monkeypatch, max_iterations=1000)
    assert len([row for row in records if row[0] == "relax"]) == 1
    assert result.iterations_taken == 1
    assert len(result.history) == 1


def test_primary_receives_original_candidate_without_replacement(monkeypatch):
    candidate = _structure()
    result, records = _run(monkeypatch, initial=candidate)
    assert records[1][1] is candidate
    assert result.execution_status == "CHGNET_OPTIMIZER_RETURNED_OUTPUT"


def test_primary_model_receives_explicit_relaxation_parameters(monkeypatch):
    _, records = _run(monkeypatch)
    assert records[1][2:] == (0.1, 100)


def test_valid_primary_result_has_explicit_model_provenance(monkeypatch):
    result, _ = _run(monkeypatch)
    assert result.history[0]["execution_status"] == "CHGNET_OPTIMIZER_RETURNED_OUTPUT"
    assert result.history[0]["model_output_provenance"] == "MLFF_PREDICTION_NOT_EXPERIMENT"
    assert result.history[0]["candidate_provenance"] == "CALLER_SUPPLIED_NOT_VERIFIED"


def test_negative_primary_potential_energy_is_not_formation_energy(monkeypatch):
    result, _ = _run(monkeypatch)
    assert result.history[0]["potential_energy_ev_per_atom"] == pytest.approx(-6.0)
    assert result.history[0]["e_form"] is None
    assert result.history[0]["formation_energy_status"] == "NOT_CALCULATED"


def test_valid_primary_cannot_certify_stability_or_discovery(monkeypatch):
    result, _ = _run(monkeypatch)
    assert result.is_stable is False
    assert result.stability_status == "NOT_EVALUATED"
    assert "no thermodynamic stability" in result.scientific_interpretation
    assert "novel materials discovery" in result.scientific_interpretation


def test_unverified_model_force_does_not_imply_convergence(monkeypatch):
    result, _ = _run(monkeypatch)
    assert result.history[0]["max_force"] == pytest.approx(0.11)
    assert result.history[0]["convergence_status"] == "NOT_VERIFIED"
    assert result.convergence_status == "NOT_VERIFIED"


def test_valid_primary_does_not_invent_stress_or_overlap_flag(monkeypatch):
    result, _ = _run(monkeypatch)
    assert result.history[0]["max_stress"] is None
    assert result.history[0]["has_overlap"] is None
    assert result.history[0]["is_ensemble_approved"] is None


def test_valid_primary_requires_no_automatic_followup_retry(monkeypatch):
    result, records = _run(monkeypatch)
    assert result.history[0]["retry_status"] == "NOT_ATTEMPTED_NO_GENERATOR"
    assert result.iterations_taken == 1
    assert len(records) == 2


def test_history_contains_no_material_stability_pass(monkeypatch):
    result, _ = _run(monkeypatch)
    assert result.history[0]["severity"] == "INFO"
    assert result.history[0]["stability_status"] == "NOT_EVALUATED"
    assert result.is_stable is False


def test_formation_energy_threshold_does_not_change_model_approval(monkeypatch):
    a, _ = _run(monkeypatch, e_form_threshold=-100.0)
    b, _ = _run(monkeypatch, e_form_threshold=100.0)
    assert a.is_stable is False and b.is_stable is False
    assert a.history[0]["severity"] == b.history[0]["severity"] == "INFO"


def test_positive_potential_energy_is_not_called_unstable(monkeypatch):
    s = _structure()
    r, _ = _run(monkeypatch, prediction=_model_result(s,
        potential_energy_ev_per_atom=3.0,
        potential_energy_total_ev=6.0))
    assert r.stability_status == "NOT_EVALUATED"
    assert r.is_stable is False


def test_model_result_is_not_modified_by_orchestrator(monkeypatch):
    structure = _structure()
    original = _model_result(structure)
    snapshot = copy.deepcopy(original)
    _run(monkeypatch, prediction=original)
    assert original == snapshot


def test_primary_result_preserves_relaxed_structure(monkeypatch):
    s = _structure()
    relaxed = s.copy()
    r, _ = _run(monkeypatch, prediction=_model_result(s, relaxed_structure=relaxed))
    assert r.final_structure is relaxed


def test_failed_model_does_not_create_synthetic_physics(monkeypatch):
    r, _ = _run(monkeypatch, error=RuntimeError("CHGNet unavailable"))
    assert r.execution_status == "FAILED"
    assert r.history[0]["severity"] == "ERROR"
    assert r.history[0]["potential_energy_ev_per_atom"] is None
    assert r.history[0]["e_form"] is None
    assert r.history[0]["max_force"] is None
    assert r.final_structure is None
    assert r.is_stable is False


@pytest.mark.parametrize("error", [
    ImportError("CHGNet absent"), RuntimeError("bad GPU"),
    ValueError("no trajectory"), OSError("missing weights"),
])
def test_failing_model_reports_exception_type_not_false_success(monkeypatch, error):
    result, _ = _run(monkeypatch, error=error)
    assert result.execution_status == "FAILED"
    assert result.history[0]["error_type"] == type(error).__name__
    assert result.history[0]["stability_status"] == "NOT_EVALUATED"


def test_failure_retains_caller_supplied_provenance(monkeypatch):
    r, _ = _run(monkeypatch, error=RuntimeError("invalid"))
    assert r.candidate_generation_status == "CALLER_SUPPLIED"
    assert r.iterations_taken == 1
    assert r.convergence_status == "NOT_VERIFIED"


def test_failure_never_attempts_fabricated_retries(monkeypatch):
    r, records = _run(monkeypatch, max_iterations=10, error=RuntimeError("no CHGNet"))
    assert r.iterations_taken == 1
    assert len([x for x in records if x[0] == "relax"]) == 1


def test_bad_primary_result_type_rejected_without_approval(monkeypatch):
    with pytest.raises(RuntimeError, match="Invalid CHGNet result"):
        _run(monkeypatch, prediction=None)


@pytest.mark.parametrize("bad", [None, 3.0, [], {}, "wrong", False, True])
def test_invalid_primary_result_container_rejected(monkeypatch, bad):
    with pytest.raises(RuntimeError, match="Invalid CHGNet result|unverified execution provenance"):
        _run(monkeypatch, prediction=bad)


@pytest.mark.parametrize("changes", [
    {"engine": "MACE"},
    {"engine": "DFT"},
    {"execution_status": "NOT_RUN"},
    {"execution_status": "FAILED"},
    {"model_output_provenance": "MEASURED_EXPERIMENT"},
    {"model_output_provenance": "UNVERIFIED"},
])
def test_primary_provenance_mismatch_rejected(monkeypatch, changes):
    with pytest.raises(RuntimeError, match="unverified execution provenance"):
        _run(monkeypatch, prediction=_model_result(_structure(), **changes))


@pytest.mark.parametrize("bad", [None, float("nan"), float("inf"),
                                       -float("inf"), False, True, "6", [], {},
                                       (), 10**1000])
def test_malformed_primary_potential_energy_rejected(monkeypatch, bad):
    with pytest.raises(RuntimeError, match="CHGNet"):
        _run(monkeypatch, prediction=_model_result(
            _structure(), potential_energy_ev_per_atom=bad))


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), "-12", True,
                                       False, [], {}, 10**1000])
def test_malformed_total_energy_rejected(monkeypatch, bad):
    with pytest.raises(RuntimeError, match="CHGNet"):
        _run(monkeypatch, prediction=_model_result(
            _structure(), potential_energy_total_ev=bad))


def test_inconsistent_total_energy_rejected(monkeypatch):
    with pytest.raises(RuntimeError, match="inconsistent"):
        _run(monkeypatch, prediction=_model_result(
            _structure(), potential_energy_total_ev=-7.0))


def test_absent_optional_total_energy_is_allowed(monkeypatch):
    r, _ = _run(monkeypatch, prediction=_model_result(
        _structure(), potential_energy_total_ev=None))
    assert r.execution_status == "CHGNET_OPTIMIZER_RETURNED_OUTPUT"
    assert r.is_stable is False


@pytest.mark.parametrize("bad", [-1.0, float("nan"), float("inf"),
                                       True, False, "1.2", [], {}, 10**1000])
def test_malformed_model_force_magnitude_rejected(monkeypatch, bad):
    with pytest.raises(RuntimeError, match="max_force"):
        _run(monkeypatch, prediction=_model_result(_structure(), max_force=bad))


@pytest.mark.parametrize("bad", [-1.0, float("nan"), float("inf"),
                                       True, False, "1.2", [], {}, 10**1000])
def test_malformed_pair_distance_rejected(monkeypatch, bad):
    with pytest.raises(RuntimeError, match="min_distance"):
        _run(monkeypatch, prediction=_model_result(_structure(), min_distance=bad))


@pytest.mark.parametrize("name", [
    "e_form", "formation_energy_ev_per_atom", "converged",
    "synthesizability_score", "band_gap_class", "estimated_gap_eV",
    "max_stress", "has_overlap", "ensemble_confidence",
    "is_ensemble_approved",
])
def test_unsupported_primary_scientific_claim_rejected(monkeypatch, name):
    with pytest.raises(RuntimeError, match="unsupported physical claims"):
        _run(monkeypatch, prediction=_model_result(_structure(), **{name: 0.75}))


def test_relaxed_structure_with_changed_composition_rejected(monkeypatch):
    wrong = _structure(["Fe", "Fe"])
    with pytest.raises(RuntimeError, match="invalid relaxed structure"):
        _run(monkeypatch, prediction=_model_result(_structure(), relaxed_structure=wrong))


def test_relaxed_structure_with_different_atom_count_rejected(monkeypatch):
    wrong = _structure(["Li"], [[0, 0, 0]])
    with pytest.raises(RuntimeError, match="invalid relaxed structure"):
        _run(monkeypatch, prediction=_model_result(_structure(), relaxed_structure=wrong))


def test_missing_relaxed_structure_rejected(monkeypatch):
    with pytest.raises(RuntimeError, match="invalid relaxed structure"):
        _run(monkeypatch, prediction=_model_result(_structure(), relaxed_structure=None))


def test_cross_model_agreement_is_never_fabricated(monkeypatch):
    r, _ = _run(monkeypatch)
    assert "ensemble_confidence" not in r.history[0]
    assert r.history[0]["is_ensemble_approved"] is None


def test_negative_energy_does_not_introduce_confidence_score(monkeypatch):
    r, _ = _run(monkeypatch)
    assert r.history[0]["severity"] != "PASS"
    assert "confidence" not in r.history[0]


def test_no_network_calls_when_primary_is_fake(monkeypatch):
    def forbid(*args, **kwargs):
        raise AssertionError("No network calls allowed in fake CHGNet test")
    monkeypatch.setattr(socket, "create_connection", forbid)
    monkeypatch.setattr(urllib.request, "urlopen", forbid)
    r, _ = _run(monkeypatch)
    assert r.execution_status == "CHGNET_OPTIMIZER_RETURNED_OUTPUT"

# END OF COMPLETE BHS LEGACY ORCHESTRATOR SAFETY TESTS — CHECK THIS LINE ON GITHUB
