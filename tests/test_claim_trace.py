"""Every displayed model quote must trace to exact source bytes and character spans."""
import hashlib
import unittest

from offerproof import analyze
from cross_review import review_case


class ClaimTraceTests(unittest.TestCase):
    def assert_anchor(self, anchor, source, quote):
        self.assertIsInstance(anchor, dict, "Quoted claims have no exact source anchor")
        self.assertEqual(anchor["source_sha256"], hashlib.sha256(source.encode("utf-8")).hexdigest())
        self.assertEqual(anchor["offset_unit"], "unicode_codepoints")
        self.assertTrue(anchor["occurrences"])
        for span in anchor["occurrences"]:
            self.assertEqual(source[span["start"]:span["end"]], quote)

    def test_extracted_claim_and_its_question_share_the_source_anchor(self):
        message = "Intern at Harbor Systems"
        result = analyze(message, extractor=lambda _: {
            "claims": [{"snippet": "Harbor Systems", "category": "employer"}],
        })
        anchor = result["claims"][0].get("source_anchor")
        self.assert_anchor(anchor, message, "Harbor Systems")
        self.assertEqual(result["verification_questions"][0].get("source_anchor"), anchor)
        self.assertFalse(result["verified"])

    def test_repeated_quotes_keep_all_occurrences_without_inventing_one_location(self):
        message = "Harbor Systems invited you. Verify Harbor Systems independently."
        result = analyze(message, extractor=lambda _: {
            "claims": [{"snippet": "Harbor Systems", "category": "employer"}],
        })
        anchor = result["claims"][0].get("source_anchor")
        self.assert_anchor(anchor, message, "Harbor Systems")
        self.assertEqual(len(anchor["occurrences"]), 2)

    def test_unicode_quotes_use_explicit_codepoint_offsets(self):
        message = "📨 فرصة تدريب لدى شركة النهر"
        quote = "شركة النهر"
        result = analyze(message, extractor=lambda _: {
            "claims": [{"snippet": quote, "category": "employer"}],
        })
        self.assert_anchor(result["claims"][0].get("source_anchor"), message, quote)

    def test_comparison_anchors_both_the_message_and_the_observation(self):
        message = "Pay a training deposit of 20 dollars."
        observation = "No training deposit is required."
        notes = [{"kind": "company_careers", "source": "independent", "observation": observation}]
        result = review_case(message, notes, extractor=lambda *_: {
            "comparisons": [{"claim_quote": "training deposit of 20 dollars",
                             "note_quote": "No training deposit is required",
                             "kind": "payment_mismatch"}],
        })
        comparison = result["comparisons"][0]
        self.assert_anchor(comparison.get("message_anchor"), message, comparison["claim_quote"])
        self.assert_anchor(comparison.get("note_anchor"), observation, comparison["note_quote"])
        self.assertEqual(comparison["epistemic_status"], "hypothesis_not_verified")
        self.assertFalse(result["sender_authenticated"])


if __name__ == "__main__":
    unittest.main()
