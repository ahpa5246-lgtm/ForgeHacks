# OfferProof

**A narrow, honest job-offer verification assistant for ForgeHacks 2026 (AI + Cybersecurity).**

Students can paste a suspicious recruiting message. The app quotes claims from the message, marks common high-risk requests, and guides the student to check an employer through a channel they selected independently. Every result stays **unverified**: a job listing does not authenticate a recruiter. Nothing in the message is fetched or visited.

## Run locally

Python 3.10+; no Python packages or paid hosting required.

```bash
python offerproof.py
```

Visit `http://127.0.0.1:8000`. On Windows use `py offerproof.py`. To enable AI claim extraction, set `GROQ_API_KEY` in the process environment and start the server again. Never put a key into the website, commit, message box, or demo recording. A free-tier key's availability and limits depend on the provider. Optional `GROQ_MODEL` defaults to `qwen/qwen3.8-27b`. If no key is present or the model fails, the UI clearly labels the rules-only fallback. `MAX_AI_CALLS` defaults to 30 calls per running process before falling back; this cap resets on restart and is not a production abuse defense. For remote deployment, set `HOST=0.0.0.0` and `PORT` to the platform's assigned port; put the key in server-side environment settings only. Public deployment needs a durable rate limit and privacy review before inviting real users; local demo is the supported path.

The included `render.yaml` can create a Render Free web service from this repository. Connect the repository to a new Blueprint in Render, supply `GROQ_API_KEY` only in its environment-variable prompt, and verify `/health` reports `ai_configured: true`. Free services may spin down on idle and are subject to Render's current free-tier limits. Treat this public service as a controlled hackathon demonstration, not a production protection tool. Do not invite strangers to submit real personal messages without abuse controls and privacy review.

## Demo in three cases

1. **Payment request:** select the first example. A red flag appears, with no safe/verified label.
2. **Plausible interview:** select the second. No flag is found, yet the result remains unverified.
3. **Identity request:** select the third. The app says to stop sending sensitive documents.

If AI is configured, `AI quoted claims from the message` appears. Each quote is accepted only if it occurs verbatim in the pasted text. Any AI-generated URL or verdict is discarded. The heuristic warning list is deterministic and limited; it cannot detect every scam, and negated phrases or unusual wording can still create false alarms or missed signals.

## Architecture

`Browser textarea → local Python HTTP server → bounded AI claim extraction (optional) → verbatim-quote filter + deterministic warning rules → unverified result`.

The AI is used for claim extraction, not for a risk score or a legitimacy verdict. A warning rule can escalate the status to `red_flag_observed`; no rule or model can set `verified=true`. A user note remains in the tab only; no message or note is persisted by the server. External AI processing sends the message to Groq when the key is configured, so fictional messages are preferable for the demo. Do not paste sensitive personal data.

## Testing and evidence

Run `python -m unittest discover -s tests -v`. The included 12 fictional cases are a **development smoke set**; the warning rules were refined after seeing these cases, so scores on them are not blinded evidence of superiority over FTC advice. A valid impact claim would require a separate frozen holdout set, a randomized checklist comparison, and independent usability sessions. None have been completed. See `docs/research/2026-10-05-research-revision.json` for the research gates.

## Hackathon presentation

Show a 2–4 minute screen recording: first the problem, then the three cases, then one live AI extraction with the configured server (without exposing the key), then the independent verification boundary and limitations. Present the result as an educational prototype, not a deployed scam detector. See `docs/demo-script.md`.

References: [ForgeHacks prompt](https://forgehacks.vercel.app/) · [ForgeHacks submission](https://forgehacks-2026.devpost.com/) · [FTC job scam advice](https://consumer.ftc.gov/articles/job-scams).

Substantial application code and interface were written during the October 3–10 hackathon; the older repository contained only pre-event research. Open-source project, no affiliation with FTC or any employer.
