"""Software-safety tests; no database/patent search or novelty calculation.

These tests verify explicit NOT_RUN/NOT_CHECKED metadata and fail-closed
handling of unknown scientific and legal conclusions. They are NOT evidence
of actual novelty, patent clearance, or freedom to operate.
"""

import socket
import urllib.request

import pytest

from src.imd_pipeline.agents.literature_agent import RealLiteraturePatentAgent


def _assess(formula="LiFePO4", fingerprint="fingerprint_xyz"):
    return RealLiteraturePatentAgent.evaluate_novelty(formula, fingerprint)


def test_valid_inputs_are_reported_without_claiming_validation():
    result = _assess()
    assert result["formula"] == "LiFePO4"
    assert result["structure_fingerprint"] == "fingerprint_xyz"
    assert result["input_provenance"] == "CALLER_SUPPLIED_NOT_VERIFIED"
    assert result["formula_validation_status"] == "NOT_VERIFIED"
    assert result["structure_fingerprint_validation_status"] == "NOT_VERIFIED"


def test_caller_whitespace_is_trimmed_not_validated():
    result = _assess("  LiFePO4  ", "  fingerprint_xyz  ")
    assert result["formula"] == "LiFePO4"
    assert result["structure_fingerprint"] == "fingerprint_xyz"


def test_novelty_score_and_confidence_not_fabricated():
    result = _assess()
    assert result["novelty_assessment_status"] == "NOT_EVALUATED"
    assert result["novelty_score"] is None
    assert result["confidence"] is None


def test_closest_material_and_polymorph_not_fabricated():
    result = _assess()
    assert result["closest_known_material"] is None
    assert result["known_polymorph"] is None


def test_no_data_source_is_reported_as_consulted():
    assert _assess()["data_sources_consulted"] == []


def test_every_external_source_is_explicitly_not_run():
    checks = _assess()["source_checks"]
    assert set(checks) == {
        "Materials Project", "OQMD", "Crossref", "arXiv", "Patent databases"
    }
    assert all(status == "NOT_RUN" for status in checks.values())


def test_patent_clearance_is_not_claimed():
    prior_art = _assess()["patent_prior_art"]
    assert prior_art["status"] == "NOT_CHECKED"
    assert prior_art["freedom_to_operate"] == "NOT_ASSESSED"


def test_patent_numbers_and_overlap_probabilities_not_invented():
    prior_art = _assess()["patent_prior_art"]
    assert prior_art["closest_patent"] is None
    assert prior_art["claim_overlap_probability"] is None


def test_patent_claims_and_jurisdictions_not_invented():
    prior_art = _assess()["patent_prior_art"]
    assert prior_art["patent_claims_reviewed"] == 0
    assert prior_art["jurisdictions_checked"] == []


def test_interpretation_explicitly_discloses_missing_search():
    note = _assess()["scientific_interpretation"]
    assert "NO SEARCH OR NOVELTY ASSESSMENT PERFORMED" in note
    assert "not independently checked" in note
    assert "No publications, structures, polymorphs, or patents" in note


def test_interpretation_does_not_assert_patent_clearance():
    note = _assess()["scientific_interpretation"]
    assert "patent clearance are unknown" in note
    assert "freedom-to-operate review" in note


def test_nonchemical_text_is_not_misrepresented_as_validated_formula():
    result = _assess("not necessarily a formula", "not a measured fingerprint")
    assert result["formula_validation_status"] == "NOT_VERIFIED"
    assert result["structure_fingerprint_validation_status"] == "NOT_VERIFIED"
    assert result["novelty_score"] is None
def test_different_user_identifiers_do_not_create_fake_novelty_variation():
    a = _assess("LiFePO4", "fingerprint_A")
    b = _assess("Na3Zr2Si2PO12", "fingerprint_B")
    for result in (a, b):
        assert result["novelty_score"] is None
        assert result["confidence"] is None
        assert result["patent_prior_art"]["status"] == "NOT_CHECKED"
    assert a["structure_fingerprint"] != b["structure_fingerprint"]


def test_mutating_returned_source_checks_does_not_leak_between_calls():
    first = _assess()
    first["source_checks"]["Crossref"] = "CHANGED_BY_TEST"
    second = _assess()
    assert second["source_checks"]["Crossref"] == "NOT_RUN"


def test_mutating_returned_patent_info_does_not_leak_between_calls():
    first = _assess()
    first["patent_prior_art"]["jurisdictions_checked"].append("fictional-jurisdiction")
    first["patent_prior_art"]["status"] = "CHANGED_BY_TEST"
    second = _assess()
    assert second["patent_prior_art"]["jurisdictions_checked"] == []
    assert second["patent_prior_art"]["status"] == "NOT_CHECKED"

def test_mutating_returned_source_list_does_not_leak_between_calls():
    first = _assess()
    first["data_sources_consulted"].append("FICTIONAL")
    assert _assess()["data_sources_consulted"] == []


def test_repeat_evaluation_is_deterministic_and_still_unverified():
    first = _assess()
    second = _assess()
    assert first == second
    assert first is not second
    assert first["novelty_assessment_status"] == "NOT_EVALUATED"


def test_unrelated_external_network_functions_not_needed(monkeypatch):
    def fail_network(*args, **kwargs):
        raise AssertionError("No network calls are allowed in legacy safety agent")

    monkeypatch.setattr(socket, "create_connection", fail_network)
    monkeypatch.setattr(urllib.request, "urlopen", fail_network)
    result = _assess()
    assert result["data_sources_consulted"] == []
    assert all(status == "NOT_RUN" for status in result["source_checks"].values())

@pytest.mark.parametrize("bad_formula", [
    None, "", " ", "\t\n", 123, True, False, [], {}, 1.5
])
def test_invalid_formula_fails_without_creating_unsupported_results(bad_formula):
    with pytest.raises(ValueError, match="formula"):
        _assess(formula=bad_formula)


@pytest.mark.parametrize("bad_fingerprint", [
    None, "", " ", "\t\n", 123, True, False, [], {}, 1.5
])
def test_invalid_structure_fingerprint_fails_without_inventing_results(bad_fingerprint):
    with pytest.raises(ValueError, match="structure_fingerprint"):
        _assess(fingerprint=bad_fingerprint)

