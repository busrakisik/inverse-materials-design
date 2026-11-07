"""Source-order invariance diagnostic for the first v12 reference mismatch.

Development investigation only. Report divergence step numbers, never design IDs,
raw source observations, or physical-effect conclusions. No policy tuning.
"""
import hashlib
import json

import numpy as np

from scripts.bhs_measurement_allocation_v12 import (
    SEEDS, INITIAL_GEOMETRIES, REPEATS, SOURCE_SHA256,
    HistoricalMeasurementOracle, initial_geometry_ids, select_measurement,
)
from scripts.bhs_replicate_leakage_v10 import fetch_pinned_source, parse_source
from scripts.bhs_replicate_pool_v11 import group_source, select_next


def trajectory_v11(features, recorded, seed):
    chosen = list(initial_geometry_ids(len(features), seed))
    later = []
    for step in range(10):
        idx = select_next('rf_ucb', features, chosen, recorded[chosen].copy(),
                          seed=seed, step=step)
        later.append(idx)
        chosen.append(idx)
    return later


def trajectory_v12(features, recorded, seed, *, artificial_order):
    initial = initial_geometry_ids(len(features), seed)
    if artificial_order:
        oracle = HistoricalMeasurementOracle(recorded, seed)
        observed = {i: tuple(oracle.reveal_one(i, j)
                              for j in range(1, REPEATS + 1)) for i in initial}
    else:
        observed = {i: tuple(map(float, recorded[i])) for i in initial}
    later = []
    for step in range(10):
        idx, ordinal = select_measurement('rf_ucb_bundled', features,
                                          observed, seed=seed, step=step * REPEATS)
        if ordinal != 1:
            raise AssertionError('BUNDLED_REFERENCE_NOT_STARTING_NEW_GEOMETRY')
        later.append(idx)
        if artificial_order:
            observed[idx] = tuple(oracle.reveal_one(idx, j)
                                  for j in range(1, REPEATS + 1))
        else:
            observed[idx] = tuple(map(float, recorded[idx]))
    return later


def first_difference(a, b):
    return next((i + 1 for i, (x, y) in enumerate(zip(a, b)) if x != y), None)


def main():
    raw = fetch_pinned_source()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise AssertionError('PINNED_SOURCE_MISMATCH')
    x, y, groups = parse_source(raw)
    features, triples = group_source(x, y, groups)
    outcome = {}
    for seed in SEEDS:
        original = trajectory_v11(features, triples, seed)
        same_order = trajectory_v12(features, triples, seed, artificial_order=False)
        shuffled = trajectory_v12(features, triples, seed, artificial_order=True)
        outcome[str(seed)] = {
            'original_source_order_first_divergence': first_difference(original, same_order),
            'artificial_replay_order_first_divergence': first_difference(original, shuffled),
            'artificial_replay_order_different_design_actions': sum(
                a != b for a, b in zip(original, shuffled)),
        }
    print(json.dumps({
        'study': 'v12 first-run reference reproducibility diagnostic only',
        'original_response_values_redistributed': False,
        'selected_design_ids_redistributed': False,
        'development_only': True,
        'source_order_check': outcome,
    }, indent=2))
    if any(v['original_source_order_first_divergence'] is not None for v in outcome.values()):
        raise AssertionError('SOURCE_ORDER_BASELINE_CODE_PARITY_FAILED')


if __name__ == '__main__':
    main()
