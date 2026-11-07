"""Constructive causal non-identifiability witness and conservative decision guard.

This module demonstrates a known identifiability limit with synthetic structural
models. It neither discovers a physical mechanism nor proves any laboratory
probability, outcome, or improvement over competing decision systems.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from bhs.decisions.verified_review_v8 import guarded_assessment


@dataclass(frozen=True)
class LatentCase:
    name: str
    probability: Fraction
    observed_action: int
    outcome_if_zero: Fraction
    outcome_if_one: Fraction


@dataclass(frozen=True)
class CausalWorld:
    name: str
    cases: tuple[LatentCase, ...]


def counterexample_worlds() -> tuple[CausalWorld, CausalWorld]:
    """Two models with identical observational law and opposite intervention effects.

    Latent U is uniformly 0/1, observed action A=U, observed Y=30 in both.
    Unobserved potential outcomes differ, so intervention signs are opposite.
    All numbers are invented and in illustrative response units, NOT MPa data.
    """
    half = Fraction(1, 2)
    increase = CausalWorld("positive_intervention_effect", (
        LatentCase("u0", half, 0, Fraction(30), Fraction(40)),
        LatentCase("u1", half, 1, Fraction(30), Fraction(30)),
    ))
    decrease = CausalWorld("negative_intervention_effect", (
        LatentCase("u0", half, 0, Fraction(30), Fraction(30)),
        LatentCase("u1", half, 1, Fraction(40), Fraction(30)),
    ))
    return increase, decrease


def _validate(world: CausalWorld) -> None:
    if not isinstance(world, CausalWorld) or not world.name or not world.cases:
        raise ValueError("INVALID_WORLD")
    names = set()
    total = Fraction()
    for case in world.cases:
        if not isinstance(case, LatentCase) or not case.name or case.name in names:
            raise ValueError("INVALID_LATENT_CASE")
        names.add(case.name)
        if type(case.observed_action) is not int or case.observed_action not in (0, 1):
            raise ValueError("INVALID_OBSERVED_ACTION")
        vals = (case.probability, case.outcome_if_zero, case.outcome_if_one)
        if any(not isinstance(v, Fraction) for v in vals):
            raise ValueError("NONRATIONAL_MODEL_INPUT")
        if case.probability <= 0:
            raise ValueError("NONPOSITIVE_LATENT_WEIGHT")
        total += case.probability
    if total != 1:
        raise ValueError("LATENT_WEIGHTS_MUST_SUM_TO_ONE")


def observed_law(world: CausalWorld) -> dict[tuple[int, Fraction], Fraction]:
    """Exact observational P(A,Y); potential outcomes are *not* observed."""
    _validate(world)
    result: dict[tuple[int, Fraction], Fraction] = {}
    for case in world.cases:
        y = case.outcome_if_one if case.observed_action else case.outcome_if_zero
        key = (case.observed_action, y)
        result[key] = result.get(key, Fraction()) + case.probability
    return result


def intervention_mean(world: CausalWorld, do_action: int) -> Fraction:
    _validate(world)
    if type(do_action) is not int or do_action not in (0, 1):
        raise ValueError("INVALID_INTERVENTION")
    return sum((c.probability * (c.outcome_if_one if do_action else c.outcome_if_zero)
                for c in world.cases), Fraction())


def _possible_pair_intersections(lines: list[tuple[Fraction, Fraction]]):
    """For lines loss(q)=intercept + q*slope, collect minimax breakpoints."""
    candidates = {Fraction(0), Fraction(1)}
    for i, (bi, mi) in enumerate(lines):
        for bj, mj in lines[i + 1:]:
            if mi != mj:
                x = (bj - bi) / (mi - mj)
                if 0 <= x <= 1:
                    candidates.add(x)
    return candidates


def identification_audit(worlds: Iterable[CausalWorld],
                         abstention_loss: Fraction = Fraction(1)) -> dict:
    """Conditional to a predeclared world family; it never proves completeness."""
    world_set = tuple(worlds)
    if len(world_set) < 2 or len({w.name for w in world_set}) != len(world_set):
        raise ValueError("AT_LEAST_TWO_DISTINCT_WORLDS_REQUIRED")
    if not isinstance(abstention_loss, Fraction) or abstention_loss < 0:
        raise ValueError("INVALID_ABSTENTION_LOSS")
    laws = [observed_law(w) for w in world_set]
    if any(law != laws[0] for law in laws[1:]):
        raise ValueError("WITNESSES_DIFFER_OBSERVATIONALLY")

    means = [(intervention_mean(w, 0), intervention_mean(w, 1)) for w in world_set]
    effects = [m1 - m0 for m0, m1 in means]
    # Regret assumes greater outcome is preferred and abstracts away action costs.
    regret_lines = []
    for m0, m1 in means:
        best = max(m0, m1)
        regret0, regret1 = best - m0, best - m1
        regret_lines.append((regret0, regret1 - regret0))

    worst0 = max(intercept for intercept, _ in regret_lines)
    worst1 = max(intercept + slope for intercept, slope in regret_lines)
    random_candidates = _possible_pair_intersections(regret_lines)
    opt_random_p = min(
        random_candidates,
        key=lambda p: (max(intercept + slope * p
                           for intercept, slope in regret_lines), p),
    )
    opt_random_loss = max(intercept + slope * opt_random_p
                          for intercept, slope in regret_lines)

    identical_observed = [
        {"action": action, "observed_response": float(y), "probability": float(p)}
        for (action, y), p in sorted(laws[0].items())
    ]
    opposite_effects = min(effects) < 0 < max(effects)
    return {
        "study": "BHS v9 constructive causal non-identifiability demonstration",
        "type": "EXACT_SYNTHETIC_STRUCTURAL_COUNTEREXAMPLE",
        "source_observations": "fabricated mathematical example, no UCI observations used",
        "observational_law_identical": True,
        "observational_law": identical_observed,
        "world_results": [
            {"name": world.name, "mean_do_zero": float(means[i][0]),
             "mean_do_one": float(means[i][1]),
             "average_intervention_effect": float(effects[i])}
            for i, world in enumerate(world_set)
        ],
        "causal_effect_range_within_declared_world_set": [
            float(min(effects)), float(max(effects))
        ],
        "opposite_effect_signs_present": opposite_effects,
        "status": ("ABSTAIN_CAUSAL_EFFECT_NOT_IDENTIFIED" if opposite_effects
                   else "REQUEST_ADDITIONAL_IDENTIFICATION_ASSUMPTIONS"),
        "conditional_illustrative_regret": {
            "always_choose_action_zero_worst": float(worst0),
            "always_choose_action_one_worst": float(worst1),
            "minimax_action_one_probability": float(opt_random_p),
            "minimax_randomized_action_worst": float(opt_random_loss),
            "abstention_loss_assumed": float(abstention_loss),
            "abstention_minimax_preferred_for_this_world_set": (
                abstention_loss < min(worst0, worst1, opt_random_loss)
            ),
            "numbers_are_assumptions_not_measured_decision_costs": True,
        },
        "assumption_failures": [
            "UNOBSERVED_RELEVANT_CONTEXT",
            "NO_ACTION_OVERLAP_CONDITIONAL_ON_LATENT_CONTEXT",
            "OBSERVATIONAL_DISTRIBUTION_DOES_NOT_IDENTIFY_INTERVENTION_EFFECT",
        ],
        "identification_proven_from_observations": False,
        "world_set_completeness_established": False,
        "new_empirical_data_used": False,
        "independent_holdout_used": False,
        "physical_validation": False,
        "automatic_laboratory_action_authorized": False,
    }


def guarded_causal_review(level, evidence, *, risk=None, attestation=None,
                          trusted_reviewers=None, witnesses=None, now=None):
    """Never escalate v8; reject signed but causally ambiguous advice.

    A finite user-supplied set of worlds can *falsify* identifiability when it
    contains observationally identical opposing effects, but a set with no
    opposing example cannot certify identifiability. Expert review remains.
    """
    base = guarded_assessment(
        level, evidence, risk=risk, attestation=attestation,
        trusted_reviewers=trusted_reviewers, now=now,
    )
    if base["status"] != "ELIGIBLE_FOR_EXPERT_REVIEW":
        return dict(base, causal_identification_verified=False)
    if witnesses is None:
        return dict(
            base, status="REQUEST_CAUSAL_IDENTIFICATION_EVIDENCE",
            reason_codes=["NO_EXPLICIT_CAUSAL_IDENTIFICATION_ARGUMENT"],
            causal_identification_verified=False,
            automatic_laboratory_action_authorized=False,
        )
    try:
        report = identification_audit(witnesses)
    except (TypeError, ValueError, AttributeError):
        return dict(
            base, status="ABSTAIN_INVALID_CAUSAL_WITNESSES",
            reason_codes=["CAUSAL_WITNESS_CONTRACT_FAILED"],
            causal_identification_verified=False,
            automatic_laboratory_action_authorized=False,
        )
    if report["opposite_effect_signs_present"]:
        return dict(
            base, status="ABSTAIN_CAUSAL_NONIDENTIFIABILITY",
            reason_codes=["OBSERVATIONALLY_EQUIVALENT_WORLDS_REQUIRE_OPPOSITE_ACTIONS"],
            causal_witness_effect_range=report["causal_effect_range_within_declared_world_set"],
            causal_identification_verified=False,
            automatic_laboratory_action_authorized=False,
        )
    return dict(
        base, status="REQUEST_CAUSAL_IDENTIFICATION_EVIDENCE",
        reason_codes=["FINITE_WITNESS_SET_CANNOT_CERTIFY_ALL_PLAUSIBLE_MODELS"],
        causal_identification_verified=False,
        automatic_laboratory_action_authorized=False,
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="runs/bhs_v9_nonidentifiability.json")
    args = parser.parse_args(argv)
    result = identification_audit(counterexample_worlds())
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"],
                      "possible_causal_effects": result["causal_effect_range_within_declared_world_set"],
                      "observational_law_identical": result["observational_law_identical"]},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
