"""Gemini adapter tests using fake provider responses. No actual keys or network."""
import io
import json
import os
import unittest
from unittest.mock import patch
from offerproof import Handler, groq_extract, analyze
from cross_review import groq_compare, review_case
from provider import provider_connection, configured_provider

CASE = "Harbor Systems offers a Software Engineering internship in July."
NOTES = [{"kind":"other","source":"independent","observation":"The company page says Data Analyst instead."}]

class Reply:
    def __init__(self, content):
        self.content = content
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self):
        return json.dumps({"choices":[{"message":{"content":json.dumps(self.content)}}]}).encode()

class ProviderTests(unittest.TestCase):
    @patch.dict(os.environ, {"GROQ_API_KEY":"g-secret","google":"google-secret"},clear=True)
    def test_gemini_alias_selected_before_groq_without_exposure(self):
        c=provider_connection()
        self.assertEqual(configured_provider(),"gemini")
        self.assertEqual(c["provider"],"gemini")
        self.assertEqual(c["model"],"gemini-3.8-flash")
        self.assertTrue(c["url"].startswith("https://generativelanguage.googleapis.com/"))

    @patch.dict(os.environ, {"google":"google-secret"},clear=True)
    def test_analysis_uses_google_json_api_and_source_quotes(self):
        output={"claims":[{"snippet":"Harbor Systems","category":"employer"}],"signals":[]}
        with patch("offerproof.urlopen",return_value=Reply(output)) as call:
            result=analyze(CASE)
        self.assertEqual(result["mode"],"ai_extract")
        self.assertEqual(result["claims"][0]["snippet"],"Harbor Systems")
        self.assertFalse(result["verified"])
        request=call.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/v1beta/openai/chat/completions"))
        params=json.loads(request.data)
        self.assertEqual(params["model"],"gemini-3.8-flash")
        self.assertEqual(params["response_format"],{"type":"json_object"})
        self.assertNotIn("reasoning_format",params)
        self.assertNotIn("google-secret",json.dumps(result))

    @patch.dict(os.environ, {"GEMINI_API_KEY":"gemini-secret"},clear=True)
    def test_comparison_provenance_preserved_with_gemini(self):
        content={"comparisons":[{"claim_quote":"Software Engineering",
                                  "note_quote":"Data Analyst","kind":"role_mismatch"}]}
        with patch("cross_review.urlopen",return_value=Reply(content)) as call:
            result=review_case(CASE,NOTES)
        self.assertEqual(result["mode"],"ai_compare")
        self.assertEqual(result["comparisons"][0]["note_classification"],
                         "self_reported_independent")
        self.assertFalse(result["sender_authenticated"])
        self.assertTrue(call.call_args.args[0].full_url.startswith(
            "https://generativelanguage.googleapis.com/"))

    @patch.dict(os.environ, {"google":"private-secret"},clear=True)
    def test_local_analyze_never_contacts_gemini_without_consent(self):
        payload=json.dumps({"message":CASE}).encode()
        handler=Handler.__new__(Handler)
        handler.path="/api/analyze"
        handler.client_address=("local-gemini-test",1)
        handler.headers={"Content-Length":str(len(payload))}
        handler.rfile=io.BytesIO(payload)
        handler.wfile=io.BytesIO()
        codes=[]
        handler.send_response=lambda status:codes.append(status)
        handler.send_header=lambda *_:None
        handler.end_headers=lambda:None
        with patch("offerproof.urlopen",side_effect=AssertionError("external call")):
            handler.do_POST()
        result=json.loads(handler.wfile.getvalue())
        self.assertEqual(codes[0],200)
        self.assertEqual(result["mode"],"rules_fallback")
        self.assertFalse(result["external_ai_requested"])

    @patch.dict(os.environ, {"google":"private-secret"},clear=True)
    def test_health_mentions_provider_not_key(self):
        handler=Handler.__new__(Handler)
        handler.path="/health"
        handler.wfile=io.BytesIO()
        handler.send_response=lambda status:None
        handler.send_header=lambda *_:None
        handler.end_headers=lambda:None
        handler.do_GET()
        data=json.loads(handler.wfile.getvalue())
        self.assertEqual(data["ai_provider"],"gemini")
        self.assertTrue(data["ai_configured"])
        self.assertNotIn("private-secret",json.dumps(data))

if __name__=="__main__": unittest.main()
