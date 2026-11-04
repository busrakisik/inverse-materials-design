"""Static publication claim-register checks; no benchmark invocation or holdout access."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

REGISTER = Path('research/PUBLICATION_CLAIMS_REGISTER_V1.json')
EXPECTED_STATUS = 'BHS_PUBLICATION_CLAIMS_REGISTER_DEVELOPMENT_ONLY'

def validate_claim_register(data):
    if type(data) is not dict or data.get('status') != EXPECTED_STATUS:
        raise ValueError('unexpected claim register')
    for field in ('independent_holdout_used', 'scored_validation_allowed',
                  'superiority_claim_validated', 'materials_discovery_validated',
                  'commercial_roi_validated'):
        if data.get(field) is not False:
            raise ValueError('research-claim gate must remain false: ' + field)
    evidence = data.get('evidence', {})
    if any(evidence.get(key) != expected for key, expected in (
        ('specific_unit_tests_passed', 15), ('paired_development_conditions', 24),
        ('policy_variants', 4), ('campaign_rows', 96), ('comparisons_to_eig', 72),
        ('cost_cap_arbitrary_units', 8))):
        raise ValueError('mismatch with reviewed development manifest')
    claims = data.get('claims')
    if not isinstance(claims, list) or len(claims) != 6 or len({c.get('id') for c in claims}) != 6:
        raise ValueError('claim inventory not complete')
    disallowed = {"C02", "C03", "C04", "C06"}
    for c in claims:
        if c.get('id') in disallowed and c.get('classification') != 'unsupported':
            raise ValueError('unsupported publication claim upgraded without review')
    return {'status': EXPECTED_STATUS, 'claim_count':len(claims),
            'unsupported_claims':sum(c.get('classification')=='unsupported' for c in claims),
            'scored_validation_allowed': False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--register',default=str(REGISTER))
    args=p.parse_args()
    data=json.loads(Path(args.register).read_text(encoding='utf-8'))
    print(json.dumps(validate_claim_register(data),sort_keys=True))

if __name__ == '__main__':main()
