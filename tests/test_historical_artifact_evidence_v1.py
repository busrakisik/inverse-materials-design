import io,json,pathlib,tempfile,unittest,zipfile
from scripts.historical_artifact_evidence_v1 import scan_zip,seed_values,inventory
class Tests(unittest.TestCase):
    def make(self,entries):
        t=tempfile.TemporaryDirectory();p=pathlib.Path(t.name)/'test.zip'
        with zipfile.ZipFile(p,'w') as z:
            for name,data in entries.items():z.writestr(name,data)
        self.addCleanup(t.cleanup);return p
    def test_seed_extraction(self):self.assertEqual(seed_values({'seed':5,'nested':[{'task_seed':6}]}),[5,6])
    def test_reject_boolean_seed(self):self.assertEqual(seed_values({'seed':True}),[])
    def test_detect_overlap(self):
        x=scan_zip(self.make({'pilot.jsonl':'{"seed":10005}\n{"seed":12}\n'}));self.assertEqual(x['proposed_seed_overlaps'],[10005]);self.assertFalse(x['scored_validation_allowed'])
    def test_csv_seed(self):self.assertEqual(scan_zip(self.make({'a.csv':'seed,value\n3,0.2\n'}))['observed_seeds'],[3])
    def test_missing_seed_not_approval(self):self.assertFalse(scan_zip(self.make({'a.json':'{}'}))['all_historical_runs_covered'])
    def test_oversized_rejected(self):
        p=self.make({'a.json':'x'*8000001})
        with self.assertRaises(ValueError):scan_zip(p)
    def test_bad_repo(self):
        with self.assertRaises(ValueError):inventory('../bad')
    def test_metadata_not_proof(self):
        class Resp:
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def read(self,*a):return json.dumps({'total_count':1,'artifacts':[{'id':7,'name':'pilot','workflow_run':{'id':4}}]}).encode()
        x=inventory('a/b',opener=lambda *a,**k:Resp());self.assertEqual(x['count'],1);self.assertFalse(x['seed_usage_fully_verified'])
if __name__=='__main__':unittest.main()
