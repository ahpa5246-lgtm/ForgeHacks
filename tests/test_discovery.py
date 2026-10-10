import unittest
from discovery import message_source_seeds
from offerproof import analyze


class OfflineSourceTests(unittest.TestCase):
    def test_extracts_hostname_without_query_or_path(self):
        message = ("See https://jobs.harborsystems.example/opening/122?token=private_code "
                   "and https://jobs.harborsystems.example/other")
        notes = message_source_seeds(message)
        self.assertEqual(len(notes), 1)
        self.assertIn("jobs.harborsystems.example", notes[0]["observation"])
        self.assertNotIn("private_code", str(notes))
        self.assertNotIn("/opening", str(notes))
        self.assertEqual(notes[0]["source"], "message")

    def test_analyze_can_seed_graph_without_ai_or_external_network(self):
        message="Consider https://jobs.harborsystems.example/offer"
        result=analyze(message, extractor=lambda _: None)
        self.assertEqual(result["mode"], "rules_fallback")
        self.assertEqual(len(result["message_source_seeds"]), 1)
        self.assertFalse(result["verified"])

    def test_malformed_and_disallowed_schemes_are_ignored(self):
        text="javascript:alert(1) ftp://fake.example/jobs https://bad..example/x"
        self.assertEqual(message_source_seeds(text), [])

    def test_deduplicate_and_limit_hostnames(self):
        msg=" ".join("https://demo"+str(i)+".example/path" for i in range(6))
        self.assertEqual(len(message_source_seeds(msg)), 3)

    def test_never_echo_userinfo_or_secrets_in_reportable_seed(self):
        notes=message_source_seeds("https://user:pass@fake.example/secret?credential=private")
        self.assertEqual(len(notes),1)
        self.assertNotIn("pass",notes[0]["observation"])
        self.assertNotIn("credential",notes[0]["observation"])
        self.assertIn("fake.example",notes[0]["observation"])


if __name__ == "__main__":
    unittest.main()
