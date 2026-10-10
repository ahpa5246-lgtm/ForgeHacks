# Devpost submission draft — OfferProof (ForgeHacks 2026)

## Project tagline

**Don't just check a job offer. Trace where the evidence came from.**

## The problem

A convincing message can claim to be from a real employer, cite a real job listing, and link to a polished-looking website. Even when someone sees what appears to be corroborating evidence, the "independent" source might have been found only through the original recruiter's message. The evidence all leads back to the same unverified actor.

Most simple job-scam checklists focus on individual warning signs such as upfront payments or password requests. These matter, but a seemingly normal internship invitation can avoid obvious words while borrowing the appearance of credibility.

## What we built

**OfferProof** is a guided evidence-integrity investigation prototype. Users can inspect the claims within a recruiting message, investigate where supporting observations originated, and produce a small evidence report without pretending they know a sender's identity.

It includes:
- **Bounded AI inspection:** Groq extracts exact message excerpts and tentative contextual caution signals. Server-side filtering drops invented excerpts and model-supplied contacts or verdicts.
- **Claim verification missions:** Each extracted claim maps to a concrete question the user could check through independently found employer channels.
- **Evidence Engine:** The user records observation origins and dependency relationships. A real directed graph propagates dependencies through multiple parent notes and highlights *source collapse*: a purportedly independent item that ultimately descends from the original message or AI output.
- **Cross-evidence AI review:** With explicit consent, Groq can suggest textually grounded discrepancies between message excerpts and reported observations. Each hypothesis includes two exact quotes, its note's provenance classification, and an uncertainty label.
- **Response center:** A separate workflow provides first-response guidance if the person already shared a login code, made a payment, or supplied documents.
- **Portable report:** Export a plain-text investigation report with quotes, source relations, remaining questions and disclosures. The original pasted message is not copied into the report.

## Why our approach is different

OfferProof is **not** another opaque "75% scam probability" widget. Its purpose is to show why a piece of purported evidence may fail to provide independent corroboration. The analysis is transparent enough to discuss: an edge from the recruiter's link to an apparent careers page shows that both may still come from the same untrusted origin.

**Crucial boundary:** Our source relationships are reported by the user, and we do not browse or authenticate websites, people, organizations, or emails. A note marked "independent" can still describe a counterfeit site. The tool never tells someone that an offer is genuine.

## How we built it

Python 3 standard-library HTTP server; JavaScript and CSS without UI framework dependencies; custom SVG directed-graph renderer; Groq chat-completions API with JSON-object structured outputs; exact-quote checks and deterministic provenance propagation; GitHub Actions with unit tests, Node syntax checking and Playwright Chromium desktop/mobile workflows. Render deployment configuration is included.

AI contributes contextual candidate claims and contrasts. Deterministic code owns the safety-critical rules: source tracing, allowed label vocabulary and the invariant that sender authenticity is never established.

## Challenges

The hardest design problem is epistemic trust: an AI that confidently assigns an authenticity score could mislead the very person the tool is supposed to protect. We addressed this by rejecting unsupported model claims and keeping AI suggestions clearly separate from self-reported source origins. We also had to distinguish the *reported* independence of a source from proof that the actual source is genuine.

A second challenge was demonstrating a non-keyword impersonation risk within a short, inspectable demo. Our synthetic one-click walkthrough starts with a plausible recruiting message and a dependency graph containing apparently corroborating notes that trace back to the same unverified source.

## What we tested

The repository includes automated unit regression checks for known-rule matches and simple negations, quote validation, forged AI outputs, directed multi-parent source-collapses, endpoint behavior, rate-limit behavior, static asset isolation and recovery guidance. GitHub Actions additionally runs Chromium desktop/mobile journeys with real SVG path checks, synthetic evidence demonstration, consent/fallback behavior and report download. Screenshots are available as CI artifacts.

**Limits:** These are engineering tests and builder-authored demonstrations — not an independent, blinded efficacy study. We have no verified evidence that OfferProof reduces successful scams compared with conventional advice, and do not claim so. A public deployment and live Groq response require separate verification on Render.

## What we learned

Credibility isn't a property of how persuasive an explanation looks; it depends on how independently its supporting evidence was obtained. Explicitly preserving uncertainty is essential in cybersecurity UX.

## What's next

Independent two-user usability comparisons; a frozen, external holdout set with benign and malicious examples; opt-in privacy review and production-grade abuse controls; more accessible graph layouts; and integrations that can check domain ownership and company identity without following unsolicited links.

## Built with

Python, JavaScript, HTML, CSS, SVG, Groq API, GitHub Actions, Playwright, Render configuration.

## Links to fill in before submission

- **Source code:** https://github.com/ahpa5246-lgtm/ForgeHacks
- **Live demo:** INSERT VERIFIED RENDER LINK
- **Demo video:** INSERT VIDEO LINK
- **Tests:** https://github.com/ahpa5246-lgtm/ForgeHacks/actions
