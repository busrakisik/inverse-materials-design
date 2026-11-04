"""Fail-closed NIST Fe-Co-Ni metadata contract; never downloads or loads material rows."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

STATUS = 'NIST_FE_CO_NI_SOURCE_CONTRACT_ONLY_NOT_BENCHMARKED'
PATH = Path('research/NIST_FE_CO_NI_SOURCE_CONTRACT_V1.json')
FIELD_UNITS = {'C': 'not specified in source description',
               'XRD': 'not specified in source description',
               'TTH': 'not specified in source description',
               'Coer': 'mT', 'Kerr': 'mrad'}
FAIL_CLOSED = ('source_binary_downloaded','source_field_shapes_verified',
               'source_missingness_measured','source_license_cleared_for_redistribution',
               'instrument_uncertainty_verified','real_experiment_cost_verified',
               'scientific_hypotheses_specified','bhs_model_compatibility_validated',
               'real_data_experiment_executed','physical_validation',
               'independent_holdout_used','scored_validation_allowed')

def validate(data):
    if type(data) is not dict or data.get('status') != STATUS:
        raise ValueError('incorrect source contract status')
    if data.get('source_repository') != 'usnistgov/remi' or data.get('source_branch') != 'nist-pages':
        raise ValueError('unexpected source repository')
    if data.get('source_file') != 'data/Combinatorial Libraries/Fe-Co-Ni/FeCoNi_benchmark_dataset_220501a.mat':
        raise ValueError('incorrect source path')
    if data.get('source_git_blob_sha') != 'e506db115d522d62618042abead7df2695ccf13e':
        raise ValueError('incorrect source Git blob')
    if data.get('source_file_size_bytes') != 289480:
        raise ValueError('incorrect source file size')
    if data.get('description_git_blob_sha') != 'a2bc0f1973cefd38759d7129d5b7573ab9f53b09':
        raise ValueError('incorrect description Git blob')
    fields = data.get('fields')
    if type(fields) is not dict or set(fields) != set(FIELD_UNITS):
        raise ValueError('fields mismatch the source description')
    for k,u in FIELD_UNITS.items():
        if type(fields[k]) is not dict or type(fields[k].get('meaning')) is not str or not fields[k]['meaning'] or fields[k].get('unit') != u:
            raise ValueError('invalid field metadata')
    for key in FAIL_CLOSED:
        if data.get(key) is not False:
            raise ValueError('unsupported scientific claim: ' + key)
    return {'status':STATUS,'documented_fields':len(fields),
            'source_file_size_bytes':data['source_file_size_bytes'],
            'dataset_ready_for_bhs':False,'real_data_experiment_executed':False,
            'physical_validation':False,'scored_validation_allowed':False,
            'independent_holdout_used':False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out-dir',default='runs/nist_source_contract_v1')
    args=parser.parse_args()
    raw=PATH.read_bytes()
    report=validate(json.loads(raw))
    report['contract_sha256']=hashlib.sha256(raw).hexdigest()
    out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    result=(json.dumps(report,sort_keys=True,indent=2)+'\n').encode()
    (out/'source_contract_report.json').write_bytes(result)
    (out/'source_contract_report.sha256').write_text(hashlib.sha256(result).hexdigest()+'  source_contract_report.json\n')
    print(json.dumps(report,sort_keys=True))

if __name__=='__main__':
    main()
