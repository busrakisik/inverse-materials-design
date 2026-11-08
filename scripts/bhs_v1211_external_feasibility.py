"""V12.11: source-attributed laboratory lead review, never lab authorization.

This offline module accepts a frozen public university-source dossier only.
It neither checks real-time laboratory status nor contacts anyone. It rejects
attempts to promote historical facility inventory to prospective physical proof.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = "BHS-V12.11"
DOSSIER_FILE = Path("research/BHS_V1211_GTU_PUBLIC_CAPABILITY_DOSSIER.json")
MAX_BYTES = 300_000
ROOT_KEYS = frozenset((
    "schema_version", "status", "institution", "location", "proposed_material",
    "retrieval_date", "source_independence_note", "evidence",
    "role_date_conflict", "required_feasibility_checks", "communication", "conclusions",
))
EVIDENCE_KEYS = frozenset((
    "id", "evidence_class", "source_date", "source_date_kind", "url",
    "material_system_scope", "supports", "summary",
))
CLASSES = frozenset((
    "institutional_inventory", "institutional_directory", "conflicting_legacy_directory",
    "historical_research_example",
))
DATE_KINDS = frozenset(("site_last_updated", "symposium_event_date", "undated"))
EXPECTED_SOURCES = {
    "gtnano-inventory-2025": (
        "institutional_inventory", "2025-09-29", "site_last_updated",
        "https://www.gtu.edu.tr/icerik/2676/758/display.aspx",
        ("moke_listed", "xrd_listed", "sputter_listed")),
    "gtphysics-moke-role-2026": (
        "institutional_directory", "2026-07-01", "site_last_updated",
        "https://www.gtu.edu.tr/en/kategori/4270/0/display.aspx",
        ("current_moke_directory_role",)),
    "gtphysics-legacy-moke-2015": (
        "conflicting_legacy_directory", "2015-06-29", "site_last_updated",
        "https://www.gtu.edu.tr/en/kategori/1658/0/display.aspx",
        ("legacy_moke_directory_role",)),
    "gtresearch-como-2025": (
        "historical_research_example", "2025-05-26", "symposium_event_date",
        "https://www.gtu.edu.tr/fileman/Files/UserFiles/fbe/GTU%20Semp_Bildiri%20%C3%96zet.%20Kitap%C3%A7%C4%B1%C4%9F%C4%B1_2025%20%281%29.pdf",
        ("historical_sputter_moke_xrd_work",)),
    "gtnano-director-2026": (
        "institutional_directory", "2026-04-16", "site_last_updated",
        "https://www.gtu.edu.tr/en/kategori/2774/0/yonetim.aspx",
        ("institute_contact_documented",)),
    "gtphysics-services-undated": (
        "institutional_directory", None, "undated",
        "https://www.gtu.edu.tr/kategori/3778/0/display.aspx",
        ("moke_service_category_listed", "sputter_service_category_listed")),
}
REQUIRED_GATES = frozenset((
    "qualified_investigator_consent_verified", "current_moke_operability_verified",
    "current_xrd_operability_verified", "current_sputter_operability_verified",
    "feconi_composition_and_thickness_capability_verified",
    "feconi_deposition_or_processing_intervention_approved",
    "treatment_assignment_unit_verified", "independent_synthesis_batch_feasibility_verified",
    "raw_trace_and_instrument_provenance_agreed", "instrument_field_calibration_verified",
    "source_rights_verified", "external_access_and_cost_verified",
    "minimum_meaningful_effect_and_precision_reviewed",
    "lab_safety_and_supervision_approved", "prospective_split_and_failure_logging_agreed",
))
COMMUNICATION_KEYS = frozenset((
    "initial_inquiry_sent", "reply_received", "facility_agreement_signed",
    "independent_review_completed",
))
DOCUMENTED_TRUE = frozenset((
    "institutional_moke_inventory_documented", "institutional_xrd_inventory_documented",
    "institutional_sputtering_inventory_documented",
    "historical_nonfeconi_joint_work_documented",
))
UNVERIFIED_FALSE = frozenset((
    "current_feconi_specific_feasibility_verified",
    "current_equipment_operability_verified", "physical_measurements_performed",
    "independent_physical_validation_established",
    "physical_recommendation_allowed", "laboratory_action_allowed",
    "real_cost_savings_verified",
))


class EvidenceGateError(ValueError):
    """Source data are incomplete, mismatched or incorrectly upgraded."""


def require(condition, reason):
    if not condition:
        raise EvidenceGateError(reason)


def no_duplicate_keys(pairs):
    result = {}
    for k, value in pairs:
        require(k not in result, "DUPLICATE_JSON_KEY")
        result[k] = value
    return result


def parse_dossier(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES, "INVALID_DOSSIER_BYTES")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicate_keys,
                          parse_constant=lambda _: (_ for _ in ()).throw(
                              EvidenceGateError("NONFINITE_JSON_VALUE")))
    except (UnicodeError, ValueError, TypeError) as exc:
        if isinstance(exc, EvidenceGateError):
            raise
        raise EvidenceGateError("INVALID_DOSSIER_JSON") from exc


def _text(x):
    return type(x) is str and bool(x.strip())


def review_dossier(d, *, original_sha256=None):
    require(type(d) is dict and set(d) == ROOT_KEYS, "INVALID_ROOT_STRUCTURE")
    expected = {
        "schema_version": SCHEMA,
        "status": "documented_uncontacted_lead_only",
        "institution": "Gebze Technical University",
        "location": "Gebze, Kocaeli, Türkiye",
        "proposed_material": "Fe-Co-Ni magnetic thin films",
        "retrieval_date": "2026-11-08",
    }
    require(all(d[k] == v for k, v in expected.items()), "DOSSIER_IDENTITY_CHANGED")
    require(_text(d["source_independence_note"]) and
            "same university" in d["source_independence_note"].lower(),
            "SOURCE_DEPENDENCE_NOT_DECLARED")
    source_rows = d["evidence"]
    require(type(source_rows) is list and len(source_rows) == len(EXPECTED_SOURCES),
            "MISSING_OR_ADDED_SOURCE")
    found = set()
    seen_urls = set()
    inventory_claims = set()
    classes = {}
    for row in source_rows:
        require(type(row) is dict and set(row) == EVIDENCE_KEYS,
                "INVALID_SOURCE_ROW_STRUCTURE")
        source_id = row["id"]
        require(type(source_id) is str and source_id in EXPECTED_SOURCES and
                source_id not in found, "UNKNOWN_OR_DUPLICATE_SOURCE")
        found.add(source_id)
        evidence_class, source_date, source_date_kind, url, support_tokens = EXPECTED_SOURCES[source_id]
        require((row["evidence_class"], row["source_date"], row["source_date_kind"],
                 row["url"]) == (evidence_class, source_date, source_date_kind, url),
                "FROZEN_INSTITUTIONAL_SOURCE_CHANGED")
        require(evidence_class in CLASSES and source_date_kind in DATE_KINDS,
                "UNSUPPORTED_SOURCE_CLASS")
        require(_text(row["material_system_scope"]) and _text(row["summary"]),
                "SOURCE_LIMITATION_NOT_DOCUMENTED")
        require(type(row["supports"]) is list and tuple(row["supports"]) == support_tokens,
                "SOURCE_CAPABILITY_CLAIM_CHANGED")
        p = urlsplit(row["url"])
        require(p.scheme == "https" and p.netloc == "www.gtu.edu.tr" and
                not p.username and not p.password and row["url"] not in seen_urls,
                "INVALID_OR_DUPLICATE_OFFICIAL_SOURCE_URL")
        seen_urls.add(row["url"])
        if source_date is None:
            require(source_date_kind == "undated", "MISSING_SOURCE_DATE_KIND")
        else:
            try:
                source_day = date.fromisoformat(source_date)
                cutoff = date.fromisoformat(d["retrieval_date"])
            except ValueError as exc:
                raise EvidenceGateError("INVALID_SOURCE_DATE") from exc
            require(source_day <= cutoff, "SOURCE_DATE_IN_FUTURE")
        if source_id == "gtresearch-como-2025":
            require("Co/Mo" in row["material_system_scope"] and
                    "not Fe-Co-Ni" in row["material_system_scope"],
                    "DIFFERENT_MATERIAL_SYSTEM_MISREPRESENTED")
        classes[source_id] = evidence_class
        inventory_claims.update(row["supports"])
    require(found == set(EXPECTED_SOURCES), "FROZEN_SOURCE_SET_INCOMPLETE")
    conflict = d["role_date_conflict"]
    require(type(conflict) is dict and set(conflict) == {
        "older_evidence_id", "newer_evidence_id", "status",
        "requires_direct_confirmation"}, "ROLE_CONFLICT_SCHEMA_INVALID")
    require(conflict == {
        "older_evidence_id": "gtphysics-legacy-moke-2015",
        "newer_evidence_id": "gtphysics-moke-role-2026",
        "status": "unresolved", "requires_direct_confirmation": True},
        "CONFLICTED_DIRECTORY_ROLE_UNRESOLVED")
    gates = d["required_feasibility_checks"]
    require(type(gates) is dict and set(gates) == REQUIRED_GATES,
            "FEASIBILITY_GATE_LIST_CHANGED")
    require(all(gates[k] is False for k in gates),
            "INDEPENDENT_PHYSICAL_FEASIBILITY_NOT_VERIFIED")
    communication = d["communication"]
    require(type(communication) is dict and set(communication) == COMMUNICATION_KEYS
            and all(communication[k] is False for k in communication),
            "UNSENT_COMMUNICATION_MISREPRESENTED")
    conclusions = d["conclusions"]
    require(type(conclusions) is dict and set(conclusions) == DOCUMENTED_TRUE | UNVERIFIED_FALSE,
            "INVALID_CLAIM_STRUCTURE")
    require(all(conclusions[k] is True for k in DOCUMENTED_TRUE) and
            all(conclusions[k] is False for k in UNVERIFIED_FALSE),
            "UNSUPPORTED_PHYSICAL_APPROVAL_OR_SUCCESS")
    require({"moke_listed", "xrd_listed", "sputter_listed",
             "historical_sputter_moke_xrd_work"}.issubset(inventory_claims),
            "MISSING_REFERENCED_TECHNIQUE")
    if original_sha256 is not None:
        require(type(original_sha256) is str and len(original_sha256) == 64 and
                all(x in "0123456789abcdef" for x in original_sha256),
                "INVALID_SOURCE_FINGERPRINT")
    return {
        "study": "BHS v12.11 public external-laboratory feasibility evidence audit",
        "source_sha256": original_sha256,
        "institution": d["institution"],
        "official_sources_count": len(found),
        "same_institution_sources_not_independent_confirmations": True,
        "publicly_documented_techniques": ["MOKE", "XRD", "magnetron sputtering"],
        "historical_material_system_is_not_proposed_system": True,
        "legacy_contact_role_conflict_unresolved": True,
        "unverified_feasibility_gate_count": len(REQUIRED_GATES),
        "unverified_feasibility_gate_keys": sorted(REQUIRED_GATES),
        "outreach_sent": False,
        "partner_agreement_verified": False,
        "proposed_material_capability_verified": False,
        "current_instrument_operability_verified": False,
        "processing_assignment_scope_verified": False,
        "external_scientific_approval_verified": False,
        "physical_measurements_performed": False,
        "physical_recommendation_allowed": False,
        "laboratory_action_allowed": False,
        "independent_physical_validation_established": False,
        "scientific_superiority_established": False,
        "measured_savings_established": False,
        "decision": "DOCUMENTED_LEAD_ONLY_NO_GO_PHYSICAL_EVALUATION",
    }


def audit_dossier_bytes(raw):
    return review_dossier(parse_dossier(raw), original_sha256=hashlib.sha256(raw).hexdigest())


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dossier", type=Path)
    p.add_argument("--out", type=Path)
    args = p.parse_args(argv)
    if args.dossier is None and args.out is None:
        print("No source loaded; no facility contacted or laboratory test conducted.")
        return 0
    if args.dossier is None or args.out is None:
        p.error("Both --dossier and --out are required")
    result = audit_dossier_bytes(args.dossier.read_bytes())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(result["decision"], "; unresolved gates:", result["unverified_feasibility_gate_count"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
