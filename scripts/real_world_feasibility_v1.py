"""Static research-feasibility contract. No download, label access, or holdout execution."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

STATUS = 'DATASET_FEASIBILITY_ONLY_NOT_BENCHMARKED'
REGISTER = Path('research/REAL_WORLD_DATASET_CANDIDATES_V1.json')
REQUIRED_IDS = ('nist_fe_co_ni', 'made_2026', 'matbench', 'materials_project')
BLOCKED_FLAGS = ('data_downloaded', 'data_license_cleared_for_redistribution',
                 'instrument_uncertainty_verified', 'actual_per_experiment_cost_verified',
                 'hypothesis_family_mapped', 'compatible_with_current_bhs')

def validate_registry(registry):
    if type(registry) is not dict or registry.get('status') != STATUS:
        raise ValueError('unknown feasibility register')
    for field in ('independent_holdout_used', 'scored_validation_allowed', 'physical_validation'):
        if registry.get(field) is not False:
            raise ValueError('unsupported validation claim: ' + field)
    entries = registry.get('datasets')
    if type(entries) is not list or len(entries) != len(REQUIRED_IDS):
        raise ValueError('unexpected dataset count')
    if tuple(e.get('id') for e in entries if type(e) is dict) != REQUIRED_IDS:
        raise ValueError('dataset inventory altered')
    for row in entries:
        for field in ('name','url','kind','intended_role','support'):
            if type(row.get(field)) is not str or not row[field].strip():
                raise ValueError('missing dataset evidence metadata')
        if not row['url'].startswith('https://'):
            raise ValueError('non-https reference')
        for flag in BLOCKED_FLAGS:
            if row.get(flag) is not False:
                raise ValueError('unreviewed readiness flag changed: ' + flag)
    gates = registry.get('pilot_prerequisites')
    if type(gates) is not list or len(gates) != 8 or len(set(gates)) != 8:
        raise ValueError('pilot gate inventory incomplete')
    return {'status': STATUS, 'dataset_candidates':len(entries),
            'first_pilot_candidate': entries[0]['id'],
            'datasets_ready_for_bhs':0, 'real_data_experiment_executed':False,
            'independent_holdout_used':False, 'physical_validation':False,
            'scored_validation_allowed':False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--register',default=str(REGISTER))
    p.add_argument('--out-dir', default='runs/real_world_feasibility_v1')
    args=p.parse_args()
    register_bytes=Path(args.register).read_bytes()
    result=validate_registry(json.loads(register_bytes))
    result['input_registry_sha256']=hashlib.sha256(register_bytes).hexdigest()
    folder=Path(args.out_dir);folder.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    (folder/'feasibility_report.json').write_bytes(raw)
    (folder/'feasibility_report.sha256').write_text(hashlib.sha256(raw).hexdigest()+'  feasibility_report.json\n')
    print(json.dumps(result,sort_keys=True))

if __name__ == '__main__':main()
