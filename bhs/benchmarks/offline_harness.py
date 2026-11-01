"""Leakage-resistant synthetic benchmark software harness; NOT materials results.

The oracle's labels are private to the runner. Each policy sees only opaque IDs,
public features and earlier revealed observations. This is not an empirical BHS
hypothesis policy or calibrated evidence model.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import random
from typing import Mapping

STATUS = "SYNTHETIC_SOFTWARE_TEST_NOT_MATERIALS_BENCHMARK"


@dataclass(frozen=True)
class Candidate:
    identifier: str
    feature: float


@dataclass(frozen=True)
class Observation:
    identifier: str
    value: float


@dataclass(frozen=True)
class View:
    remaining: tuple[Candidate, ...]
    observations: tuple[Observation, ...]
    queries_left: int


class Oracle:
    """An evaluation oracle: no method for policies to read unrevealed labels."""

    def __init__(self, labels: Mapping[str, float]):
        if not labels or any(not isinstance(k, str) or not k for k in labels):
            raise ValueError("Nonempty valid label identifiers required")
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in labels.values()):
            raise ValueError("Labels must be finite numeric values")
        self.__labels = dict(labels)

    def evaluate(self, identifier: str) -> float:
        return float(self.__labels[identifier])

    def identifiers(self) -> frozenset[str]:
        return frozenset(self.__labels)


class RandomWithoutReplacement:
    def __init__(self, seed: int):
        self._rng = random.Random(seed)

    def choose(self, view: View) -> str:
        return self._rng.choice(view.remaining).identifier


class PublicFeatureRanking:
    """Illustrative nonadaptive ranking by public feature, not a trained baseline."""

    def choose(self, view: View) -> str:
        return max(view.remaining, key=lambda c: (c.feature, c.identifier)).identifier


def run_trial(candidates: tuple[Candidate, ...], oracle: Oracle, policy, *, budget: int, seed: int):
    """Run exactly budget distinct oracle queries; keep query-level provenance."""
    if not isinstance(budget, int) or isinstance(budget, bool) or not 1 <= budget <= len(candidates):
        raise ValueError("budget must be an integer between 1 and number of candidates")
    ids = [c.identifier for c in candidates]
    if len(ids) != len(set(ids)) or not all(ids) or set(ids) != oracle.identifiers():
        raise ValueError("Candidate identifiers must be unique and match oracle IDs")
    if any(isinstance(c.feature, bool) or not isinstance(c.feature, (int, float)) or not math.isfinite(c.feature) for c in candidates):
        raise ValueError("Public candidate features must be finite numbers")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    if not callable(getattr(policy, "choose", None)):
        raise TypeError("policy requires choose(view) method")

    remaining = {c.identifier: c for c in candidates}
    observations: list[Observation] = []
    history = []
    best = -math.inf
    # The runner intentionally never passes oracle, labels, or all candidates'
    # hidden values to the policy. It constructs a fresh immutable public view.
    for step in range(1, budget + 1):
        view = View(remaining=tuple(remaining.values()), observations=tuple(observations), queries_left=budget-step+1)
        identifier = policy.choose(view)
        if not isinstance(identifier, str) or identifier not in remaining:
            raise ValueError("Policy selected an invalid or previously queried candidate")
        value = oracle.evaluate(identifier)
        remaining.pop(identifier)
        observations.append(Observation(identifier, value))
        best = max(best, value)
        history.append({"step": step, "candidate_id": identifier, "observed_value": value, "best_so_far": best})

    payload = {"status": STATUS, "seed": seed, "query_budget": budget, "query_count": len(history), "query_log": history,
               "disclaimer": "Software-only synthetic ground truth; no materials or CHGNet result."}
    payload["log_sha256"] = hashlib.sha256(json.dumps(payload["query_log"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def synthetic_example(seed: int = 17, budget: int = 3):
    # Values below are intentionally invented for software unit tests ONLY.
    candidates = (Candidate("synthetic_A", 0.1), Candidate("synthetic_B", 0.8), Candidate("synthetic_C", 0.4), Candidate("synthetic_D", 0.6))
    ground_truth = Oracle({"synthetic_A": 0.9, "synthetic_B": 0.1, "synthetic_C": 0.7, "synthetic_D": 0.2})
    return {
        "random": run_trial(candidates, ground_truth, RandomWithoutReplacement(seed), budget=budget, seed=seed),
        "public_feature_ranking": run_trial(candidates, ground_truth, PublicFeatureRanking(), budget=budget, seed=seed),
    }


if __name__ == "__main__":
    print(json.dumps(synthetic_example(), indent=2))
