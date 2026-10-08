# ForgeHacks strategy decision — 8 October 2026

## Decision

Continue with **OfferProof as an evidence-provenance and response rehearsal**, rather than pitching an AI scam score. Its differentiator is a traceable source chain: a seemingly independent page may lead back to the recruiter's original link or an AI suggestion. The demo must make that failure visible and never mark a sender safe. The current prototype is still a candidate, not a proven winner.

## Contest fit and competitive pressure

The published cybersecurity prompt calls for AI tools that help recognize, prevent, verify or respond to modern scams, impersonation and fraud. Judges separately score impact, AI implementation depth, innovation, completion, and presentation. The project gallery is unpublished as of this review, so participating teams cannot yet be compared. The public JobScamScore product already markets paste-to-score analysis, cited red flags, source checks and responses. Copying that shape with fewer checks would be a weak entry.

Sources: [ForgeHacks tracks](https://forgehacks.vercel.app/), [official rules](https://forgehacks-2026.devpost.com/rules), [unpublished gallery](https://forgehacks-2026.devpost.com/project-gallery), [JobScamScore](https://jobscamscore.com/), [FTC job-scam guidance](https://consumer.ftc.gov/articles/job-scams).

## Alternatives considered

| Route | Advantage | Failure mode under the deadline | Decision |
| --- | --- | --- | --- |
| Job offer risk score | Easy first demo | Already crowded; unreliable safe verdict; weak AI depth | Reject |
| General AI tutor for misconceptions | Fits education prompt | Established tutoring competitors; new domain and validation from scratch | Defer |
| Evidence source-chain investigation | Concrete anti-impersonation mechanic; extends working app | Self-reported provenance cannot authenticate a website; AI still narrow | Build and measure |

## What the prototype really does

1. AI extracts exact quoted claims from a message when configured; a deterministic filter rejects invented quotes and any verdict or link outside that schema.
2. Deterministic warning rules highlight a few known job-scam patterns, with disclosed misses and false positives.
3. The user logs source provenance, including whether a new observation depends on an earlier one. A dependency chain back to a message or AI suggestion is labeled **source collapse** and excluded from independently found observations.
4. Independent observations never authenticate a sender. The response path gives practical steps after password, money, or document exposure.

This is a focused consumer workflow, not an automated investigation, evidence verification service, domain reputation engine, or scientifically validated detector. Source descriptions are user-reported and can be wrong. A real listing can coexist with an impersonating recruiter.

## Gates before claiming impact or depth

- **Live AI:** demonstrate one actual model extraction using a server-side key. Record model, latency, fallback behavior, and failures. No key is present in this repository.
- **Holdout:** freeze a separate set of plausible scam and legitimate messages before tuning, including indirect pressure, recruiter impersonation with a genuine listing, and benign wording that mentions fees or passwords. Report misses, false alarms and abstentions; compare against a plain FTC checklist. Existing fictional smoke cases are not a holdout.
- **User task:** ask outside participants to handle the same fictional cases with a checklist and with this prototype in counterbalanced order. Measure whether they choose an independently found company channel and avoid trusting circular evidence. Do not claim observed improvement until it is measured.
- **Presentation:** show a plausible case that passes simple red-flag detection, then a source-collapse chain and the response workflow. Explain why AI is constrained and where it adds value. A successful screen recording and public demo link are still needed.

If the live model is unavailable, label the demonstration a rules-only prototype. If the holdout shows poor recall or users misunderstand source provenance, report that honestly and narrow the claim. The probability of winning is unknown; no published information supports certainty.
