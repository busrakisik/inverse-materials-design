"""BHS v12.1: representation-invariant observed-response interface.

Only an already revealed measurement multiset is canonicalized. This does not
model chronology, remove measurement noise or establish laboratory behavior.
The historical evaluator and all original v12 policies remain unchanged.
"""
from __future__ import annotations

from collections.abc import Mapping

from scripts.bhs_measurement_allocation_v12 import (
    MeasurementContractError,
    acquisition_view,
    select_measurement,
)


def canonical_revealed_state(candidate_features, observed: Mapping[int, tuple[float, ...]]):
    """Normalize *representation* of the same finite, revealed response multiset.

    Candidate IDs and their observed values are public inputs to a selector;
    no source oracle, unseen response or extra label is consulted. Sorting
    within each acquired design has no interpretation as measurement time.
    """
    _features, clean, _full = acquisition_view(candidate_features, observed)
    # Fixed key ordering plus deterministic per-design summation order.
    # Both +0 and -0 encode the same observed numeric response.
    return {
        int(index): tuple(sorted(0.0 if response == 0.0 else response for response in clean[index]))
        for index in sorted(clean)
    }


def select_canonical_measurement(
    policy: str,
    candidate_features,
    observed: Mapping[int, tuple[float, ...]],
    *,
    seed: int,
    step: int,
) -> tuple[int, int]:
    """Apply an unchanged v12 policy to a canonicalized acquired-only view.

    For any two maps with the same measured response multiset per design,
    the resulting action should be identical, with the same seed and step.
    Different *partial* observations imply different evidence, so this
    contract does NOT require identical sequential trajectories when physical
    responses are revealed in a different order.
    """
    state = canonical_revealed_state(candidate_features, observed)
    return select_measurement(
        policy,
        candidate_features,
        state,
        seed=seed,
        step=step,
    )


def main():
    print("BHS v12.1: canonical acquired-response interface; synthetic checks only.")
    print("Historical source not accessed; no development scores produced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
