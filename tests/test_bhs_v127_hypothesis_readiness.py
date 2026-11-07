"""Adversarial contracts for the Fe-Co-Ni hypothesis-to-measurement passport."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.bhs_v127_hypothesis_readiness import (
    PASSPORT_PATH, PilotContractError, audit_passport_bytes,
    main, parse_passport, validate_passport,
)


def example():
    return json.loads(PASSPORT_PATH.read_text(encoding="utf-8"))


def encode(data):
    return (json.dumps(data, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


class HypothesisReadinessContracts(unittest.TestCase):
    def test_candidate_has_explicit_no_go_and_scientific_blockers(self):
        raw = PASSPORT_PATH.read_bytes()
        report = audit_passport_bytes(raw)
        self.assertEqual(report["schema_version"], "BHS-V12.7")
        self.assertEqual(report["passport_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertTrue(report["structural_contract_passed"])
        self.assertGreaterEqual(report["blocking_count"], 20)
        self.assertIn("design.minimum_meaningful_effect_A_per_m",
                      report["blocking_fields"])
        self.assertIn("governance.lab_partner_confirmed", report["blocking_fields"])
        self.assertFalse(report["laboratory_action_allowed"])
        self.assertFalse(report["independent_physical_validation_established"])
        self.assertFalse(report["posterior_calibration_established"])
        self.assertEqual(report["decision"], "NO_GO_EXTERNAL_REVIEW_REQUIRED")

    def test_reordered_json_preserves_structure_but_changes_raw_hash(self):
        data = example()
        one = audit_passport_bytes(encode(data))
        raw = json.dumps(data, separators=(",", ":"), sort_keys=False).encode()
        two = audit_passport_bytes(raw)
        self.assertEqual(one["blocking_fields"], two["blocking_fields"])
        self.assertNotEqual(one["passport_sha256"], two["passport_sha256"])

    def test_duplicate_json_keys_and_nonfinite_json_rejected(self):
        with self.assertRaisesRegex(PilotContractError, "DUPLICATE_JSON_KEY"):
            parse_passport(b'{"a":1,"a":2}')
        with self.assertRaises(PilotContractError):
            parse_passport(b'{"value":NaN}')
        with self.assertRaises(PilotContractError):
            parse_passport(b"")
        with self.assertRaises(PilotContractError):
            parse_passport(b"x" * 130_000)

    def test_unknown_root_and_nested_fields_rejected(self):
        data = example()
        data["unverified_raw_measurement"] = [10.0]
        with self.assertRaisesRegex(PilotContractError, "INVALID_ROOT_FIELDS"):
            validate_passport(data)
        data = example()
        data["design"]["response_fitted_on_evaluation_labels"] = True
        with self.assertRaisesRegex(PilotContractError, "INVALID_DESIGN_FIELDS"):
            validate_passport(data)

    def test_no_approved_status_via_manifest_change(self):
        data = example()
        data["status"] = "laboratory_approved"
        with self.assertRaises(PilotContractError):
            validate_passport(data)
        data = example()
        data["material_system"] = "unknown substance"
        with self.assertRaises(PilotContractError):
            validate_passport(data)

    def test_duplicate_prediction_or_falsifier_rejected(self):
        for key in ("prediction", "falsifier"):
            data = example()
            data["hypotheses"][1][key] = data["hypotheses"][0][key]
            with self.subTest(key=key):
                with self.assertRaisesRegex(PilotContractError, "NOT_DISTINGUISHABLE"):
                    validate_passport(data)

    def test_missing_or_unmeasurable_hypothesis_rejected(self):
        data = example()
        data["hypotheses"] = data["hypotheses"][:1]
        with self.assertRaises(PilotContractError):
            validate_passport(data)
        data = example()
        data["hypotheses"][0]["prediction"] = "TBD"
        with self.assertRaises(PilotContractError):
            validate_passport(data)
        data = example()
        data["hypotheses"][1]["unit"] = "mT"
        with self.assertRaises(PilotContractError):
            validate_passport(data)

    def test_unit_and_raw_trace_contracts_rejected(self):
        for key, value in (
            ("primary_unit", "mT"),
            ("primary_observable", "saturation"),
            ("method", "unidentified scanner"),
            ("raw_trace_retention", False),
        ):
            data = example()
            data["readout"][key] = value
            with self.subTest(key=key):
                with self.assertRaisesRegex(PilotContractError, "PRIMARY_MEASUREMENT"):
                    validate_passport(data)

    def test_fabricated_holdout_or_prospective_evidence_claim_rejected(self):
        for field in (
            "historical_nist_used_as_holdout",
            "new_prospective_measurements_available",
            "independent_validation_available",
            "authentic_measurement_log_verified",
        ):
            data = example()
            data["evidence"][field] = True
            with self.subTest(field=field):
                with self.assertRaisesRegex(PilotContractError, "UNSUPPORTED_PHYSICAL"):
                    validate_passport(data)

    def test_release_flags_are_hard_disabled(self):
        for field in ("requested", "physical_action_allowed",
                      "generalization_claim_allowed"):
            data = example()
            data["release"][field] = True
            with self.subTest(field=field):
                with self.assertRaisesRegex(PilotContractError, "PROHIBITED_RELEASE"):
                    validate_passport(data)

    def test_group_overlap_and_duplicate_groups_fail(self):
        data = example()
        data["design"]["calibration_group_ids"] = ["batch-1"]
        data["design"]["evaluation_group_ids"] = ["batch-1"]
        with self.assertRaisesRegex(PilotContractError, "GROUP_OVERLAP"):
            validate_passport(data)
        data["design"]["evaluation_group_ids"] = ["batch-2", "batch-2"]
        with self.assertRaisesRegex(PilotContractError, "DUPLICATE_EVALUATION"):
            validate_passport(data)

    def test_group_partitions_do_not_claim_independence(self):
        data = example()
        data["design"]["calibration_group_ids"] = ["batch-cal"]
        data["design"]["evaluation_group_ids"] = ["batch-eval"]
        report = validate_passport(data)
        self.assertNotIn("design.calibration_group_ids", report["blocking_fields"])
        self.assertNotIn("design.evaluation_group_ids", report["blocking_fields"])
        self.assertFalse(report["independent_physical_validation_established"])
        data["design"]["independence_unit"] = "measurement_order"
        with self.assertRaisesRegex(PilotContractError, "INDEPENDENCE_UNIT"):
            validate_passport(data)

    def test_nonpositive_effect_uncertainty_and_cost_rejected(self):
        for field, value in [
            ("minimum_meaningful_effect_A_per_m", 0.0),
            ("measurement_uncertainty_A_per_m", -1),
        ]:
            data = example()
            data["design"][field] = value
            with self.subTest(field=field):
                with self.assertRaises(PilotContractError):
                    validate_passport(data)
        for field, value in [
            ("response_budget", True),
            ("per_measurement_cost", 0.0),
            ("measurement_seconds", float("inf")),
            ("abstention_cost", -2.0),
        ]:
            data = example()
            data["resources"][field] = value
            with self.subTest(field=field):
                with self.assertRaises(PilotContractError):
                    validate_passport(data)

    def test_verification_flags_are_strict_booleans(self):
        data = example()
        data["governance"]["lab_partner_confirmed"] = "true"
        with self.assertRaisesRegex(PilotContractError, "INVALID_GOVERNANCE"):
            validate_passport(data)
        data = example()
        data["readout"]["instrument_field_calibration_verified"] = 1
        with self.assertRaisesRegex(PilotContractError, "INVALID_READOUT_VERIFICATION"):
            validate_passport(data)

    def test_placeholder_strings_do_not_complete_evidence(self):
        for field in ("randomization_plan", "missing_data_plan"):
            data = example()
            data["design"][field] = "TBD"
            report = validate_passport(data)
            self.assertIn("design." + field, report["blocking_fields"])
        data = example()
        data["evidence"]["source_license"] = "unknown"
        report = validate_passport(data)
        self.assertIn("evidence.source_license", report["blocking_fields"])

    def test_approval_looking_metadata_does_not_authorize_operations(self):
        data = example()
        for field in data["governance"]:
            data["governance"][field] = True
        for field in ("instrument_field_calibration_verified",
                      "structural_instrument_calibration_verified"):
            data["readout"][field] = True
        data["design"]["composition_verified"] = True
        data["design"]["calibration_group_ids"] = ["batch-cal-001"]
        data["design"]["evaluation_group_ids"] = ["batch-eval-001"]
        for field in ("randomization_plan", "processing_conditions",
                      "substrate_control", "thickness_control",
                      "structural_contrast_definition",
                      "sample_size_and_precision_plan",
                      "measurement_chronology_plan", "missing_data_plan"):
            data["design"][field] = "Declared hypothetical reference, not independently verified."
        data["design"]["minimum_meaningful_effect_A_per_m"] = 100.0
        data["design"]["measurement_uncertainty_A_per_m"] = 10.0
        data["resources"].update({
            "response_budget": 48, "per_measurement_cost": 7.0,
            "cost_unit": "declared units", "abstention_cost": 0.0,
            "measurement_seconds": 30.0,
        })
        data["evidence"]["source_sha256"] = "0" * 64
        data["evidence"]["source_license"] = "declared-license"
        report = validate_passport(data)
        self.assertEqual(report["blocking_count"], 0)
        self.assertFalse(report["has_external_scientific_review"])
        self.assertFalse(report["physical_recommendation_allowed"])
        self.assertFalse(report["laboratory_action_allowed"])
        self.assertFalse(report["independent_physical_validation_established"])
        self.assertEqual(report["decision"], "NO_GO_EXTERNAL_REVIEW_REQUIRED")

    def test_source_digest_structure_and_references(self):
        data = example()
        data["evidence"]["source_sha256"] = "not-a-digest"
        with self.assertRaisesRegex(PilotContractError, "INVALID_EVIDENCE_SHA256"):
            validate_passport(data)
        data = example()
        data["references"] += [data["references"][0]]
        with self.assertRaisesRegex(PilotContractError, "INVALID_PRIOR_RESEARCH"):
            validate_passport(data)

    def test_cli_requires_explicit_paths_and_does_not_score(self):
        self.assertEqual(main([]), 0)
        with TemporaryDirectory() as tmp:
            outfile = Path(tmp) / "report.json"
            self.assertEqual(main(["--passport", str(PASSPORT_PATH),
                                   "--out", str(outfile)]), 0)
            report = json.loads(outfile.read_text())
            self.assertFalse(report["physical_recommendation_allowed"])
            self.assertFalse(report["independent_physical_validation_established"])
            self.assertGreater(report["blocking_count"], 0)


if __name__ == "__main__":
    unittest.main()
