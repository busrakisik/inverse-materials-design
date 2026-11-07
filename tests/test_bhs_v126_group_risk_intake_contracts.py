"""Source-independent structural contracts for BHS v12.6 read-only audit."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import unittest

from scripts.bhs_v126_group_risk_intake_contracts import (
    CAL_GROUPS, EVAL_GROUPS, ORDER_VARIANTS, POLICIES,
    EvidenceContractError, _check_rows, _stable_digest,
    audit_v125, hypothetical_group_upper_bound,
    minimum_zero_error_groups, validate_prospective_intake, main,
)


def fake_rows(groups, split):
    rows = []
    for group in groups:
        for order in ORDER_VARIANTS:
            for policy in POLICIES:
                rows.append({
                    "group": group, "order_variant": order, "policy": policy,
                    "split": split, "source_fingerprint": f"{group:064x}",
                    "latent_recommendation_regret": 0.25,
                    "high_regret_error": False,
                    "evidence_score": float(1 + order),
                    "measurement_count": 48,
                    "completed_designs": 10, "incomplete_designs": 2,
                    "stranded_partial_responses": 2,
                    "completion_interventions": 0,
                    "latent_outcomes_passed_to_selector": False,
                    "future_responses_passed_to_selector": False,
                })
    return rows


def sample_records():
    def rec(group, split, design, batch, ordinal, event):
        return {
            "event_id": event, "split": split, "group_id": group,
            "design_id": design, "replicate_ordinal": ordinal,
            "site_id": "site-001", "instrument_id": "instrument-001",
            "instrument_calibration_ref": "calibration-log-001",
            "synthesis_batch_id": "synth-" + batch,
            "measurement_batch_id": "measurement-" + batch,
            "timestamp": f"2026-11-07T10:0{ordinal}:00+03:00",
            "experiment_date": "2026-11-07",
            "units": "arbitrary-test-units", "value": float(ordinal),
            "reported_uncertainty": 0.1, "acquisition_cost": 7.0,
            "acquisition_seconds": 45.0,
        }
    return [
        rec("cal-a", "calibration", "design-a", "batch-a", 1, "event-1"),
        rec("cal-a", "calibration", "design-a", "batch-a", 2, "event-2"),
        rec("eval-b", "evaluation", "design-b", "batch-b", 1, "event-3"),
        rec("eval-b", "evaluation", "design-b", "batch-b", 2, "event-4"),
    ]


def encode_records(records):
    raw = json.dumps(records, sort_keys=True, separators=(",", ":"),
                     allow_nan=False).encode()
    manifest = {
        "source_id": "manufactured-test-fixture",
        "source_license": "test-fixture-only",
        "units": "arbitrary-test-units",
        "review_reference": "test-only-not-a-real-approval",
        "calibration_groups": ["cal-a"],
        "evaluation_groups": ["eval-b"],
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
    }
    return raw, manifest


class GroupRiskContracts(unittest.TestCase):
    def test_zero_error_illustration_requires_eleven_iid_groups(self):
        self.assertEqual(minimum_zero_error_groups(), 11)
        self.assertGreater(hypothetical_group_upper_bound(0, 4), 0.5)
        self.assertGreater(hypothetical_group_upper_bound(0, 10), 0.25)
        self.assertLessEqual(hypothetical_group_upper_bound(0, 11), 0.25)

    def test_group_error_math_and_zero_coverage(self):
        self.assertIsNone(hypothetical_group_upper_bound(0, 0))
        self.assertEqual(hypothetical_group_upper_bound(4, 4), 1.0)
        self.assertAlmostEqual(hypothetical_group_upper_bound(0, 1), 0.95)
        self.assertGreater(hypothetical_group_upper_bound(1, 3),
                           hypothetical_group_upper_bound(0, 3))

    def test_invalid_binomial_counts_and_assumptions_rejected(self):
        for count, total in [(-1, 4), (5, 4), (0, -1), (True, 4)]:
            with self.subTest(count=count, total=total):
                with self.assertRaises(EvidenceContractError):
                    hypothetical_group_upper_bound(count, total)
        with self.assertRaises(EvidenceContractError):
            minimum_zero_error_groups(0.0, 0.95)
        with self.assertRaises(EvidenceContractError):
            minimum_zero_error_groups(1.0, 0.95)

    def test_complete_group_grid_passes_and_is_grouped(self):
        rows = fake_rows(EVAL_GROUPS, "evaluation")
        sources = _check_rows(rows, split="evaluation", groups=EVAL_GROUPS)
        self.assertEqual(len(rows), 48)
        self.assertEqual(len(sources), 4)
        self.assertEqual(len({_stable_digest(rows)}), 1)

    def test_reused_campaign_and_missing_group_fails(self):
        rows = fake_rows(EVAL_GROUPS, "evaluation")
        rows[0] = dict(rows[1])
        with self.assertRaises(EvidenceContractError):
            _check_rows(rows, split="evaluation", groups=EVAL_GROUPS)
        rows = fake_rows(EVAL_GROUPS, "evaluation")[1:]
        with self.assertRaises(EvidenceContractError):
            _check_rows(rows, split="evaluation", groups=EVAL_GROUPS)

    def test_changed_fingerprint_within_same_group_fails(self):
        rows = fake_rows(EVAL_GROUPS, "evaluation")
        rows[1]["source_fingerprint"] = "f"*64
        with self.assertRaises(EvidenceContractError):
            _check_rows(rows, split="evaluation", groups=EVAL_GROUPS)

    def test_tampered_label_measurement_count_and_leakage_fail(self):
        for field, value in [
            ("high_regret_error", True), ("measurement_count", 47),
            ("future_responses_passed_to_selector", True),
            ("latent_outcomes_passed_to_selector", True),
            ("evidence_score", float("nan")),
            ("completed_designs", -1),
        ]:
            rows = fake_rows(CAL_GROUPS, "calibration")
            rows[0][field] = value
            with self.subTest(field=field):
                with self.assertRaises(EvidenceContractError):
                    _check_rows(rows, split="calibration", groups=CAL_GROUPS)

    def test_archived_reports_not_recreatable_by_unpinned_bytes(self):
        with self.assertRaisesRegex(EvidenceContractError, "SHA256_MISMATCH"):
            audit_v125(b"{}", b"{}")

    def test_manifest_check_accepts_only_structural_fixture(self):
        raw, manifest = encode_records(sample_records())
        result = validate_prospective_intake(raw, manifest)
        self.assertEqual(result["structural_record_count"], 4)
        self.assertTrue(result["source_sha256_matched"])
        self.assertFalse(result["source_authenticity_externally_verified"])
        self.assertFalse(result["instrument_calibration_externally_verified"])
        self.assertFalse(result["physical_recommendation_allowed"])
        self.assertFalse(result["statistical_guarantee_supported"])

    def test_original_bytes_integrity_and_source_license(self):
        raw, manifest = encode_records(sample_records())
        with self.assertRaisesRegex(EvidenceContractError, "DIGEST_MISMATCH"):
            validate_prospective_intake(raw+b" ", manifest)
        changed = dict(manifest, source_license="")
        with self.assertRaises(EvidenceContractError):
            validate_prospective_intake(raw, changed)

    def test_cross_split_design_or_batches_rejected(self):
        original = sample_records()
        for field in ("design_id", "synthesis_batch_id", "measurement_batch_id"):
            rows = copy.deepcopy(original)
            rows[2][field] = rows[0][field]
            raw, manifest = encode_records(rows)
            with self.subTest(field=field):
                with self.assertRaisesRegex(EvidenceContractError, "CROSS_SPLIT"):
                    validate_prospective_intake(raw, manifest)

    def test_duplicate_event_replicate_and_missing_ordinal_rejected(self):
        original = sample_records()
        for field, value in [
            ("event_id", original[0]["event_id"]),
            ("replicate_ordinal", original[0]["replicate_ordinal"]),
        ]:
            rows = copy.deepcopy(original)
            rows[1][field] = value
            raw, manifest = encode_records(rows)
            with self.subTest(field=field):
                with self.assertRaises(EvidenceContractError):
                    validate_prospective_intake(raw, manifest)
        rows = copy.deepcopy(original)
        rows[1]["replicate_ordinal"] = 3
        raw, manifest = encode_records(rows)
        with self.assertRaisesRegex(EvidenceContractError, "REPLICATES"):
            validate_prospective_intake(raw, manifest)

    def test_real_timestamps_must_include_timezone_and_increase(self):
        original = sample_records()
        for value in ("2026-11-07T10:02:00", "2026-11-07"):
            rows = copy.deepcopy(original)
            rows[1]["timestamp"] = value
            raw, manifest = encode_records(rows)
            with self.assertRaises(EvidenceContractError):
                validate_prospective_intake(raw, manifest)
        rows = copy.deepcopy(original)
        rows[1]["timestamp"] = "2026-11-07T09:00:00+03:00"
        raw, manifest = encode_records(rows)
        with self.assertRaisesRegex(EvidenceContractError, "NONCHRONOLOGICAL"):
            validate_prospective_intake(raw, manifest)

    def test_invalid_units_uncertainty_and_cost_fail(self):
        for field, value in [
            ("units", "wrong-unit"), ("reported_uncertainty", 0),
            ("acquisition_cost", -1), ("acquisition_seconds", 0),
            ("value", float("inf")), ("site_id", ""),
        ]:
            rows = copy.deepcopy(sample_records())
            rows[0][field] = value
            if not math.isfinite(value) if type(value) is float else False:
                raw = json.dumps(rows, allow_nan=True).encode()
                manifest = encode_records(sample_records())[1]
                manifest["raw_sha256"] = hashlib.sha256(raw).hexdigest()
            else:
                raw, manifest = encode_records(rows)
            with self.subTest(field=field):
                with self.assertRaises(EvidenceContractError):
                    validate_prospective_intake(raw, manifest)

    def test_cross_split_group_overlap_and_missing_group_fail(self):
        raw, manifest = encode_records(sample_records())
        overlap = dict(manifest, evaluation_groups=["cal-a"])
        with self.assertRaises(EvidenceContractError):
            validate_prospective_intake(raw, overlap)
        missing = dict(manifest, evaluation_groups=["eval-b", "missing"])
        with self.assertRaises(EvidenceContractError):
            validate_prospective_intake(raw, missing)

    def test_unsupported_input_and_safe_default(self):
        self.assertEqual(main([]), 0)
        with self.assertRaises(EvidenceContractError):
            validate_prospective_intake(b"[]", {"raw_sha256": "0"*64})
        with self.assertRaises(EvidenceContractError):
            validate_prospective_intake(b'{"not":"list"}', encode_records(sample_records())[1])


if __name__ == "__main__":
    unittest.main()
