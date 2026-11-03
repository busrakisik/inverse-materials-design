import io
import unittest
import urllib.error
from email.message import Message
from scripts.evidence_reconciliation_v1 import download_artifact, _trusted_artifact_host, MAX_ZIP

class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

class FakeOpener:
    def __init__(self, location, payload=b'zipbytes', first_status=302):
        self.location=location;self.payload=payload;self.first_status=first_status;self.requests=[]
    def open(self, req, timeout=30):
        self.requests.append(req)
        if len(self.requests)==1:
            if self.first_status==200:return Response(self.payload)
            h=Message();h['Location']=self.location
            raise urllib.error.HTTPError(req.full_url,self.first_status,'redirect',h,None)
        return Response(self.payload)

class RedirectTests(unittest.TestCase):
    def test_blob_request_without_bearer(self):
        op=FakeOpener('https://productionresults.blob.core.windows.net/signed/path?sig=secret')
        self.assertEqual(download_artifact(123,'test-token',opener=op),b'zipbytes')
        self.assertEqual(len(op.requests),2)
        self.assertIn('Bearer test-token',dict(op.requests[0].header_items())['Authorization'])
        self.assertNotIn('Authorization',dict(op.requests[1].header_items()))
    def test_no_redirect_200(self):
        op=FakeOpener('',first_status=200)
        self.assertEqual(download_artifact(1,'token',opener=op),b'zipbytes')
        self.assertEqual(len(op.requests),1)
    def test_untrusted_cross_domain_rejected(self):
        op=FakeOpener('https://attacker.example/artifact')
        with self.assertRaisesRegex(ValueError,'untrusted'): download_artifact(1,'token',opener=op)
        self.assertEqual(len(op.requests),1)
    def test_http_rejected(self):
        op=FakeOpener('http://productionresults.blob.core.windows.net/file')
        with self.assertRaisesRegex(ValueError,'untrusted'): download_artifact(1,'token',opener=op)
    def test_auth_not_in_error(self):
        class BadOpener:
            def open(self,req,timeout=30):
                raise urllib.error.HTTPError(req.full_url,401,'unauthorized',Message(),None)
        with self.assertRaises(RuntimeError) as e:download_artifact(1,'topsecret',opener=BadOpener())
        self.assertNotIn('topsecret',str(e.exception))
    def test_oversize_rejected(self):
        op=FakeOpener('',payload=b'x'*(MAX_ZIP+1),first_status=200)
        with self.assertRaisesRegex(ValueError,'too large'):download_artifact(1,'token',opener=op)
    def test_missing_token_rejected(self):
        with self.assertRaisesRegex(ValueError,'token required'):download_artifact(1,'')
    def test_safe_host_matching(self):
        self.assertFalse(_trusted_artifact_host('fakeblob.core.windows.net.evil.com'))
        self.assertTrue(_trusted_artifact_host('productionresultssa.blob.core.windows.net'))
        self.assertTrue(_trusted_artifact_host('objects.githubusercontent.com'))

if __name__=='__main__':unittest.main()
