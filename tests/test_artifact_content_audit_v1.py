import json, pathlib, tempfile, unittest, zipfile
from scripts.artifact_content_audit_v1 import audit_zip

class EvidenceTests(unittest.TestCase):
    def make_archive(self,folder,mutate=None):
        p=pathlib.Path(folder)/'pilot.zip'
        rows=[{'scenario':s,'seed':i,'budget':b,'policy':method,'queries':b,
             'trace':[{'candidate_id':f'c_{k}'} for k in range(b)]}
              for s in ['smooth','multimodal','uninformative','mismatched','duplicates']
              for i in range(30) for b in [1,2,5,10] for method in ['random','greedy','bayesian_only']]
        if mutate: mutate(rows)
        with zipfile.ZipFile(p,'w') as z:
            z.writestr('runs/paired_pilot_v1/pilot_raw.jsonl','\n'.join(json.dumps(x) for x in rows)+'\n')
            z.writestr('runs/paired_pilot_v1/pilot_manifest.json',json.dumps({'n_rows':1800,'n_pairs':30,'confirmatory':False,'synthetic_only':True}))
        return p
    def test_actual_structure(self):
        with tempfile.TemporaryDirectory() as d:
            r=audit_zip(self.make_archive(d));self.assertEqual(r['pilot_rows_verified'],1800)
    def test_30_seeds(self):
        with tempfile.TemporaryDirectory() as d:self.assertEqual(audit_zip(self.make_archive(d))['observed_task_seeds'],list(range(30)))
    def test_not_approved(self):
        with tempfile.TemporaryDirectory() as d:self.assertFalse(audit_zip(self.make_archive(d))['scored_validation_allowed'])
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):audit_zip(self.make_archive(d,lambda x:x.__setitem__(1,dict(x[0]))))
    def test_holdout_seed_rejected_by_spec(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):audit_zip(self.make_archive(d,lambda x:x[0].update(seed=10000)))
    def test_budget_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):audit_zip(self.make_archive(d,lambda x:x[0].update(queries=99)))
    def test_missing_file_rejected(self):
        with self.assertRaises(ValueError):audit_zip('/this/does/not/exist.zip')
    def test_bad_zip_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'bad.zip';p.write_bytes(b'not zip')
            with self.assertRaises(zipfile.BadZipFile):audit_zip(p)
if __name__=='__main__':unittest.main()
