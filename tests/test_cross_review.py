import io
import json
import unittest
from unittest.mock import patch

from cross_review import review_case, groq_compare
from offerproof import Handler


CASE = "Harbor Systems invites you to a Software Engineering internship starting July 1."
NOTES = [
    {"kind": "other", "source": "message",
     "observation": "Recruiter linked to a Software Engineering job listing."},
    {"kind": "company_careers", "source": "independent",
     "observation": "A separately located jobs page lists a Data Analyst internship starting August."},
]


class ComparisonTests(unittest.TestCase):
    def test_source_quote_bound_comparison(self):
        def fake_model(_message, _notes):
            return {"verified": True, "contact_url": "https://made-up.invalid", "comparisons": [
                {"claim_quote": "Software Engineering internship",
                 "note_quote": "Data Analyst internship", "kind": "role_mismatch"},
                {"claim_quote": "Fictitious title",
                 "note_quote": "Data Analyst internship", "kind": "other"},
                {"claim_quote": "Software Engineering internship",
                 "note_quote": "Fictitious note content", "kind": "other"},
            ]}
        result = review_case(CASE, NOTES, extractor=fake_model)
        self.assertEqual(result["mode"], "ai_compare")
        self.assertEqual(len(result["comparisons"]), 1)
        self.assertEqual(result["comparisons"][0]["note_index"], 1)
        self.assertEqual(result["comparisons"][0]["note_classification"],
                         "self_reported_independent")
        self.assertEqual(result["comparisons"][0]["epistemic_status"],
                         "hypothesis_not_verified")
        self.assertFalse(result["sender_authenticated"])
        self.assertNotIn("made-up.invalid", json.dumps(result))

    def test_malicious_model_can_never_create_new_contact_or_verdict(self):
        data={"comparisons":[{"claim_quote":"Harbor Systems",
                              "note_quote":"Data Analyst internship",
                              "kind":"other","verified":True,
                              "explanation":"Contact https://hijack.invalid"}]}
        result=review_case(CASE, NOTES, extractor=lambda *_: data)
        self.assertEqual(len(result["comparisons"]), 1)
        self.assertNotIn("hijack.invalid", json.dumps(result))
        self.assertEqual(result["status"], "unverified")

    def test_invalid_comparison_falls_back_without_claims(self):
        result=review_case(CASE, NOTES, extractor=lambda *_: {"comparisons":"yes"})
        self.assertEqual(result["mode"], "rules_fallback")
        self.assertEqual(result["comparisons"], [])

    def test_provider_failure_falls_back(self):
        def bad(*_): raise TimeoutError("model timeout")
        result=review_case(CASE, NOTES, extractor=bad)
        self.assertEqual(result["comparisons"], [])
        self.assertEqual(result["mode"], "rules_fallback")

    def test_evidence_dependency_is_separate_from_semantic_contradiction(self):
        notes=[
            {"kind":"other","source":"message","observation":"Sender's job listing"},
            {"kind":"company_contact","source":"independent","derived_from":0,
             "observation":"A third-party summary says Data Analyst internship."},
        ]
        result=review_case(CASE,notes,extractor=lambda *_:{
            "comparisons":[{"claim_quote":"Software Engineering internship",
                            "note_quote":"Data Analyst internship",
                            "kind":"role_mismatch"}]})
        self.assertEqual(result["comparisons"][0]["note_classification"],
                         "source_collapse")
        self.assertFalse(result["sender_authenticated"])

    def test_empty_evidence_cannot_trigger_provider(self):
        result=review_case(CASE,[],extractor=lambda *_: self.fail("should not call"))
        self.assertEqual(result["mode"],"rules_fallback")

    def test_provider_schema_uses_json_object_without_exposing_key(self):
        class Reply:
            def __enter__(self): return self
            def __exit__(self,*_): return False
            def read(self):
                return json.dumps({"choices":[{"message":{"content": '{"comparisons":[]}'}}]}).encode()
        with patch.dict("os.environ",{"GROQ_API_KEY":"fake-secret"}), \
             patch("cross_review.urlopen",return_value=Reply()) as patched:
            result=groq_compare(CASE,NOTES)
        self.assertEqual(result,{"comparisons":[]})
        request=patched.call_args.args[0]
        self.assertEqual(json.loads(request.data)["response_format"],{"type":"json_object"})
        self.assertNotIn("fake-secret",json.dumps(result))


class HttpComparisonTests(unittest.TestCase):
    def test_http_compare_contract_with_model_unavailable(self):
        raw=json.dumps({"message":CASE,"evidence":NOTES,"groq_consent":True}).encode()
        handler=Handler.__new__(Handler)
        handler.path="/api/compare"
        handler.client_address=("test-audience",123)
        handler.headers={"Content-Length":str(len(raw))}
        handler.rfile=io.BytesIO(raw);handler.wfile=io.BytesIO()
        codes=[]
        handler.send_response=lambda code:codes.append(code)
        handler.send_header=lambda *_:None
        handler.end_headers=lambda:None
        with patch.dict("os.environ",{"GROQ_API_KEY":""}):
            handler.do_POST()
        output=json.loads(handler.wfile.getvalue())
        self.assertEqual(codes[0],200)
        self.assertEqual(output["mode"],"rules_fallback")
        self.assertEqual(len(output["graph"]["nodes"]),2)
        self.assertFalse(output["sender_authenticated"])


if __name__=="__main__":
    unittest.main()
