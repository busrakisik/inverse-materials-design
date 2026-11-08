"""V12.10: outcome-free physical processing-scope and assignment-unit audit.

Two conditional Fe-Co-Ni design examples; no instruments, physical source data,
material property predictions, or experimental results are accessed.
The exact rational rank operation is inherited from frozen v12.8.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from scripts.bhs_v128_design_estimability import _exact_rank

SCHEMA = 'BHS-V12.10'
FIXTURE = Path('research/BHS_V1210_ASSIGNMENT_UNIT_FIXTURES.json')
V129_SOURCE_GIT_BLOB = '0dbd73ce65c48239e94a8e611faa450056217f8d'
MODES = ('postdeposition_coupon', 'deposition_run')
ARMS = ('reference', 'modified')
MAX_BYTES = 200_000
ROOT_KEYS = frozenset((
    'schema_version', 'status', 'source_v129_fixture_blob',
    'material_system', 'target_observable', 'target_unit', 'scenarios',
))
SCENARIO_KEYS = frozenset((
    'processing_scope', 'declared_assignment_unit',
    'treatment_unit_physical_feasibility_verified',
    'instrument_calibration_verified', 'composition_matching_verified',
    'randomization_externally_verified', 'independent_batch_provenance_verified',
    'new_physical_measurements_present', 'physical_action_allowed', 'specimens',
))
ROW_KEYS = frozenset((
    'coupon_id', 'matched_block_id', 'source_deposition_run_id',
    'processing_event_id', 'processing_arm', 'moke_session_id',
    'planned_position', 'substrate_location_stratum',
    'planned_moke_traces', 'xrd_planned', 'moke_raw_trace_retention',
))
FALSE_CLAIMS = frozenset(SCENARIO_KEYS - {'processing_scope', 'declared_assignment_unit', 'specimens'})


class AssignmentContractError(ValueError):
    """Reject malformed or scientifically unsupported assignment plans."""


def _require(test, label):
    if not test:
        raise AssignmentContractError(label)


def _unique_json_pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'DUPLICATED_JSON_KEY')
        result[key] = value
    return result


def parse_fixtures(raw: bytes):
    _require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES,
             'INVALID_SOURCE_BYTES')
    try:
        obj = json.loads(
            raw.decode('utf-8'), object_pairs_hook=_unique_json_pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(
                AssignmentContractError('NONFINITE_JSON_LITERAL')),
        )
    except (TypeError, ValueError, UnicodeError) as exc:
        if isinstance(exc, AssignmentContractError):
            raise
        raise AssignmentContractError('INVALID_JSON_SOURCE') from exc
    return obj


def _str(value):
    return type(value) is str and bool(value.strip())


def _groups(rows, column):
    result = defaultdict(list)
    for row in rows:
        result[row[column]].append(row)
    return result


def _matrix_rank(rows):
    """Exact algebraic fixed-block/session/position/location design rank.

    A contrast can be linearly estimable without a valid error distribution or
    a practically assignable treatment. No magnetic responses are used.
    """
    _require(type(rows) is list and len(rows) >= 2, 'TOO_FEW_PLAN_UNITS')
    blocks = _groups(rows, 'matched_block_id')
    sessions = _groups(rows, 'moke_session_id')
    locations = sorted({r['substrate_location_stratum'] for r in rows})
    block_ids = sorted(blocks)
    session_ids = sorted(sessions)
    nuisance = []
    treatment = []
    for row in rows:
        sess = row['moke_session_id']
        nuisance.append(
            [1]
            + [int(row['matched_block_id'] == x) for x in block_ids[1:]]
            + [int(sess == x) for x in session_ids[1:]]
            + [int(row['substrate_location_stratum'] == x) for x in locations[1:]]
            + [2 * row['planned_position'] - len(sessions[x]) - 1 if sess == x else 0
               for x in session_ids]
        )
        treatment.append(int(row['processing_arm'] == 'modified'))
    base_rank = _exact_rank(nuisance)
    full_rank = _exact_rank([a + [t] for a, t in zip(nuisance, treatment)])
    return {
        'coupon_rows': len(rows),
        'named_matched_blocks': len(blocks),
        'named_deposition_runs': len({r['source_deposition_run_id'] for r in rows}),
        'named_processing_events': len({r['processing_event_id'] for r in rows}),
        'moke_sessions': len(sessions),
        'technical_traces': sum(x['planned_moke_traces'] for x in rows),
        'complete_paired_blocks': sum(
            {r['processing_arm'] for r in group} == set(ARMS)
            for group in blocks.values()),
        'nuisance_rank': base_rank,
        'full_rank': full_rank,
        'residual_coupon_row_df': len(rows)-full_rank,
        'treatment_estimable_in_declared_additive_matrix': full_rank == base_rank + 1,
        'nominal_rank_and_df_pass': bool(full_rank == base_rank+1 and len(rows)>full_rank),
        'physical_independence_established': False,
        'group_robust_uncertainty_established': False,
        'formal_power_established': False,
    }


def _validate_scenario(mode, scenario):
    _require(type(scenario) is dict and set(scenario) == SCENARIO_KEYS,
             'INVALID_SCENARIO_FIELDS')
    _require(scenario['processing_scope'] == mode and
             scenario['declared_assignment_unit'] ==
             ('coupon' if mode == 'postdeposition_coupon' else 'deposition_run'),
             'TREATMENT_SCOPE_UNIT_MISMATCH')
    for key in FALSE_CLAIMS:
        _require(scenario[key] is False, 'UNSUPPORTED_APPROVAL_OR_PHYSICAL_RESULT')
    rows = scenario['specimens']
    _require(type(rows) is list and len(rows) == 16,
             'EXPECTED_SIXTEEN_PLANNED_COUPONS')
    coupons = set()
    session_slots = set()
    blocks = defaultdict(list)
    runs = defaultdict(list)
    events = defaultdict(list)
    sessions = defaultdict(list)
    strata = defaultdict(Counter)
    for row in rows:
        _require(type(row) is dict and set(row) == ROW_KEYS,
                 'INVALID_PLAN_ROW_FIELDS')
        for name in ('coupon_id','matched_block_id','source_deposition_run_id',
                     'processing_event_id','moke_session_id'):
            _require(_str(row[name]), 'INVALID_SOURCE_IDENTIFIER')
        _require(row['processing_arm'] in ARMS,
                 'UNKNOWN_PROCESSING_ARM')
        _require(row['substrate_location_stratum'] in ('near','far'),
                 'INVALID_SUBSTRATE_POSITION_STRATUM')
        _require(type(row['planned_position']) is int and row['planned_position'] > 0
                 and type(row['planned_moke_traces']) is int
                 and row['planned_moke_traces'] > 0,
                 'INVALID_SESSION_POSITION_OR_TRACE_COUNT')
        _require(row['xrd_planned'] is True and row['moke_raw_trace_retention'] is True,
                 'MISSING_ORIGINAL_STRUCTURAL_OR_MAGNETIC_EVIDENCE_PLAN')
        cid = row['coupon_id']
        key = (row['moke_session_id'],row['planned_position'])
        _require(cid not in coupons, 'DUPLICATE_COUPON')
        _require(key not in session_slots, 'DUPLICATE_SESSION_POSITION')
        coupons.add(cid)
        session_slots.add(key)
        blocks[row['matched_block_id']].append(row)
        runs[row['source_deposition_run_id']].append(row)
        events[row['processing_event_id']].append(row)
        sessions[row['moke_session_id']].append(row)
        strata[row['substrate_location_stratum']][row['processing_arm']] += 1
    _require(len(blocks) == 8 and set(blocks)=={f'B{i:02d}' for i in range(1,9)},
             'MATCHED_BLOCK_STRUCTURE_CHANGED')
    _require(len(sessions)==2 and set(sessions)=={'S1','S2'},
             'MEASUREMENT_SESSION_STRUCTURE_CHANGED')
    for batch, pair in blocks.items():
        _require(len(pair) == 2 and {r['processing_arm'] for r in pair} == set(ARMS),
                 'INCOMPLETE_REFERENCE_MODIFIED_BLOCK')
        _require({r['coupon_id'] for r in pair} == {batch+'-R',batch+'-M'},
                 'COUPON_TO_MATCHED_BLOCK_WRONG')
    for sess, members in sessions.items():
        _require(len(members) == 8 and
                 sorted(x['planned_position'] for x in members)==list(range(1,9)),
                 'SESSION_POSITION_COUNT_WRONG')
        _require(Counter(r['processing_arm'] for r in members) ==
                 Counter({'reference':4,'modified':4}),
                 'SESSION_TREATMENT_CONFUNDING')
        rpositions=[r['planned_position'] for r in members if r['processing_arm']=='reference']
        mpositions=[r['planned_position'] for r in members if r['processing_arm']=='modified']
        _require(Fraction(sum(rpositions),4)==Fraction(sum(mpositions),4),
                 'SESSION_TIME_TREND_TREATMENT_CONFOUNDING')
    for location, counts in strata.items():
        _require(counts.get('reference',0)>0 and counts.get('modified',0)>0,
                 'SPATIAL_COMPOSITION_POSITION_TREATMENT_CONFOUNDING')
    _require(set(strata)=={'near','far'}, 'SPATIAL_POSITION_VARIATION_UNREGISTERED')
    _require(len(events)==16 and all(len(members)==1 for members in events.values()),
             'SHARED_PROCESSING_EVENT_INVALIDATES_DECLARED_UNIT')
    for run, members in runs.items():
        arms={r['processing_arm'] for r in members}
        if mode == 'deposition_run':
            _require(len(members)==1 and len(arms)==1,
                     'WHOLE_DEPOSITION_RUN_WITH_MIXED_OR_DUPLICATED_TREATMENT')
            _require(members[0]['processing_event_id']==run,
                     'DEPOSITION_PROCESSING_RUN_ID_MISMATCH')
    if mode == 'postdeposition_coupon':
        _require(len(runs)==8 and all(len(members)==2 for members in runs.values()),
                 'POSTDEPOSITION_MATCHED_SOURCE_REQUIRED')
        for block,pair in blocks.items():
            _require({r['source_deposition_run_id'] for r in pair}=={block},
                     'POSTDEPOSITION_COUPON_CANNOT_HAVE_SEPARATE_SOURCE_BATCHES')
            _require(len({r['processing_event_id'] for r in pair})==2,
                     'POSTDEPOSITION_TREATMENT_EVENTS_NOT_SEPARATE')
    else:
        _require(len(runs)==16,
                 'DEPOSITION_TREATMENT_REQUIRES_SEPARATE_SYNTHESIS_RUNS')
        for block,pair in blocks.items():
            _require(len({r['source_deposition_run_id'] for r in pair})==2,
                     'SINGLE_RUN_CANNOT_CONTAIN_TWO_DEPOSITION_TREATMENTS')
            _require(all(r['source_deposition_run_id']==f'dep-{block}-'+
                         ('R' if r['processing_arm']=='reference' else 'M')
                         for r in pair),
                     'DEPOSITION_RUN_TO_BLOCK_ASSIGNMENT_INCONSISTENT')
    return rows


def audit_all(bundle, *, source_sha256=None):
    _require(type(bundle) is dict and set(bundle)==ROOT_KEYS,
             'INVALID_FIXTURE_ROOT_SCHEMA')
    _require(bundle['schema_version']==SCHEMA and
             bundle['status']=='outcome_free_processing_scope_comparison' and
             bundle['source_v129_fixture_blob']==V129_SOURCE_GIT_BLOB and
             bundle['material_system']=='Fe-Co-Ni magnetic thin films' and
             bundle['target_observable']=='coercive_field' and
             bundle['target_unit']=='A/m',
             'UNAUTHORIZED_SCIENTIFIC_SOURCE_OR_UNITS')
    variants=bundle['scenarios']
    _require(type(variants) is dict and set(variants)==set(MODES),
             'MISSING_PRECOMMITTED_PROCESSING_SCENARIOS')
    result={}
    for mode in MODES:
        rows=_validate_scenario(mode,variants[mode])
        groups=_groups(rows,'matched_block_id')
        events=_groups(rows,'processing_event_id')
        sessions=_groups(rows,'moke_session_id')
        full=_matrix_rank(rows)
        leave_event={
            eid:_matrix_rank([r for r in rows if r['processing_event_id']!=eid])
            for eid in sorted(events)
        }
        leave_session={
            session:_matrix_rank([r for r in rows if r['moke_session_id']!=session])
            for session in sorted(sessions)
        }
        # Each named matched block is a design/accounting entity, not verified
        # independent physical sampling from any population.
        result[mode]={
            'declared_assignment_unit':variants[mode]['declared_assignment_unit'],
            'full_design':full,
            'all_event_losses':leave_event,
            'all_session_losses':leave_session,
            'event_loss_nominal_pass_count':sum(v['nominal_rank_and_df_pass'] for v in leave_event.values()),
            'session_loss_nominal_pass_count':sum(v['nominal_rank_and_df_pass'] for v in leave_session.values()),
            'event_count':len(events),
            'session_count':len(sessions),
            'named_matched_blocks':len(groups),
            'planned_measurement_traces_not_independent_units':True,
            'actual_processing_scope_verified':False,
            'actual_independent_replicates_verified':False,
            'causal_identification_established':False,
            'physical_recommendation_allowed':False,
            'laboratory_action_allowed':False,
        }
    return {
        'study':'BHS v12.10 outcome-free processing-scope feasibility audit',
        'source_sha256':source_sha256,
        'parent_v129_fixture_blob':V129_SOURCE_GIT_BLOB,
        'physical_measurements_performed':False,
        'previous_experiment_results_changed':False,
        'no_physical_composition_or_thickness_derived':True,
        'actual_treatment_assignability_verified':False,
        'formal_sample_size_established':False,
        'statistical_guarantee_supported':False,
        'physical_recommendation_allowed':False,
        'laboratory_action_allowed':False,
        'independent_physical_validation_established':False,
        'status':'NO_GO_EXTERNAL_PROCESSING_SCOPE_AND_LAB_REVIEW_REQUIRED',
        'scenarios':result,
    }


def audit_bytes(raw: bytes):
    return audit_all(parse_fixtures(raw),source_sha256=hashlib.sha256(raw).hexdigest())


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixtures',type=Path)
    p.add_argument('--out',type=Path)
    a=p.parse_args(argv)
    if a.fixtures is None and a.out is None:
        print('Protocol-only: no physical measurements or structural results generated.')
        return 0
    if a.fixtures is None or a.out is None:
        p.error('Both --fixtures and --out are required')
    report=audit_bytes(a.fixtures.read_bytes())
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('Processing-scope audit complete. External physical feasibility remains unverified.')
    print('Output:',a.out)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
