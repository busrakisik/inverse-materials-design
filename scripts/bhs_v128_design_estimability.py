"""BHS v12.8: proposed specimen-level design estimability, not physical inference.

No physical outcomes, experimental commands, fitted responses or source downloads.
Exact rational rank detects specified batch/session/time confounding only.
Even a full-rank plan never authorizes physical action or validates a mechanism.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

SCHEMA = 'BHS-V12.8'
FIXTURE_PATH = Path('research/BHS_V128_MANUFACTURED_DESIGN_FIXTURE.json')
MAX_BYTES = 200_000
ROOT_KEYS = frozenset((
    'schema_version', 'status', 'material_system', 'response_name',
    'response_unit', 'independent_unit', 'intended_primary_contrast',
    'processing_conditions_physically_approved',
    'measurement_calibration_independently_verified',
    'randomization_independently_verified',
    'external_investigator_approval_verified',
    'reviewed_minimum_effect_A_per_m', 'raw_outcomes_present',
    'physical_action_allowed', 'specimens',
))
SPECIMEN_KEYS = frozenset((
    'coupon_id', 'synthesis_batch_id', 'processing_arm',
    'moke_session_id', 'planned_position', 'planned_moke_traces',
    'xrd_planned', 'moke_raw_trace_retention',
))
ARMS = ('reference', 'modified')


class DesignContractError(ValueError):
    """Plan malformed or contains unsupported physical/evaluation assertions."""


def _require(ok, tag):
    if not ok:
        raise DesignContractError(tag)


def _pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'DUPLICATE_JSON_KEY')
        result[key] = value
    return result


def parse_plan(raw: bytes):
    _require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES,
             'INVALID_PLAN_BYTES')
    try:
        return json.loads(
            raw.decode('utf-8'),
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=lambda _: (_ for _ in ()).throw(
                DesignContractError('NONFINITE_JSON_LITERAL')),
        )
    except (UnicodeError, ValueError, TypeError) as exc:
        if isinstance(exc, DesignContractError):
            raise
        raise DesignContractError('PLAN_JSON_INVALID') from exc


def _text(x):
    return type(x) is str and bool(x.strip())


def _exact_rank(matrix):
    """Gauss-Jordan rank over rationals; all entries must be integral."""
    _require(type(matrix) is list and len(matrix) >= 1,
             'INVALID_LINEAR_SYSTEM')
    width = len(matrix[0])
    _require(width >= 1 and all(len(row) == width and
             all(type(a) is int for a in row) for row in matrix),
             'INVALID_LINEAR_MATRIX')
    a = [[Fraction(value) for value in row] for row in matrix]
    pivot_row = 0
    for col in range(width):
        selected = next((r for r in range(pivot_row, len(a))
                         if a[r][col] != 0), None)
        if selected is None:
            continue
        a[pivot_row], a[selected] = a[selected], a[pivot_row]
        factor = a[pivot_row][col]
        a[pivot_row] = [x / factor for x in a[pivot_row]]
        for row in range(len(a)):
            if row == pivot_row:
                continue
            factor = a[row][col]
            if factor:
                a[row] = [x - factor * y for x, y in zip(a[row], a[pivot_row])]
        pivot_row += 1
        if pivot_row == len(a):
            break
    return pivot_row


def audit_plan(plan: dict, *, source_sha256: str | None = None):
    _require(type(plan) is dict and set(plan) == ROOT_KEYS,
             'INVALID_PLAN_SCHEMA')
    fixed = {
        'schema_version': SCHEMA,
        'status': 'manufactured_design_fixture_only',
        'material_system': 'Fe-Co-Ni magnetic thin films',
        'response_name': 'coercive_field',
        'response_unit': 'A/m',
        'independent_unit': 'planned_coupon',
        'intended_primary_contrast': 'modified_minus_reference',
    }
    _require(all(plan.get(k) == v for k, v in fixed.items()),
             'UNSUPPORTED_STUDY_IDENTITY')
    for flag in (
        'processing_conditions_physically_approved',
        'measurement_calibration_independently_verified',
        'randomization_independently_verified',
        'external_investigator_approval_verified',
        'raw_outcomes_present', 'physical_action_allowed',
    ):
        _require(plan[flag] is False, 'UNSUPPORTED_PHYSICAL_OR_RESULT_CLAIM')
    threshold = plan['reviewed_minimum_effect_A_per_m']
    _require(threshold is None or
             (type(threshold) in (int, float) and math.isfinite(threshold)
              and threshold > 0), 'INVALID_EFFECT_THRESHOLD')
    specs = plan['specimens']
    _require(type(specs) is list and specs and len(specs) <= 1000,
             'INVALID_SPECIMEN_RECORDS')

    ids = set()
    sessions = defaultdict(list)
    batches = defaultdict(list)
    trace_count = 0
    for row in specs:
        _require(type(row) is dict and set(row) == SPECIMEN_KEYS,
                 'INVALID_SPECIMEN_SCHEMA')
        for name in ('coupon_id', 'synthesis_batch_id', 'moke_session_id'):
            _require(_text(row[name]), 'MISSING_SPECIMEN_IDENTIFIER')
        _require(row['coupon_id'] not in ids, 'DUPLICATED_SPECIMEN')
        ids.add(row['coupon_id'])
        _require(row['processing_arm'] in ARMS,
                 'INVALID_TREATMENT_ARM')
        for name in ('planned_position', 'planned_moke_traces'):
            _require(type(row[name]) is int and row[name] > 0,
                     'INVALID_SEQUENCE_OR_TRACE_COUNT')
        _require(row['xrd_planned'] is True and
                 row['moke_raw_trace_retention'] is True,
                 'MISSING_ORIGINAL_STRUCTURAL_OR_MAGNETIC_MEASUREMENTS')
        sessions[row['moke_session_id']].append(row)
        batches[row['synthesis_batch_id']].append(row)
        trace_count += row['planned_moke_traces']

    _require(len(batches) >= 2 and len(sessions) >= 2,
             'INSUFFICIENT_BATCH_OR_SESSION_STRUCTURE')
    for session, members in sessions.items():
        order = [r['planned_position'] for r in members]
        _require(sorted(order) == list(range(1, len(members)+1)),
                 'DUPLICATED_OR_MISSING_SESSION_SLOT')

    blockers = []
    for group, members in batches.items():
        if {r['processing_arm'] for r in members} != set(ARMS):
            blockers.append('UNPAIRED_SYNTHESIS_BATCH:' + group)
    for group, members in sessions.items():
        if {r['processing_arm'] for r in members} != set(ARMS):
            blockers.append('SINGLE_ARM_MEASUREMENT_SESSION:' + group)
        else:
            reference = [r['planned_position'] for r in members
                         if r['processing_arm'] == 'reference']
            modified = [r['planned_position'] for r in members
                        if r['processing_arm'] == 'modified']
            # Compare exact rational mean positions; a systematic ordering
            # difference can confound the contrast with nonlinear time drift.
            if Fraction(sum(reference), len(reference)) != Fraction(
                    sum(modified), len(modified)):
                blockers.append('ARM_POSITION_IMBALANCE:' + group)

    batch_names = sorted(batches)
    session_names = sorted(sessions)
    nuisance = []
    treatment = []
    for row in specs:
        session = row['moke_session_id']
        nuisance.append(
            [1]
            + [int(row['synthesis_batch_id'] == name) for name in batch_names[1:]]
            + [int(session == name) for name in session_names[1:]]
            + [(2 * row['planned_position'] - (len(sessions[name])+1))
               if session == name else 0 for name in session_names]
        )
        treatment.append(int(row['processing_arm'] == 'modified'))
    rank_nuisance = _exact_rank(nuisance)
    full = [row + [tr] for row, tr in zip(nuisance, treatment)]
    rank_full = _exact_rank(full)
    estimable = rank_full > rank_nuisance
    if not estimable:
        blockers.append('PROCESSING_CONTRAST_CONFOUNDED_WITH_NUISANCE')
    residual_df = len(specs) - rank_full
    if residual_df <= 0:
        blockers.append('NO_RESIDUAL_DEGREES_OF_FREEDOM')
    if threshold is None:
        blockers.append('PHYSICAL_MINIMUM_MEANINGFUL_EFFECT_UNSET')
    # Even with estimability, independent group calibration and physical oversight
    # cannot be established from manufactured metadata.
    blockers.extend((
        'EXTERNAL_LAB_APPROVAL_UNVERIFIED',
        'ACTUAL_RANDOMIZATION_UNVERIFIED',
        'INSTRUMENT_CALIBRATION_UNVERIFIED',
        'INDEPENDENT_PHYSICAL_VALIDATION_ABSENT',
    ))
    return {
        'study': 'BHS v12.8 source-independent design estimability check',
        'source_sha256': source_sha256,
        'physical_outcomes_seen': False,
        'specimen_rows': len(specs),
        'planned_technical_traces': trace_count,
        'synthesis_batch_count': len(batches),
        'measurement_session_count': len(sessions),
        'nuisance_rank': rank_nuisance,
        'full_rank': rank_full,
        'residual_degrees_of_freedom': residual_df,
        'linear_contrast_estimable_under_declared_nuisance': estimable,
        'no_claim_of_causal_identification': True,
        'blocking_conditions': sorted(blockers),
        'physical_recommendation_allowed': False,
        'laboratory_action_allowed': False,
        'independent_physical_validation_established': False,
        'statistical_risk_guarantee_supported': False,
        'status': 'NO_GO_PHYSICAL_DESIGN_NOT_EXTERNALLY_VALIDATED',
    }


def audit_plan_bytes(raw: bytes):
    return audit_plan(parse_plan(raw), source_sha256=hashlib.sha256(raw).hexdigest())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args(argv)
    if args.plan is None and args.out is None:
        print('Protocol-only mode; no design source opened or scored.')
        return 0
    if args.plan is None or args.out is None:
        parser.error('Both --plan and --out are required')
    result = audit_plan_bytes(args.plan.read_bytes())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print('Design rank and physical no-go contract verified.')
    print('Specimen units:', result['specimen_rows'], 'Independent batches:',
          result['synthesis_batch_count'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
