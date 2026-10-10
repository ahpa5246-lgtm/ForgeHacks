# OfferProof — 75-second judge walkthrough (ForgeHacks 2026)

**Problem:** A real-looking job listing can falsely reassure a candidate if the apparent supporting page or search result ultimately comes from the same unverified recruiter. Traditional surface keyword checks don't expose the source dependency.

**Claim:** OfferProof helps a person *trace and question evidence origins*. It does **not** authenticate a recruiter, website or company, and the example is entirely fictional.

## Live screen-recording sequence

| Time | Action | On-screen result |
|---|---|---|
| 0–10 s | Home screen: one sentence on circular evidence | How one sender can make a claim look independently corroborated |
| 10–15 s | Click **Run full evidence demo** | Synthetic plausible message is analyzed (AI label clearly visible in Inspect view) |
| 15–40 s | In Evidence Lab, focus on the genuine SVG arrows and the red collapse nodes | A polished careers page arrived via recruiter's link; a blended later summary inherits the same tainted origin |
| 40–53 s | Point to independently found channel | Separately found but still *self-reported and unauthenticated* |
| 53–62 s | Click **Export investigation report** | The browser generates a local report with exact source dependencies and missing proof; original message text is excluded |
| 62–75 s | Visit Inspect and show claim-specific verification missions | AI quotes claims; fixed missions ask how to independently verify them. No fake safety score |

## Distinguishing responsibilities

1. **AI** (only if active): bounded exact claim extraction and tentative context cues; never the trust authority.
2. **Deterministic graph engine:** computes reachability from untrusted sender/AI roots, including multi-parent dependencies.
3. **User:** supplies how a source was found; still must contact a legitimate company channel themselves.
4. **Product:** produces an auditable, clearly limited investigation record.

## Demo quality gates

- Show browser on public Render URL, not a stale screenshot.
- In the Inspect view, state exactly whether the mode reads AI extraction or Rules-only fallback.
- Demonstrate at least one non-keyword case that generates source collapse.
- Never claim that a careers page authenticates a specific recruiter.
- Keep the demo synthetic; never display the Groq key, real person's information or private messages.
- A public deployment, Devpost submission and externally verified impact measurements are separate deliverables. Do not claim them unless actually completed.

## Honest one-line pitch

"OfferProof doesn't tell you whether a stranger is trustworthy. It shows when the evidence that persuaded you to trust them all comes from that same stranger."
