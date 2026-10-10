# OfferProof — final demo storyboard (2:20, fictional data)

**Recording setup:** Public deployed URL only after checking /health and the AI mode in the Inspect view. Full HD desktop capture, browser zoom about 100%, hide account tabs, credentials and any private data. Do not show an unverified live Groq path as verified. If provider is unavailable, use the same synthetic case and label the rules fallback honestly.

| Time | Visual on screen | Narration (English) |
|---|---|---|
| 0:00–0:13 | Homepage hero and three overview claims | "A convincing job offer can have convincing evidence. But what if all of that evidence traces back to the person who sent the offer?" |
| 0:13–0:31 | Click **Run full evidence demo** | "OfferProof starts by inspecting a fictional recruiting message. It extracts the actual claims and separates plain warning rules from bounded AI suggestions. No safety verdict is generated." |
| 0:31–0:57 | Evidence Lab graph, linger on recruiter source and first red node | "Now we trace a careers page that looked like corroboration. The graph shows it was reached through the recruiter's own link. That is source collapse: not independent evidence." |
| 0:57–1:14 | Move to separate green node and red mixed-dependency node | "The separately found channel remains only user-reported. A later summary that depends on both sources inherits the untrusted chain. None of this authenticates the sender." |
| 1:14–1:38 | Show **Challenge the evidence**, tick external-AI consent. Click button only if actual Groq works | "With explicit consent, the AI can compare the message against observation notes and propose quote-grounded discrepancies. We reject invented excerpts and label every finding as a hypothesis; the source graph remains the trust boundary." |
| 1:38–1:53 | Click Export investigation report | "The result is a portable record of claim quotes, their supporting dependencies and what still needs checking. It does not export the entire pasted message." |
| 1:53–2:08 | Move to Inspect claim verification missions | "OfferProof tells the user what independent checks to perform next. Even a real job listing cannot prove who sent a message." |
| 2:08–2:20 | Show response center, Github tests if time | "We tested the flows on desktop and mobile using Chromium and constrained the AI output. OfferProof is a prototype, not a certified detector. Our focus is a safer, more transparent decision." |

## Pre-recording gate

1. Check service is Live and new frontend files deploy: /dashboard.js, /source_graph.js, /health.
2. Open fictional Plausible offer, inspect, confirm actual mode (AI or rules fallback). A key presence alone does not prove AI works.
3. Load the full demo and make sure two red Source Collapse notes and one reported-independent note appear.
4. Check comparison only after consenting; if AI is unavailable, **do not fake the result or say it ran**.
5. Download the report once to confirm the browser gives a text file without raw private message.
6. Record real browser behavior, not static screenshots.
7. Submit source repository, actual live link if available, video and Devpost description **before deadline**.

## Hero statement for judges

**"We don't ask AI to decide whether a stranger is trustworthy. We help people see when the evidence that convinced them all came from that same stranger."**
