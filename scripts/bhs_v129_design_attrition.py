"""V12.9: outcome-free attrition audit of proposed paired coupon schedules.

Uses the exact rational matrix-rank operation from the frozen V12.8 design
contract. Structural resilience is neither physical feasibility nor causal
identification; no experiment, observation, posterior or score is generated.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from scripts.bhs_v128_design_estimability import (
    DesignContractError, _exact_rank, audit_plan,
)

SCHEMA = 'BHS-V12.9'
ROOT_KEYS = frozenset((
    'schema_version', 'status', 'parent_v128_design_blob',
    'treatment_unit_feasibility_approved',
    'independent_synthesis_batches_verified',
    'physical_measurements_available', 'laboratory_action_allowed',
    'variants',
))
VARIANTS = ('cross_session_pairs', 'within_session_pairs')
EXPECTED_PARENT = '3cde6a6ad809effdf21fcdd50ab737c8cfaf07e8'
MAX_SOURCE_BYTES = 300_000
EXPECTED_BATCHES = tuple(f'B{i:02d}' for i in range(1, 9))
EXPECTED_SESSIONS = ('S1', 'S2')
ARMS = ('reference', 'modified')


class AttritionContractError(ValueError):
    """Invalid source plan, duplicate evidence or unsupported physical claim."""


def _require(condition, tag):
    if not condition:
        raise AttritionContractError(tag)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'DUPLICATED_JSON_KEY')
        result[key] = value
    return result


def parse_bundle(raw: bytes):
    _require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
             'INVALID_BUNDLE_BYTES')
    try:
        return json.loads(
            raw.decode('utf-8'), object_pairs_hook=_unique_pairs,
            parse_constant=lambda s: (_ for _ in ()).throw(
                AttritionContractError('NONFINITE_JSON_NUMBER')),
        )
    except (UnicodeError, ValueError, TypeError) as exc:
        if isinstance(exc, AttritionContractError):
            raise
        raise AttritionContractError('INVALID_BUNDLE_JSON') from exc


def _group_rows(rows, field):
    groups = defaultdict(list)
    for row in rows:
        groups[row[field]].append(row)
    return groups


def model_summary(rows):
    """Same declared nuisance columns as V12.8, allowing dropped sessions.

    The output is deterministic algebraic rank, NOT confidence, precision,
    a tested physical hypothesis, causal isolation or a sample-size result.
    """
    _require(type(rows) is list and len(rows) >= 2, 'NO_COUPON_ROWS')
    groups = _group_rows(rows, 'synthesis_batch_id')
    sessions = _group_rows(rows, 'moke_session_id')
    batch_ids, session_ids = sorted(groups), sorted(sessions)
    nuisance = []
    arm = []
    for row in rows:
        session = row['moke_session_id']
        nuisance.append(
            [1]
            + [int(row['synthesis_batch_id'] == name) for name in batch_ids[1:]]
            + [int(session == name) for name in session_ids[1:]]
            + [
                (2 * row['planned_position'] - (len(sessions[name]) + 1))
                if session == name else 0
                for name in session_ids
            ]
        )
        arm.append(int(row['processing_arm'] == 'modified'))
    rank_nuisance = _exact_rank(nuisance)
    rank_full = _exact_rank([a + [b] for a, b in zip(nuisance, arm)])
    complete_pairs = sum(
        {row['processing_arm'] for row in group} == set(ARMS)
        for group in groups.values()
    )
    balanced_sessions = sum(
        {row['processing_arm'] for row in group} == set(ARMS)
        for group in sessions.values()
    )
    row_df = len(rows) - rank_full
    is_estimable = rank_full == rank_nuisance + 1
    return {
        'coupon_rows': len(rows),
        'named_batch_count': len(groups),
        'session_count': len(sessions),
        'technical_trace_count': sum(row['planned_moke_traces'] for row in rows),
        'fully_paired_batch_count': int(complete_pairs),
        'both_arm_session_count': int(balanced_sessions),
        'nuisance_rank': rank_nuisance,
        'full_rank': rank_full,
        'residual_row_degrees_of_freedom': row_df,
        'linear_treatment_estimable': is_estimable,
        'algebraically_non_saturated': row_df > 0,
        'nominal_robustness_condition': bool(is_estimable and row_df > 0),
        'physical_adequacy_inferred': False,
        'cluster_uncertainty_calibrated': False,
    }


def _validate_variant(name, plan):
    try:
        initial = audit_plan(plan)
    except (DesignContractError, ValueError, TypeError, KeyError) as exc:
        raise AttritionContractError('INVALID_V128_COMPONENT_DESIGN') from exc
    rows = plan['specimens']
    _require(len(rows) == 16, 'EXPECTED_SIXTEEN_INDEPENDENT_COUPON_ROWS')
    _require(
        sorted({row['synthesis_batch_id'] for row in rows}) == list(EXPECTED_BATCHES)
        and sorted({row['moke_session_id'] for row in rows}) == list(EXPECTED_SESSIONS),
        'CHANGED_BATCH_OR_SESSION_SET',
    )
    coupon_ids = {row['coupon_id'] for row in rows}
    _require(
        coupon_ids == {
            batch + '-' + arm
            for batch in EXPECTED_BATCHES for arm in ('R', 'M')
        }, 'COUPON_ID_OR_TREATMENT_PAIR_INCOMPLETE',
    )
    batches = _group_rows(rows, 'synthesis_batch_id')
    for batch, pair in batches.items():
        _require(len(pair) == 2 and {x['processing_arm'] for x in pair} == set(ARMS)
                 and {x['coupon_id'][-1] for x in pair} == {'R', 'M'}
                 and all(x['coupon_id'] == batch + '-'
                         + ('R' if x['processing_arm'] == 'reference' else 'M')
                         for x in pair),
                 'BATCH_TREATMENT_PAIR_BROKEN')
        if name == 'cross_session_pairs':
            _require(len({row['moke_session_id'] for row in pair}) == 2,
                     'EXPECTED_CROSS_SESSION_TREATMENT_PAIR')
        else:
            _require(len({row['moke_session_id'] for row in pair}) == 1,
                     'EXPECTED_WITHIN_SESSION_TREATMENT_PAIR')
    sessions = _group_rows(rows, 'moke_session_id')
    _require(all(len(group) == 8 for group in sessions.values()),
             'EIGHT_COUPONS_PER_SESSION_REQUIRED')
    _require(not any(x.startswith('SINGLE_ARM_MEASUREMENT_SESSION:') or
                     x.startswith('ARM_POSITION_IMBALANCE:')
                     for x in initial['blocking_conditions']),
             'SESSION_ARM_OR_POSITION_IMBALANCE')
    # The full fixture may not claim an approved effect threshold or data.
    _require(plan['reviewed_minimum_effect_A_per_m'] is None,
             'UNSUPPORTED_PHYSICAL_EFFECT_THRESHOLD')
    return rows, initial


def audit_bundle(bundle, *, source_sha256=None):
    _require(type(bundle) is dict and set(bundle) == ROOT_KEYS,
             'INVALID_BUNDLE_STRUCTURE')
    _require(bundle['schema_version'] == SCHEMA and
             bundle['status'] == 'two_outcome_free_development_designs'
             and bundle['parent_v128_design_blob'] == EXPECTED_PARENT,
             'FROZEN_DESIGN_OR_SOURCE_IDENTITY_CHANGED')
    for key in (
        'treatment_unit_feasibility_approved',
        'independent_synthesis_batches_verified',
        'physical_measurements_available', 'laboratory_action_allowed',
    ):
        _require(bundle[key] is False, 'UNSUPPORTED_EXTERNAL_APPROVAL_OR_RESULT')
    variants = bundle['variants']
    _require(type(variants) is dict and set(variants) == set(VARIANTS),
             'REQUIRED_VARIANTS_MISSING')

    reports = {}
    for name in VARIANTS:
        rows, full_v128 = _validate_variant(name, variants[name])
        full = model_summary(rows)
        _require(full['nuisance_rank'] == full_v128['nuisance_rank'] and
                 full['full_rank'] == full_v128['full_rank'] and
                 full['residual_row_degrees_of_freedom'] ==
                 full_v128['residual_degrees_of_freedom'] and
                 full['linear_treatment_estimable'] ==
                 full_v128['linear_contrast_estimable_under_declared_nuisance'],
                 'INHERITED_LINEAR_MODEL_PARITY_FAILURE')
        by_batch = _group_rows(rows, 'synthesis_batch_id')
        by_session = _group_rows(rows, 'moke_session_id')
        leave_batches = {
            group: model_summary([x for x in rows
                                  if x['synthesis_batch_id'] != group])
            for group in sorted(by_batch)
        }
        leave_sessions = {
            session: model_summary([x for x in rows
                                    if x['moke_session_id'] != session])
            for session in sorted(by_session)
        }
        reports[name] = {
            'full_design': full,
            'leave_one_batch': leave_batches,
            'leave_one_session': leave_sessions,
            'batch_loss_nominal_pass_count': sum(
                x['nominal_robustness_condition'] for x in leave_batches.values()),
            'batch_loss_scenarios': len(leave_batches),
            'session_loss_nominal_pass_count': sum(
                x['nominal_robustness_condition'] for x in leave_sessions.values()),
            'session_loss_scenarios': len(leave_sessions),
            'full_design_initial_v128_no_go': full_v128['status'],
            'treatment_assignment_feasible_verified': False,
            'independent_batch_provenance_verified': False,
            'physical_recommendation_allowed': False,
            'laboratory_action_allowed': False,
        }
    return {
        'study': 'BHS v12.9 manufactured design attrition and session review',
        'source_sha256': source_sha256,
        'parent_v128_design_blob': EXPECTED_PARENT,
        'physical_measurements_performed': False,
        'hypothesis_evaluation_performed': False,
        'real_source_accessed': False,
        'technical_traces_are_independent_specimens': False,
        'formal_power_or_precision_established': False,
        'scientific_sample_size_recommended': False,
        'physical_recommendation_allowed': False,
        'laboratory_action_allowed': False,
        'independent_physical_validation_established': False,
        'statistical_risk_guarantee_supported': False,
        'status': 'NO_GO_EXTERNAL_LAB_AND_PRECISION_REVIEW_REQUIRED',
        'variants': reports,
    }


def audit_bundle_bytes(raw: bytes):
    return audit_bundle(parse_bundle(raw), source_sha256=hashlib.sha256(raw).hexdigest())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--designs', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args(argv)
    if args.designs is None and args.out is None:
        print('Protocol-only; no design or outcome records opened.')
        return 0
    if args.designs is None or args.out is None:
        parser.error('Both --designs and --out required')
    report = audit_bundle_bytes(args.designs.read_bytes())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print('Deterministic outcome-free batch/session attrition review complete.')
    print('Physical laboratory and scientific release decisions remain NO-GO.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
