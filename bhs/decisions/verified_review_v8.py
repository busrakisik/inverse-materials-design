"""BHS v8: fail-closed integrity preflight for prospective scientific review.

A valid signature binds a packet to an independently configured key; it does
NOT establish truth of measurements, model calibration, causal validity or
laboratory safety. No automatic physical action is ever authorized.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from bhs.decisions.evidence_contract_v7 import assess as assess_v7

CONTRACT = "bhs-review-v8"
REQUIRED_UNIT_FIELDS = ("benefit_unit", "harm_unit", "abstention_unit")
EXPERT_ROLE = "independent_lab_reviewer"
MAX_ATTESTATION_DAYS = 30


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def _digest(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def _fail(base, status, reason):
    result = dict(base)
    result.update(status=status, reason_codes=[reason],
                  automatic_laboratory_action_authorized=False,
                  human_review_required_for_laboratory_action=True,
                  attestation_integrity_verified=False,
                  actual_measurement_validity_verified_by_code=False,
                  probability_calibration_verified_by_code=False)
    return result


def _parse_utc(value):
    if not isinstance(value, str):
        raise ValueError("A timestamp is required")
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("Timestamp must carry an offset")
    return t.astimezone(timezone.utc)


def guarded_assessment(level, evidence, *, risk=None, attestation=None,
                       trusted_reviewers=None, now=None):
    """Conservative v7 extension: only an out-of-band trust anchor may review.

    trusted_reviewers MUST be installed by the deployment administrator, never
    supplied by the same untrusted caller as the submitted evidence. Source
    reference strings and even verified signatures cannot prove source truth.
    """
    base = assess_v7(level, evidence, risk=risk)
    if base["status"] != "ELIGIBLE_FOR_EXPERT_REVIEW":
        return dict(base, v8_integrity_guard="NOT_APPLICABLE",
                    attestation_integrity_verified=False)
    if level != "laboratory":
        return _fail(base, "ABSTAIN_UNEXPECTED_REVIEW_SCOPE", "LABORATORY_SCOPE_REQUIRED")
    if not isinstance(risk, Mapping):
        return _fail(base, "ABSTAIN_INVALID_RISK_UNITS", "RISK_RECORD_NOT_A_MAPPING")
    try:
        units = [risk[x] for x in REQUIRED_UNIT_FIELDS]
    except KeyError:
        return _fail(base, "ABSTAIN_INVALID_RISK_UNITS", "RISK_UNITS_NOT_DECLARED")
    if (any(not isinstance(u, str) or not u.strip() or u.lower().strip() == "unspecified" for u in units)
            or len(set(units)) != 1 or risk.get("utility_units") != units[0]):
        return _fail(base, "ABSTAIN_INVALID_RISK_UNITS", "RISK_UNITS_NOT_COMPARABLE")
    if (not isinstance(risk.get("lower_bound_method"), str)
            or not risk["lower_bound_method"].strip()
            or not isinstance(risk.get("validation_population"), str)
            or not risk["validation_population"].strip()):
        return _fail(base, "ABSTAIN_UNDOCUMENTED_RISK_BOUND", "BOUND_METHOD_OR_POPULATION_MISSING")
    if not isinstance(trusted_reviewers, Mapping) or not isinstance(attestation, Mapping):
        return _fail(base, "REQUEST_INDEPENDENT_ATTESTATION", "TRUSTED_REVIEW_NOT_AVAILABLE")
    reviewer = attestation.get("reviewer_id")
    trusted = trusted_reviewers.get(reviewer) if isinstance(reviewer, str) else None
    if (not isinstance(trusted, Mapping) or trusted.get("role") != EXPERT_ROLE
            or not isinstance(trusted.get("public_key_b64"), str)):
        return _fail(base, "ABSTAIN_UNTRUSTED_REVIEWER", "NO_OUT_OF_BAND_TRUST_ANCHOR")
    packet = attestation.get("packet")
    if not isinstance(packet, Mapping):
        return _fail(base, "ABSTAIN_ATTESTATION_SCHEMA", "MISSING_REVIEW_PACKET")
    required = ("contract", "reviewer_id", "scope", "evidence_sha256", "risk_sha256", "issued_at", "expires_at")
    if (set(packet) != set(required) or packet.get("contract") != CONTRACT
            or packet.get("reviewer_id") != reviewer or packet.get("scope") != "laboratory"):
        return _fail(base, "ABSTAIN_ATTESTATION_SCHEMA", "INVALID_REVIEW_PACKET_SCOPE")
    try:
        if packet["evidence_sha256"] != _digest(evidence) or packet["risk_sha256"] != _digest(risk):
            return _fail(base, "ABSTAIN_ATTESTATION_MISMATCH", "SIGNED_PACKET_DOES_NOT_BIND_CURRENT_INPUTS")
        issued, expiry = _parse_utc(packet["issued_at"]), _parse_utc(packet["expires_at"])
        instant = now if now is not None else datetime.now(timezone.utc)
        if not isinstance(instant, datetime) or instant.tzinfo is None:
            raise ValueError("now must be offset aware")
        instant = instant.astimezone(timezone.utc)
        if expiry <= issued or expiry - issued > timedelta(days=MAX_ATTESTATION_DAYS):
            return _fail(base, "ABSTAIN_ATTESTATION_WINDOW", "INVALID_REVIEW_VALIDITY_WINDOW")
        if issued > instant:
            return _fail(base, "ABSTAIN_ATTESTATION_NOT_YET_VALID", "REVIEW_ISSUED_IN_THE_FUTURE")
        if expiry <= instant:
            return _fail(base, "ABSTAIN_EXPIRED_ATTESTATION", "REVIEW_EXPIRED")
        public_bytes = base64.b64decode(trusted["public_key_b64"], validate=True)
        signature_bytes = base64.b64decode(attestation.get("signature_b64"), validate=True)
        if len(public_bytes) != 32 or len(signature_bytes) != 64:
            raise ValueError("Invalid Ed25519 byte lengths")
        Ed25519PublicKey.from_public_bytes(public_bytes).verify(signature_bytes, _canonical(dict(packet)))
    except (ValueError, TypeError, KeyError, binascii.Error, InvalidSignature, OverflowError):
        return _fail(base, "ABSTAIN_INVALID_ATTESTATION", "CRYPTOGRAPHIC_OR_TIME_VERIFICATION_FAILED")
    result = dict(base)
    result.update(v8_integrity_guard="ATTESTED_FOR_EXPERT_REVIEW",
                  attestation_integrity_verified=True,
                  reviewer_id=reviewer,
                  cryptographic_linkage_verified=True,
                  actual_measurement_validity_verified_by_code=False,
                  probability_calibration_verified_by_code=False,
                  automatic_laboratory_action_authorized=False,
                  human_review_required_for_laboratory_action=True)
    return result


def create_unsigned_review_packet(reviewer_id, evidence, risk, issued_at, expires_at):
    """Prepare canonical review content for external signing; no private keys."""
    return {
        "contract": CONTRACT, "reviewer_id": reviewer_id,
        "scope": "laboratory", "evidence_sha256": _digest(evidence),
        "risk_sha256": _digest(risk), "issued_at": issued_at,
        "expires_at": expires_at,
    }
