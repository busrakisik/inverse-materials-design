import io,json,pathlib,sys,tempfile,unittest,zipfile
from unittest.mock import patch
from scripts import evidence_reconciliation_v1 as m

class EvidenceReconciliationTests(unittest.TestCase):
 def test_pinned_five(self):self.assertEqual(len(m.SOURCES),5)
 def test_digest(self):self.assertEqual(m.digest(b'abc'),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
 def test_empty_artifacts_fail(self):
  with self.assertRaises(ValueError):m.reconcile({})
 def test_wrong_digest(self):
  with self.assertRaises(ValueError):m.read_zip(b'bad','0'*64,'a.json')
 def test_valid_minimal_zip(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:z.writestr('foo.json',json.dumps({'x':3}))
  self.assertEqual(m.read_zip(b.getvalue(),m.digest(b.getvalue()),'foo.json')[0]['x'],3)
 def test_missing_entry(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:z.writestr('foo.json','{}')
  with self.assertRaises(ValueError):m.read_zip(b.getvalue(),m.digest(b.getvalue()),'other.json')
 def test_path_traversal(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:z.writestr('../escape','bad');z.writestr('foo.json','{}')
  with self.assertRaises(ValueError):m.read_zip(b.getvalue(),m.digest(b.getvalue()),'foo.json')
 def test_duplicate_zip_member(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:
   z.writestr('foo.json','{}');
   import warnings
   with warnings.catch_warnings():warnings.simplefilter('ignore');z.writestr('foo.json','{}')
  with self.assertRaises(ValueError):m.read_zip(b.getvalue(),m.digest(b.getvalue()),'foo.json')
 def test_token_required(self):
  with self.assertRaises(ValueError):m.download_artifact(1,'')
 def test_status_cannot_approve(self):self.assertIn('NO_HOLDOUT',m.STATUS)

if __name__=='__main__':unittest.main()
