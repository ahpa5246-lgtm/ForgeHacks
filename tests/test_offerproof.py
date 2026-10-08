import json
import io
import unittest
from unittest.mock import patch

from offerproof import Handler, analyze, groq_extract


class AnalysisTests(unittest.TestCase):
    def test_live_adapter_parses_provider_reply_without_exposing_key(self):
        class Reply:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self):
                return json.dumps({"choices": [{"message": {"content": json.dumps({"claims": [{"snippet": "Intern", "category": "role"}]})}}]}).encode()
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-secret"}), patch("offerproof.urlopen", return_value=Reply()) as call:
            claims = groq_extract("Intern role")
        self.assertEqual(claims["claims"][0]["snippet"], "Intern")
        self.assertTrue(call.call_args.args[0].full_url.startswith("https://api.groq.com/"))
        self.assertNotIn("test-secret", str(claims))

    def test_upfront_payment_is_flagged_without_claiming_verified(self):
        result = analyze("Pay a $29 training deposit to secure your remote job tonight.")
        self.assertEqual(result["status"], "red_flag_observed")
        self.assertIn("upfront_payment", result["red_flags"])
        self.assertFalse(result["verified"])

    def test_plausible_message_stays_unverified(self):
        result = analyze("We invite you to interview for an internship at Harbor Systems.")
        self.assertEqual(result["status"], "unverified")
        self.assertFalse(result["verified"])
        self.assertEqual(result["contact_policy"], "do_not_trust_message_or_ai_contacts")

    def test_ai_cannot_add_verified_status_or_contact_link(self):
        def malicious(_):
            return {"employer": "Harbor Systems", "role": "Intern", "url": "https://fake.example", "verified": True,
                    "claims": ["Interview offered"], "red_flags": ["upfront_payment"]}
        result = analyze("Interview offer from Harbor Systems", extractor=malicious)
        self.assertFalse(result["verified"])
        self.assertNotIn("url", result["claims"])
        self.assertNotIn("https://fake.example", json.dumps(result))
        self.assertEqual(result["status"], "unverified")

    def test_model_failure_uses_disclosed_fallback(self):
        def broken(_):
            raise TimeoutError("provider timeout")
        result = analyze("Send your password for the job", extractor=broken)
        self.assertEqual(result["mode"], "rules_fallback")
        self.assertIn("credential_request", result["red_flags"])

    def test_negated_fee_does_not_trigger_payment_flag(self):
        result = analyze("An internship interview is offered; no fee is mentioned.")
        self.assertNotIn("upfront_payment", result["red_flags"])

    def test_equipment_check_pattern_is_flagged(self):
        result = analyze("We will send you a check to buy equipment from our supplier.")
        self.assertIn("equipment_check", result["red_flags"])


class HttpTests(unittest.TestCase):
    def call(self, path, payload):
        raw = json.dumps(payload).encode()
        handler = Handler.__new__(Handler)
        handler.path = path
        handler.headers = {"Content-Length": str(len(raw))}
        handler.rfile = io.BytesIO(raw)
        handler.wfile = io.BytesIO()
        status = []
        handler.send_response = lambda code: status.append(code)
        handler.send_header = lambda *_: None
        handler.end_headers = lambda: None
        handler.do_POST()
        return status[0], json.loads(handler.wfile.getvalue())

    def test_analyze_endpoint(self):
        status, data = self.call("/api/analyze", {"message": "Pay $20 now"})
        self.assertEqual(status, 200)
        self.assertIn("upfront_payment", data["red_flags"])

    def test_rejects_large_request(self):
        status, _ = self.call("/api/analyze", {"message": "a" * 51000})
        self.assertEqual(status, 413)

    def test_does_not_expose_key_or_arbitrary_files(self):
        status, _ = self.call("/../offerproof.py", {"message": "hello"})
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
