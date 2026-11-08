"""Independent fail-closed checks for the V12.11 public institutional lead."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest

from scripts.bhs_v1211_external_feasibility import (
    EXPECTED_SOURCES, REQUIRED_GATES, COMMUNICATION_KEYS,
    DOCUMENTED_TRUE, UNVERIFIED_FALSE,
    EvidenceGateError, parse_dossier, review_dossier,
    audit_dossier_bytes, main,
)

DOSSIER = "research/BHS_V1211_GTU_PUBLIC_CAPABILITY_DOSSIER.json"


def original():
    with open(DOSSIER, encoding="utf-8") as f:
        return json.load(f)


class OfficialLeadContracts(unittest.TestCase):
    def test_original_official_lead_is_uncontacted(self):
        data = original()
        out = review_dossier(data)
        self.assertEqual(out["official_sources_count"], 6)
        self.assertEqual(out["unverified_feasibility_gate_count"], 15)
        self.assertEqual(out["decision"], "DOCUMENTED_LEAD_ONLY_NO_GO_PHYSICAL_EVALUATION")
        self.assertFalse(out["physical_recommendation_allowed"])
        self.assertFalse(out["partner_agreement_verified"])

    def test_sha_of_raw_source_is_reported(self):
        with open(DOSSIER, "rb") as f:
            raw = f.read()
        out = audit_dossier_bytes(raw)
        self.assertEqual(out["source_sha256"], hashlib.sha256(raw).hexdigest())

    def test_duplicate_json_key_and_nonfinite_json_refused(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b"bad", b""):
            with self.subTest(raw=raw[:30]):
                with self.assertRaises(EvidenceGateError):
                    parse_dossier(raw)

    def test_untrusted_university_identity_refused(self):
        for name, change in (("institution", "unverified site"), ("status", "approved"),
                             ("retrieval_date", "2027-01-01"), ("proposed_material", "Co/Mo")):
            data = original()
            data[name] = change
            with self.subTest(name=name):
                with self.assertRaises(EvidenceGateError):
                    review_dossier(data)

    def test_all_sources_are_one_institution_not_independent(self):
        data = original()
        data["source_independence_note"] = "six different physical confirmations"
        with self.assertRaisesRegex(EvidenceGateError, "DEPENDENCE"):
            review_dossier(data)

    def test_missing_and_duplicate_source_refused(self):
        for change in ("remove", "copy"):
            data = original()
            if change == "remove":
                data["evidence"].pop()
            else:
                data["evidence"][1] = copy.deepcopy(data["evidence"][0])
            with self.subTest(change=change):
                with self.assertRaises(EvidenceGateError):
                    review_dossier(data)

    def test_source_url_and_claim_injection_refused(self):
        for key, value in (("url", "https://attacker.example/moke"),
                           ("source_date", "2027-11-08"),
                           ("supports", ["current_feconi_synthesis_verified"])):
            data = original()
            data["evidence"][0][key] = value
            with self.subTest(key=key):
                with self.assertRaises(EvidenceGateError):
                    review_dossier(data)

    def test_old_role_disagreement_is_not_silently_resolved(self):
        data = original()
        data["role_date_conflict"]["status"] = "resolved"
        with self.assertRaisesRegex(EvidenceGateError, "DIRECTORY_ROLE_UNRESOLVED"):
            review_dossier(data)

    def test_co_mo_is_not_fe_co_ni_validation(self):
        data = original()
        row = next(r for r in data["evidence"] if r["id"] == "gtresearch-como-2025")
        row["material_system_scope"] = "Fe-Co-Ni verified by us"
        with self.assertRaisesRegex(EvidenceGateError, "DIFFERENT_MATERIAL_SYSTEM"):
            review_dossier(data)

    def test_external_feasibility_flags_cannot_be_upgraded(self):
        for key in sorted(REQUIRED_GATES):
            data = original()
            data["required_feasibility_checks"][key] = True
            with self.subTest(field=key):
                with self.assertRaises(EvidenceGateError):
                    review_dossier(data)

    def test_unsent_contact_does_not_become_sent(self):
        for key in sorted(COMMUNICATION_KEYS):
            data = original()
            data["communication"][key] = True
            with self.subTest(field=key):
                with self.assertRaisesRegex(EvidenceGateError, "UNSENT_COMMUNICATION"):
                    review_dossier(data)

    def test_no_physical_or_financial_success_can_be_claimed(self):
        for key in sorted(UNVERIFIED_FALSE):
            data = original()
            data["conclusions"][key] = True
            with self.subTest(field=key):
                with self.assertRaises(EvidenceGateError):
                    review_dossier(data)

    def test_structured_inventory_must_be_attributed(self):
        for key in sorted(DOCUMENTED_TRUE):
            data = original()
            data["conclusions"][key] = False
            with self.subTest(field=key):
                with self.assertRaises(EvidenceGateError):
                    review_dossier(data)

    def test_unexpected_data_and_source_field_refused(self):
        data = original()
        data["outcome_scores"] = [1, 2, 3]
        with self.assertRaisesRegex(EvidenceGateError, "ROOT_STRUCTURE"):
            review_dossier(data)
        data = original()
        data["evidence"][0]["private_measurements"] = "none"
        with self.assertRaisesRegex(EvidenceGateError, "SOURCE_ROW_STRUCTURE"):
            review_dossier(data)

    def test_protocol_default_does_not_read_outcomes(self):
        self.assertEqual(main([]), 0)


if __name__ == "__main__":
    unittest.main()
