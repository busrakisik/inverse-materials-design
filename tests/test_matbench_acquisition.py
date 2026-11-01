import gzip, json, unittest
from acquire_matbench_expt_gap import inspect, read_table


def fixture(n=4604):
    return gzip.compress(json.dumps({'columns':['composition','gap expt'],'index':list(range(n)),'data':[[f'A{i}B',float(i%5)] for i in range(n)]}).encode())


class AcquisitionTests(unittest.TestCase):
    def test_positive_contract(self):
        m=inspect(fixture())
        self.assertEqual(m['rows'],4604)
        self.assertEqual(m['status'],'RAW_FILE_AND_SCHEMA_VERIFIED_LICENSE_NOT_CLEARED')
        self.assertFalse(m['benchmark_run'])
    def test_no_implicit_license_clearance(self):
        self.assertEqual(inspect(fixture())['license_review'],'PENDING_MANUAL_VERIFICATION')
    def test_incorrect_rows(self):
        with self.assertRaises(ValueError):inspect(fixture(50))
    def test_unrecognized_columns(self):
        with self.assertRaises(ValueError):read_table(gzip.compress(json.dumps({'columns':['x','y'],'data':[[1,2]]}).encode()))
    def test_nan_rejected(self):
        raw=gzip.compress(json.dumps({'columns':['composition','gap expt'],'data':[['A',float('nan')]]*4604}).encode())
        with self.assertRaises(ValueError):inspect(raw)
    def test_corrupt_gzip(self):
        with self.assertRaises(ValueError):read_table(b'not-gzip')
    def test_negative_label_rejected(self):
        raw=gzip.compress(json.dumps({'columns':['composition','gap expt'],'data':[['A',-1]]*4604}).encode())
        with self.assertRaises(ValueError):inspect(raw)

if __name__=='__main__':unittest.main()
