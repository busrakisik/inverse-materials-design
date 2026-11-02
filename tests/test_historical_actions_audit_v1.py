import io, json, unittest
from scripts.historical_actions_audit_v1 import fetch_pages,STATUS
class Response(io.BytesIO):
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
def mock_open(data):
    def f(request,timeout):return Response(json.dumps(data).encode())
    return f
class AuditTests(unittest.TestCase):
    def test_single_page(self):
        x=fetch_pages('a/b',opener=mock_open({'total_count':1,'workflow_runs':[{'id':12,'name':'demo'}]}))
        self.assertTrue(x['pagination_complete']);self.assertEqual(x['runs_observed'],1)
    def test_no_approval(self):
        x=fetch_pages('a/b',opener=mock_open({'total_count':0,'workflow_runs':[]}))
        self.assertFalse(x['independent_validation_approved']);self.assertFalse(x['historical_seed_usage_verified'])
        self.assertEqual(x['status'],STATUS)
    def test_unavailable_missing_page(self):
        x=fetch_pages('a/b',opener=mock_open({'total_count':2,'workflow_runs':[{'id':1}]}))
        self.assertFalse(x['pagination_complete'])
    def test_bad_repository(self):
        with self.assertRaises(ValueError):fetch_pages('https://evil/',opener=mock_open({}))
    def test_bad_payload(self):
        with self.assertRaises(ValueError):fetch_pages('a/b',opener=mock_open({'x':1}))
    def test_duplicate(self):
        with self.assertRaises(ValueError):fetch_pages('a/b',opener=mock_open({'total_count':2,'workflow_runs':[{'id':1},{'id':1}]}))
    def test_page_limit(self):
        with self.assertRaises(ValueError):fetch_pages('a/b',max_pages=0)
if __name__=='__main__':unittest.main()
