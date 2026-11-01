import gzip,json,unittest
from scripts.matbench_integrity_gate import audit,parse

def fixture(formulas=None):
    formulas=formulas or [f'Li{i}O' for i in range(4604)]
    return gzip.compress(json.dumps({'columns':['composition','gap expt'],'data':[[f,1.5] for f in formulas]}).encode())
class Tests(unittest.TestCase):
    def test_safe_no_benchmark(self):
        x=audit(fixture());self.assertFalse(x['benchmark_run']);self.assertFalse(x['raw_data_published'])
    def test_hash_computed(self):self.assertEqual(len(audit(fixture())['repeat_sha256']),64)
    def test_parser_row_count(self):self.assertEqual(len(parse(fixture())),4604)
    def test_wrong_count(self):
        with self.assertRaises(ValueError):parse(fixture(['LiO']))
    def test_invalid_schema(self):
        with self.assertRaises(ValueError):parse(gzip.compress(json.dumps({'columns':['x'],'data':[]}).encode()))
    def test_invalid_gzip(self):
        with self.assertRaises(OSError):parse(b'not gzip')
    def test_duplicate_canonical_group(self):
        x=audit(fixture(['Li2O']*4604),canonicalize=lambda _: 'Li2O');self.assertEqual(x['reduced_formula_duplicate_rows'],4603)
    def test_canonical_failure_does_not_disappear(self):
        def fail(_):raise ValueError('bad formula')
        x=audit(fixture(),canonicalize=fail);self.assertEqual(x['chemical_equivalence_status'],'FAILED');self.assertEqual(x['unparseable_formula_count'],4604)
if __name__=='__main__':unittest.main()
