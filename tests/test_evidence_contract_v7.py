"""v7 contracts: selection between evidence requests, refusal and expert review."""
import json
import unittest
from pathlib import Path

from bhs.decisions.evidence_contract_v7 import REQUIRED, assess, v6_source_case


def verified(level="laboratory"):
    return {key: {"status": "verified", "source_ref": "document:" + key}
            for key in REQUIRED[level]}


def risk(lower, harm=4, benefit=1, abstain_cost=0.1, provenance="document:independent_performance_evidence"):
    return {
        "lower_success_probability": lower,
        "benefit_if_correct": benefit,
        "harm_if_wrong": harm,
        "abstention_cost": abstain_cost,
        "lower_bound_provenance": provenance,
        "utility_units": "synthetic illustrative utility points",
    }


class EvidenceContractTests(unittest.TestCase):
    def test_incomplete_realistic_uci_lab_context_requests_data(self):
        d = verified("descriptive")
        out = assess("laboratory", d)
        self.assertEqual(out["status"], "REQUEST_ADDITIONAL_EVIDENCE")
        self.assertIn("controlled_intervention", out["evidence_requested"])
        self.assertFalse(out["automatic_laboratory_action_authorized"])

    def test_source_contradiction_abstains_and_overrides_missing(self):
        d = verified("descriptive")
        d["source_integrity"]["status"] = "contradicted"
        out = assess("laboratory", d)
        self.assertEqual(out["status"], "ABSTAIN_CONTRADICTED_ASSUMPTIONS")
        self.assertIn("CONTRADICTED:source_integrity", out["reason_codes"])

    def test_verified_without_referenced_source_fails_closed(self):
        d = verified("laboratory")
        d["instrument_calibration"]["source_ref"] = ""
        out = assess("laboratory", d, risk=risk(0.99))
        self.assertEqual(out["status"], "ABSTAIN_INVALID_PROVENANCE")

    def test_missing_risk_prevents_action_even_if_fields_complete(self):
        out = assess("laboratory", verified())
        self.assertEqual(out["status"], "ABSTAIN_UNBOUNDED_DECISION_RISK")

    def test_unsupported_risk_source_prevents_action(self):
        out = assess("laboratory", verified(), risk=risk(0.99, provenance="unrelated:record"))
        self.assertEqual(out["status"], "ABSTAIN_INVALID_RISK_PROVENANCE")

    def test_unacceptable_worst_case_risk_refuses(self):
        out = assess("laboratory", verified(), risk=risk(0.5))
        self.assertEqual(out["status"], "ABSTAIN_RISK_NOT_ACCEPTABLE")
        self.assertLess(out["risk_assessment"]["decision_margin"], 0)

    def test_eligible_only_for_human_review_not_auto_action(self):
        out = assess("laboratory", verified(), risk=risk(0.98))
        self.assertEqual(out["status"], "ELIGIBLE_FOR_EXPERT_REVIEW")
        self.assertGreater(out["risk_assessment"]["decision_margin"], 0)
        self.assertFalse(out["automatic_laboratory_action_authorized"])
        self.assertTrue(out["risk_assessment"]["risk_values_are_self_reported"])

    def test_equal_utility_abstains(self):
        # With benefit=harm=1 and abstention cost=0, at p=0.5 utilities tie.
        out = assess("laboratory", verified(), risk=risk(0.5, harm=1, benefit=1, abstain_cost=0))
        self.assertEqual(out["status"], "ABSTAIN_RISK_NOT_ACCEPTABLE")

    def test_malformed_probability_and_costs_abstain(self):
        for lower in (-0.1, 1.1, float("nan"), float("inf")):
            out = assess("laboratory", verified(), risk=risk(lower))
            self.assertEqual(out["status"], "ABSTAIN_INVALID_RISK_INPUT")
        self.assertEqual(
            assess("laboratory", verified(), risk=risk(0.99, harm=-3))["status"],
            "ABSTAIN_INVALID_RISK_INPUT"
        )

    def test_descriptive_and_observational_never_authorize_lab(self):
        out1 = assess("descriptive", verified("descriptive"))
        self.assertEqual(out1["status"], "DESCRIPTIVE_REPORT_ONLY")
        out2 = assess("observational", verified("observational"))
        self.assertEqual(out2["status"], "OBSERVATIONAL_REVIEW_ONLY")
        self.assertFalse(out1["automatic_laboratory_action_authorized"])
        self.assertFalse(out2["automatic_laboratory_action_authorized"])

    def test_unknown_evidence_status_rejected(self):
        d=verified("descriptive")
        d["schema_and_units"]["status"]="maybe"
        self.assertEqual(assess("descriptive", d)["status"], "ABSTAIN_INVALID_INPUT")

    def test_v6_real_evidence_source_has_no_invented_metadata(self):
        source = json.loads(Path("research/uci_concrete_assumptions_v6.json").read_text())
        d = v6_source_case(source)
        self.assertEqual(d["curing_conditions"]["status"], "missing")
        self.assertEqual(assess("laboratory", d)["status"], "REQUEST_ADDITIONAL_EVIDENCE")
        self.assertEqual(assess("descriptive", d)["status"], "DESCRIPTIVE_REPORT_ONLY")
        broken = json.loads(json.dumps(source))
        broken["source"]["parsed_table_sha256"] = "wrong"
        with self.assertRaises(ValueError):
            v6_source_case(broken)


if __name__ == "__main__":
    unittest.main()
