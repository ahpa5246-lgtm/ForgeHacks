import json
import io
import unittest
from time import monotonic
from unittest.mock import patch

from offerproof import Handler, analyze, assess_evidence, response_steps, groq_extract, allow_demo_call


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

    def test_app_does_not_stop_model_after_thirty_requests(self):
        class Reply:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self):
                return json.dumps({"choices": [{"message": {"content": '{"claims": []}'}}]}).encode()
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-secret"}), patch("offerproof.urlopen", side_effect=lambda *_args, **_kwargs: Reply()) as call:
            modes = [analyze("Interview invitation for an internship")["mode"] for _ in range(31)]
        self.assertEqual(modes, ["ai_extract"] * 31)
        self.assertEqual(call.call_count, 31)

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

    def test_ai_cautions_are_source_bound_and_never_verify(self):
        def extractor(_):
            return {"claims": [], "verified": True, "signals": [
                {"kind": "urgency", "snippet": "before lunch", "url": "https://fake.invalid"},
                {"kind": "impersonation", "snippet": "made up claim"},
                {"kind": "payment", "snippet": "before lunch", "explanation": "User-generated fake advice"}]}
        result = analyze("Reply before lunch for an interview.", extractor=extractor)
        self.assertFalse(result["verified"])
        self.assertEqual(len(result["ai_attention"]), 2)
        self.assertEqual(result["status"], "unverified")
        self.assertNotIn("fake.invalid", json.dumps(result))
        self.assertNotIn("User-generated fake advice", json.dumps(result))

    def test_model_failure_uses_disclosed_fallback(self):
        def broken(_):
            raise TimeoutError("provider timeout")
        result = analyze("Send your password for the job", extractor=broken)
        self.assertEqual(result["mode"], "rules_fallback")
        self.assertIn("credential_request", result["red_flags"])


    def test_explicit_denials_do_not_trigger_known_flags(self):
        examples = [
            ("We will never ask you to pay a fee.", "upfront_payment"),
            ("Never share your password.", "credential_request"),
            ("We will not ask for your passport.", "sensitive_data_request"),
        ]
        for message, flag in examples:
            self.assertNotIn(flag, analyze(message, extractor=lambda _: None)["red_flags"])

    def test_multi_parent_source_collapse(self):
        items = [
            {"kind": "other", "source": "message", "observation": "Sender link"},
            {"kind": "other", "source": "independent", "observation": "Independent channel"},
            {"kind": "company_careers", "source": "independent",
             "observation": "A later page depends on both", "derived_from": [0, 1]},
        ]
        result = assess_evidence(items)
        self.assertIn(2, result["source_collapses"])
        self.assertEqual(result["nodes"][2]["tainted_by"], ["message"])
        self.assertEqual(len(result["edges"]), 3)
        self.assertFalse(result["sender_authenticated"])

    def test_claim_based_questions_are_source_bounded(self):
        result = analyze("Intern at Harbor Systems", extractor=lambda _: {
            "claims": [{"snippet": "Harbor Systems", "category": "employer"}]})
        self.assertEqual(len(result["verification_questions"]), 1)
        self.assertFalse(result["verified"])

    def test_negated_fee_does_not_trigger_payment_flag(self):
        result = analyze("An internship interview is offered; no fee is mentioned.")
        self.assertNotIn("upfront_payment", result["red_flags"])

    def test_equipment_check_pattern_is_flagged(self):
        result = analyze("We will send you a check to buy equipment from our supplier.")
        self.assertIn("equipment_check", result["red_flags"])

    def test_careers_listing_does_not_authenticate_recruiter(self):
        result = assess_evidence([{"kind": "company_careers", "observation": "Job listing exists", "source": "independent"}])
        self.assertFalse(result["sender_authenticated"])
        self.assertEqual(result["status"], "unverified")
        self.assertIn("listing", result["remaining_questions"][0].lower())

    def test_link_from_original_message_is_not_independent_evidence(self):
        result = assess_evidence([{"kind": "company_careers", "observation": "Job listing exists", "source": "message"}])
        self.assertEqual(result["accepted_evidence"], [])
        self.assertEqual(result["status"], "unverified")

    def test_source_collapse_through_intermediate_note(self):
        notes = [
            {"kind": "other", "observation": "Search result copied the recruiter link", "source": "message"},
            {"kind": "company_careers", "observation": "The page repeats the role", "source": "independent", "derived_from": 0},
        ]
        result = assess_evidence(notes)
        self.assertEqual(result["accepted_evidence"], [])
        self.assertIn(1, result["source_collapses"])

    def test_independent_sources_remain_unverified(self):
        notes = [
            {"kind": "company_careers", "observation": "Role listed", "source": "independent"},
            {"kind": "company_contact", "observation": "I called a known switchboard", "source": "independent"},
        ]
        result = assess_evidence(notes)
        self.assertEqual(len(result["accepted_evidence"]), 2)
        self.assertFalse(result["sender_authenticated"])

    def test_invalid_future_dependency_is_rejected(self):
        with self.assertRaises(ValueError):
            assess_evidence([{"kind": "other", "observation": "A", "source": "independent", "derived_from": 0}])

    def test_action_after_password_disclosure_is_separate_from_offer_rating(self):
        steps = response_steps(["shared_password"])
        self.assertTrue(any("password" in step.lower() for step in steps))
        self.assertTrue(any("multi-factor" in step.lower() for step in steps))


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

    def test_assess_endpoint_does_not_return_verified(self):
        status, data = self.call("/api/assess", {"evidence": [{"kind": "company_careers", "observation": "Job listing exists", "source": "independent"}]})
        self.assertEqual(status, 200)
        self.assertFalse(data["sender_authenticated"])


class ReleaseChecks(unittest.TestCase):
    def get(self, path):
        handler = Handler.__new__(Handler)
        handler.path = path
        handler.wfile = io.BytesIO()
        statuses, headers = [], []
        handler.send_response = lambda code: statuses.append(code)
        handler.send_header = lambda key, value: headers.append((key, value))
        handler.end_headers = lambda: None
        handler.do_GET()
        return statuses[0], dict(headers), handler.wfile.getvalue()

    def test_frontend_assets_are_served_with_safe_mime_types(self):
        for path, content_type, marker in [
            ("/", "text/html; charset=utf-8", b"Investigation Workspace"),
            ("/dashboard.css", "text/css; charset=utf-8", b".hero"),
            ("/dashboard.js", "text/javascript; charset=utf-8", b"renderGraph"),
        ]:
            with self.subTest(path=path):
                status, headers, body = self.get(path)
                self.assertEqual(status, 200)
                self.assertEqual(headers["Content-Type"], content_type)
                self.assertIn(marker, body)
                self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
                self.assertEqual(headers["Referrer-Policy"], "no-referrer")
                self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
                self.assertNotIn("'unsafe-inline'", headers["Content-Security-Policy"])

    def test_unknown_or_sensitive_paths_rejected(self):
        for path in ("/offerproof.py", "/../offerproof.py", "/.env", "/dashboard.css?other=1"):
            with self.subTest(path=path):
                status, _, _ = self.get(path)
                self.assertEqual(status, 404)

    def test_frontend_has_navigation_and_no_html_injection_renderer(self):
        from pathlib import Path
        base = Path(__file__).resolve().parents[1]
        html = (base / "index.html").read_text(encoding="utf-8")
        javascript = (base / "dashboard.js").read_text(encoding="utf-8")
        for section in ("view-overview", "view-inspect", "view-evidence", "view-response"):
            self.assertIn(section, html)
        self.assertIn("source-collapse", html)
        self.assertIn("textContent", javascript)
        self.assertNotIn("innerHTML", javascript)
        self.assertNotIn("eval(", javascript)

    def test_demo_rate_limit_is_bounded_and_resets(self):
        marker = "limit-check-"+str(id(self))
        now = monotonic()
        for _ in range(12):
            self.assertTrue(allow_demo_call(marker, now=now))
        self.assertFalse(allow_demo_call(marker, now=now))
        self.assertTrue(allow_demo_call(marker, now=now+61))


if __name__ == "__main__":
    unittest.main()
