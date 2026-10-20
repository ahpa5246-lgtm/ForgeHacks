# Exact quote traceability

Accepted extracted claims carry a `source_anchor`: the UTF-8 SHA-256 of the supplied message and every exact occurrence of the quote. Verification questions preserve the same anchor. Cross-evidence comparisons carry separate `message_anchor` and `note_anchor` records.

Spans are zero-based, half-open `start`/`end` offsets measured in Unicode code points, explicitly labelled `unicode_codepoints`. Browser clients must account for JavaScript's UTF-16 indexing before highlighting text containing characters such as emoji. Repeated or overlapping quotes retain all locations.

The note anchor identifies the whitespace-trimmed observation displayed in the provenance graph. A changed source text produces a different digest. These records identify the text used by the analysis; they do not authenticate its author, establish independent provenance or verify a real-world claim. No user text or anchor is persisted by this change.

Python regressions exercise repeated English quotes, Arabic following emoji, shared claim/question anchors, and both sides of a comparison. Existing browser tests exercise the unchanged user journeys.
