"""Exact arithmetic and fail-closed scientific decision tests for synthetic v9."""
import base64
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from bhs.decisions.evidence_contract_v7 import REQUIRED
from bhs.decisions.verified_review_v8 import (
    create_unsigned_review_packet, guarded_assessment,
)
from bhs.decisions.causal_nonidentifiability_v9 import (
    CausalWorld, LatentCase, counterexample_worlds, observed_law,
    intervention_mean, identification_audit, guarded_causal_review, main,
)

NOW = datetime(2026, 11, 7, 7, 0, tzinfo=timezone.utc)


def synthetic_review():
    ev = {k: {"status": "verified", "source_ref": "fixture:" + k}
          for k in REQUIRED["laboratory"]}
    r = {
        "lower_success_probability": 0.99,
        "benefit_if_correct": 1.0,
        "harm_if_wrong": 3.0,
        "abstention_cost": 0.1,
        "lower_bound_provenance": "fixture:independent_performance_evidence",
        "benefit_unit": "synthetic_units",
        "harm_unit": "synthetic_units",
        "abstention_unit": "synthetic_units",
        "utility_units": "synthetic_units",
        "lower_bound_method": "invented mathematical test case",
        "validation_population": "not real; synthetic cases only",
    }
    private = Ed25519PrivateKey.generate()
    reviewer = "synthetic-reviewer"
    packet = create_unsigned_review_packet(
        reviewer, ev, r, (NOW - timedelta(hours=1)).isoformat(),
        (NOW + timedelta(hours=1)).isoformat(),
    )
    msg = json.dumps(packet, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode()
    att = {
        "reviewer_id": reviewer,
        "packet": packet,
        "signature_b64": base64.b64encode(private.sign(msg)).decode(),
    }
    pub = base64.b64encode(private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
    trust = {reviewer: {
        "role": "independent_lab_reviewer",
        "public_key_b64": pub,
    }}
    return ev, r, att, trust


class CausalIdentifiabilityTests(unittest.TestCase):
    def test_observed_distribution_exactly_equal(self):
        a, b = counterexample_worlds()
        self.assertEqual(observed_law(a), observed_law(b))
        self.assertEqual(observed_law(a), {
            (0, Fraction(30)): Fraction(1, 2),
            (1, Fraction(30)): Fraction(1, 2),
        })

    def test_same_observed_y_but_opposite_do_effects(self):
        positive, negative = counterexample_worlds()
        self.assertEqual(intervention_mean(positive, 0), Fraction(30))
        self.assertEqual(intervention_mean(positive, 1), Fraction(35))
        self.assertEqual(intervention_mean(negative, 0), Fraction(35))
        self.assertEqual(intervention_mean(negative, 1), Fraction(30))

    def test_no_conditional_action_overlap_in_both_worlds(self):
        for world in counterexample_worlds():
            self.assertEqual({c.observed_action for c in world.cases}, {0, 1})
            self.assertTrue(all(c.observed_action == int(c.name[-1])
                                for c in world.cases))
            # Within either latent stratum, only one action is ever observed.
            self.assertEqual(len(world.cases), 2)

    def test_identification_must_abstain(self):
        r = identification_audit(counterexample_worlds())
        self.assertTrue(r["observational_law_identical"])
        self.assertEqual(r["causal_effect_range_within_declared_world_set"], [-5.0, 5.0])
        self.assertEqual(r["status"], "ABSTAIN_CAUSAL_EFFECT_NOT_IDENTIFIED")
        self.assertFalse(r["identification_proven_from_observations"])
        self.assertFalse(r["physical_validation"])

    def test_optimal_deterministic_policies_have_worst_regret_five(self):
        loss = identification_audit(counterexample_worlds())["conditional_illustrative_regret"]
        self.assertEqual(loss["always_choose_action_zero_worst"], 5.0)
        self.assertEqual(loss["always_choose_action_one_worst"], 5.0)

    def test_minimax_randomized_action_has_regret_two_point_five(self):
        loss = identification_audit(counterexample_worlds())["conditional_illustrative_regret"]
        self.assertEqual(loss["minimax_action_one_probability"], 0.5)
        self.assertEqual(loss["minimax_randomized_action_worst"], 2.5)

    def test_abstention_preferred_only_for_declared_illustrative_cost(self):
        good = identification_audit(counterexample_worlds(), Fraction(1))
        bad = identification_audit(counterexample_worlds(), Fraction(3))
        self.assertTrue(good["conditional_illustrative_regret"][
            "abstention_minimax_preferred_for_this_world_set"])
        self.assertFalse(bad["conditional_illustrative_regret"][
            "abstention_minimax_preferred_for_this_world_set"])

    def test_invalid_latent_probability_sum_rejected(self):
        plus, minus = counterexample_worlds()
        wrong = CausalWorld("bad", (
            LatentCase("u0", Fraction(2, 3), 0, Fraction(30), Fraction(40)),
            LatentCase("u1", Fraction(1, 2), 1, Fraction(30), Fraction(30)),
        ))
        with self.assertRaisesRegex(ValueError, "LATENT_WEIGHTS_MUST_SUM_TO_ONE"):
            identification_audit((wrong, minus))

    def test_observationally_different_worlds_do_not_count_as_witnesses(self):
        plus, minus = counterexample_worlds()
        different = CausalWorld("different", (
            LatentCase("u0", Fraction(1, 2), 0, Fraction(29), Fraction(30)),
            LatentCase("u1", Fraction(1, 2), 1, Fraction(40), Fraction(30)),
        ))
        with self.assertRaisesRegex(ValueError, "WITNESSES_DIFFER_OBSERVATIONALLY"):
            identification_audit((plus, different))

    def test_one_world_is_not_identification_proof(self):
        plus, _ = counterexample_worlds()
        with self.assertRaisesRegex(ValueError, "AT_LEAST_TWO"):
            identification_audit((plus,))

    def test_no_opposing_signs_does_not_prove_identification(self):
        plus, _ = counterexample_worlds()
        same_conclusion = CausalWorld("different_name", plus.cases)
        r = identification_audit((plus, same_conclusion))
        self.assertEqual(r["status"], "REQUEST_ADDITIONAL_IDENTIFICATION_ASSUMPTIONS")
        self.assertFalse(r["identification_proven_from_observations"])

    def test_existing_v8_missing_evidence_cannot_be_overridden(self):
        ev, risk, att, trust = synthetic_review()
        ev["curing_conditions"] = {"status": "missing"}
        r = guarded_causal_review("laboratory", ev, risk=risk, attestation=att,
                                   trusted_reviewers=trust,
                                   witnesses=counterexample_worlds(), now=NOW)
        self.assertEqual(r["status"], "REQUEST_ADDITIONAL_EVIDENCE")
        self.assertFalse(r["automatic_laboratory_action_authorized"])

    def test_even_signed_v8_review_is_not_a_causal_identification(self):
        ev, risk, att, trust = synthetic_review()
        old = guarded_assessment("laboratory", ev, risk=risk, attestation=att,
                                 trusted_reviewers=trust, now=NOW)
        self.assertEqual(old["status"], "ELIGIBLE_FOR_EXPERT_REVIEW")
        new = guarded_causal_review("laboratory", ev, risk=risk, attestation=att,
                                    trusted_reviewers=trust,
                                    witnesses=counterexample_worlds(), now=NOW)
        self.assertEqual(new["status"], "ABSTAIN_CAUSAL_NONIDENTIFIABILITY")
        self.assertEqual(new["causal_witness_effect_range"], [-5.0, 5.0])
        self.assertFalse(new["automatic_laboratory_action_authorized"])

    def test_without_declared_worlds_cannot_claim_identification(self):
        ev, risk, att, trust = synthetic_review()
        r = guarded_causal_review("laboratory", ev, risk=risk, attestation=att,
                                   trusted_reviewers=trust, witnesses=None, now=NOW)
        self.assertEqual(r["status"], "REQUEST_CAUSAL_IDENTIFICATION_EVIDENCE")
        self.assertFalse(r["causal_identification_verified"])

    def test_synthetic_regression_does_not_use_real_measurement_data(self):
        r = identification_audit(counterexample_worlds())
        self.assertFalse(r["new_empirical_data_used"])
        self.assertFalse(r["independent_holdout_used"])
        self.assertFalse(r["automatic_laboratory_action_authorized"])
        self.assertIn("fabricated", r["source_observations"])

    def test_cli_output_contains_proof_and_does_not_fetch_data(self):
        with tempfile.TemporaryDirectory() as root:
            dest = Path(root) / "example.json"
            self.assertEqual(main(["--out", str(dest)]), 0)
            result = json.loads(dest.read_text())
            self.assertEqual(result["status"], "ABSTAIN_CAUSAL_EFFECT_NOT_IDENTIFIED")
            self.assertEqual(result["observational_law"][0]["observed_response"], 30.0)


if __name__ == "__main__":
    unittest.main()
