"""Synthetic adversarial fixtures; no claims of calibrated or physical evidence."""
import base64
import json
import unittest
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from bhs.decisions.evidence_contract_v7 import REQUIRED
from bhs.decisions.verified_review_v8 import guarded_assessment, create_unsigned_review_packet

T0 = datetime(2026, 11, 6, 16, 0, tzinfo=timezone.utc)


def evidence():
    return {n: {"status": "verified", "source_ref": "record:" + n} for n in REQUIRED["laboratory"]}


def risk():
    return {
        "lower_success_probability": 0.99,
        "benefit_if_correct": 1.0, "harm_if_wrong": 3.0, "abstention_cost": 0.1,
        "lower_bound_provenance": "record:independent_performance_evidence",
        "utility_units": "illustrative_points",
        "benefit_unit": "illustrative_points",
        "harm_unit": "illustrative_points",
        "abstention_unit": "illustrative_points",
        "lower_bound_method": "synthetic fixture, no measured calibration",
        "validation_population": "fictional development group",
    }


def signed_packet(ev, ri, private_key=None, *, issued=None, expires=None):
    private_key = private_key or Ed25519PrivateKey.generate()
    issued = issued or T0 - timedelta(days=1)
    expires = expires or T0 + timedelta(days=1)
    packet = create_unsigned_review_packet(
        "fixture-lab-reviewer", ev, ri, issued.isoformat(), expires.isoformat())
    sig = private_key.sign(json.dumps(
        packet, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False).encode())
    pub = private_key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return (
        {"reviewer_id": "fixture-lab-reviewer", "packet": packet,
         "signature_b64": base64.b64encode(sig).decode()},
        {"fixture-lab-reviewer": {
            "role": "independent_lab_reviewer",
            "public_key_b64": base64.b64encode(pub).decode()}}
    )


class VerifiedReviewV8Contracts(unittest.TestCase):
    def test_missing_context_stays_request(self):
        ev = evidence()
        ev["curing_conditions"] = {"status": "missing"}
        d = guarded_assessment("laboratory", ev, risk=risk(), now=T0)
        self.assertEqual(d["status"], "REQUEST_ADDITIONAL_EVIDENCE")
        self.assertFalse(d["automatic_laboratory_action_authorized"])

    def test_contradictions_cannot_be_overridden_by_signature(self):
        ev, ri = evidence(), risk()
        att, keys = signed_packet(ev, ri)
        ev["source_integrity"]["status"] = "contradicted"
        d = guarded_assessment("laboratory", ev, risk=ri, attestation=att,
                               trusted_reviewers=keys, now=T0)
        self.assertEqual(d["status"], "ABSTAIN_CONTRADICTED_ASSUMPTIONS")

    def test_missing_unit_fails_closed(self):
        ri = risk()
        ri.pop("benefit_unit")
        self.assertEqual(guarded_assessment("laboratory", evidence(), risk=ri, now=T0)["status"],
                         "ABSTAIN_INVALID_RISK_UNITS")

    def test_mixed_currency_units_fails_closed(self):
        ri = risk()
        ri["harm_unit"] = "USD"
        ri["abstention_unit"] = "EUR"
        self.assertEqual(guarded_assessment("laboratory", evidence(), risk=ri, now=T0)["status"],
                         "ABSTAIN_INVALID_RISK_UNITS")

    def test_unspecified_units_fail_closed(self):
        ri = risk()
        for key in ("benefit_unit", "harm_unit", "abstention_unit", "utility_units"):
            ri[key] = "unspecified"
        self.assertEqual(guarded_assessment("laboratory", evidence(), risk=ri, now=T0)["status"],
                         "ABSTAIN_INVALID_RISK_UNITS")

    def test_unclear_lower_bound_method_fails_closed(self):
        ri = risk()
        ri["lower_bound_method"] = ""
        self.assertEqual(guarded_assessment("laboratory", evidence(), risk=ri, now=T0)["status"],
                         "ABSTAIN_UNDOCUMENTED_RISK_BOUND")

    def test_unattested_evidence_never_becomes_review_eligible(self):
        d = guarded_assessment("laboratory", evidence(), risk=risk(), now=T0)
        self.assertEqual(d["status"], "REQUEST_INDEPENDENT_ATTESTATION")
        self.assertFalse(d["attestation_integrity_verified"])

    def test_untrusted_self_signed_key_does_not_create_trust(self):
        ev, ri = evidence(), risk()
        att, _ = signed_packet(ev, ri)
        d = guarded_assessment("laboratory", ev, risk=ri, attestation=att,
                               trusted_reviewers={}, now=T0)
        self.assertEqual(d["status"], "ABSTAIN_UNTRUSTED_REVIEWER")

    def test_signed_risk_cannot_be_changed(self):
        ev, ri = evidence(), risk()
        att, keys = signed_packet(ev, ri)
        ri["benefit_if_correct"] = 1000.0
        d = guarded_assessment("laboratory", ev, risk=ri, attestation=att,
                               trusted_reviewers=keys, now=T0)
        self.assertEqual(d["status"], "ABSTAIN_ATTESTATION_MISMATCH")

    def test_signed_evidence_cannot_be_changed(self):
        ev, ri = evidence(), risk()
        att, keys = signed_packet(ev, ri)
        ev["instrument_calibration"]["source_ref"] = "different:record"
        d = guarded_assessment("laboratory", ev, risk=ri, attestation=att,
                               trusted_reviewers=keys, now=T0)
        self.assertEqual(d["status"], "ABSTAIN_ATTESTATION_MISMATCH")

    def test_modified_signature_is_rejected(self):
        ev, ri = evidence(), risk()
        att, keys = signed_packet(ev, ri)
        att["signature_b64"] = base64.b64encode(b"\0" * 64).decode()
        d = guarded_assessment("laboratory", ev, risk=ri, attestation=att,
                               trusted_reviewers=keys, now=T0)
        self.assertEqual(d["status"], "ABSTAIN_INVALID_ATTESTATION")

    def test_expired_review_is_rejected(self):
        ev, ri = evidence(), risk()
        att, keys = signed_packet(ev, ri, issued=T0 - timedelta(days=4),
                                  expires=T0 - timedelta(days=1))
        self.assertEqual(guarded_assessment("laboratory", ev, risk=ri, attestation=att,
                        trusted_reviewers=keys, now=T0)["status"],
                         "ABSTAIN_EXPIRED_ATTESTATION")

    def test_future_review_is_rejected(self):
        ev, ri = evidence(), risk()
        att, keys = signed_packet(ev, ri, issued=T0 + timedelta(days=1),
                                  expires=T0 + timedelta(days=2))
        self.assertEqual(guarded_assessment("laboratory", ev, risk=ri, attestation=att,
                        trusted_reviewers=keys, now=T0)["status"],
                         "ABSTAIN_ATTESTATION_NOT_YET_VALID")

    def test_excessive_validity_window_is_rejected(self):
        ev, ri = evidence(), risk()
        att, keys = signed_packet(ev, ri, expires=T0 + timedelta(days=45))
        self.assertEqual(guarded_assessment("laboratory", ev, risk=ri, attestation=att,
                        trusted_reviewers=keys, now=T0)["status"],
                         "ABSTAIN_ATTESTATION_WINDOW")

    def test_valid_synthetic_signature_only_entitles_expert_review(self):
        ev, ri = evidence(), risk()
        att, keys = signed_packet(ev, ri)
        d = guarded_assessment("laboratory", ev, risk=ri, attestation=att,
                               trusted_reviewers=keys, now=T0)
        self.assertEqual(d["status"], "ELIGIBLE_FOR_EXPERT_REVIEW")
        self.assertTrue(d["attestation_integrity_verified"])
        self.assertFalse(d["actual_measurement_validity_verified_by_code"])
        self.assertFalse(d["probability_calibration_verified_by_code"])
        self.assertFalse(d["automatic_laboratory_action_authorized"])
        self.assertTrue(d["human_review_required_for_laboratory_action"])

    def test_descriptive_report_does_not_escalate(self):
        d = guarded_assessment("descriptive", evidence(), risk=risk(), now=T0)
        self.assertEqual(d["status"], "DESCRIPTIVE_REPORT_ONLY")
        self.assertFalse(d["automatic_laboratory_action_authorized"])


if __name__ == "__main__":
    unittest.main()
