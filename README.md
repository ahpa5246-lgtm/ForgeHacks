# OfferProof

**A claim-and-evidence integrity investigation workspace for ForgeHacks 2026 (AI + Cybersecurity).**

Students can paste a suspicious recruiting message. The app quotes claims from the message, marks common high-risk requests, records where a user's observations came from, and provides response steps if the student already shared a password, money, or documents. Every result stays **unverified**: a job listing does not authenticate a recruiter. Nothing in the message is fetched or visited.

## Google AI Studio / Gemini setup

OfferProof now supports Gemini through Google's documented OpenAI-compatible REST API. On the Render **Environment** page, add your AI Studio API key as **GEMINI_API_KEY** (recommended). For compatibility with the first setup screenshot, the lowercase name **google** is also supported. Do not put the key in the code, client-side JavaScript or any public screenshot. Save the configuration and redeploy.

The default model is `gemini-3.8-flash`. To use another model supported by your Google AI Studio project, set `GEMINI_MODEL`. When both Google and Groq are configured, Google is preferred; the existing Groq integration remains a fallback for installations with only Groq configured. The `/health` response exposes `ai_provider: gemini|groq|none` and `ai_configured`, but never the key; these fields indicate configuration, **not** whether model inference succeeds.

In **Inspect**, select a fictional message, tick the opt-in checkbox, and click Inspect claims. Only a displayed `AI extraction active` result confirms a successful inference attempt. In **Evidence Lab**, the cross-evidence comparison has separate consent. Both options send the relevant text to the configured provider and are off by default. Local rule checks and the provenance graph work without any AI credentials.

Provider error categories appear without secret keys or provider response bodies. If a model name is inaccessible, choose a model actually available to your account and redeploy. Google AI Studio quotas and data-handling terms vary by project/tier.

## Run locally

Python 3.10+; no Python packages or paid hosting required.

```bash
python offerproof.py
```

Visit `http://127.0.0.1:8000`. On Windows use `py offerproof.py`. To enable AI claim extraction, set `GEMINI_API_KEY` or `GROQ_API_KEY` in the process environment, start the server again, **and explicitly tick the Groq opt-in checkbox in Inspect**. Message inspection defaults to local-only rules even if the key is configured. The cross-evidence comparison has a separate consent checkbox. API clients must send `groq_consent: true` to request external processing; otherwise no message text is sent to Groq. Never put a key into the website, commit, message box, or demo recording. Optional `GROQ_MODEL` defaults to `qwen/qwen3.8-27b`. If no key is present or the model fails, the UI clearly labels the rules-only fallback. For a public demonstration, the server applies **best-effort in-memory AI request limits** (12 inspections/minute per socket IP and 120 inspections/hour globally). These reset on server restart and are not suitable as a distributed production abuse-control system. Groq usage is **not unlimited or necessarily free**: Groq enforces per-organization request and token limits, and usage may incur charges if your account is on a paid plan. Check your account's current Limits and billing pages before a public demo. For remote deployment, set `HOST=0.0.0.0` and `PORT` to the platform's assigned port; put the key in server-side environment settings only. Public deployment needs a durable rate limit and privacy review before inviting real users; local demo is the supported path.

The redesigned browser experience now has four sections: **Overview, Inspect a message, Evidence lab, and Response center**. The interactive dependency map explicitly highlights source collapse. It is a guided single-page application with local CSS and JavaScript assets (`dashboard.css`, `dashboard.js`), not four separately deployed sites.

The included `render.yaml` can create a Render Free web service from this repository. Connect the repository to a new Blueprint in Render, supply `GROQ_API_KEY` only in its environment-variable prompt, and verify `/health` reports `ai_configured: true`. This only confirms that a key is present; it does **not** test whether the key works, the model responds, or the account has remaining quota. Free services may spin down on idle and are subject to Render's current free-tier limits. Treat this public service as a controlled hackathon demonstration, not a production protection tool. Do not invite strangers to submit real personal messages without abuse controls and privacy review.

## Evidence Engine v2 — what materially changed

Open the homepage and choose **Run full evidence demo**. OfferProof analyzes a synthetic plausible recruiting message, then displays a four-note dependency graph. Two apparently corroborating notes trace to the original recruiter message, while a separately found contact remains *reported independent but not authenticated*. The graph is an actual directed acyclic graph with explicit edges and support for multiple source parents — not a sequential list styled as a graph.

- **Source-bound AI:** Groq, when configured, quotes up to five source claims and suggests up to three tentative caution cues. Fixed claim-category missions tell users what could verify each claim independently. No model-suggested links, authenticity labels, or freeform verdicts are accepted as evidence.
- **Structured provenance:** The server evaluates explicit parent dependencies and propagates untrusted sender/AI origins along all paths. The client renders the directed graph with SVG; manually reported origins remain self-reported.
- **Usable output:** The browser exports an investigation report with observed red flags, quoted claims, verification missions, source dependencies, and explicit uncertainty. It intentionally excludes the full pasted message.
- **False alarms:** Simple negation guards reduce obvious mistakes on phrases such as "we will never ask for a fee"; this is not general-language semantic comprehension.
- **Verification:** Unit tests, JS syntax checks and Chromium desktop/mobile E2E run in CI. Browser E2E uses the disclosed rules-only fallback; real Groq integration must be verified separately on Render.

**Limits:** OfferProof does not browse external URLs, authenticate websites, validate real employers, or verify the reported origins. A page found independently can still be counterfeit. No blinded efficacy study or outside-user comparison is claimed. Do not describe it as an autonomous fraud detective or calibrated scam score.

See [Judge quickstart](docs/judges-quickstart.md) for the 75-second showcase.

## Cinematic case narrative (presentation layer)

The landing page now presents a three-act fictional investigation — **The Approach**, **The Illusion**, and **The Reveal** — with animated CSS message cards, an evidence-origin illusion, cinematic chapter transitions, progress indicator, and a one-click bridge into the *real* deterministic source-provenance demo. The workspace retains the original Inspect, Evidence Lab, and Response Center flows and their API contracts. An actual SVG DAG animates source edges and nodes as the user builds the case.

The visual effects use local CSS and a small same-origin script (no remote image, animation or font dependencies). Motion-heavy effects are disabled by the user's reduced-motion accessibility preference. The page remains keyboard navigable with a skip link and labeled navigation controls. The 40+ unit checks and automated Chromium desktop/mobile scenarios remain the release gates.

**Presentation boundary:** The story is fictional. The animated cards and storyboard are illustrative, while the **Run full evidence demo** button operates on the actual analysis and graph APIs. This redesign does not claim new fraud-detection accuracy or solve the still-outstanding live Groq HTTP 403 access issue.

## Offline sender-link discovery (v5)

When the message contains HTTP(S) links, OfferProof extracts up to three distinct **hostnames** without browsing them or making DNS requests. It automatically records these as non-independent, message-derived source leads in the Evidence Lab. Full URLs, paths, credentials and query strings are not copied into the graph or report. Even a familiar hostname is **not evidence of authenticity**; the feature records only what the untrusted sender supplied. Users still report any subsequently discovered evidence and its dependencies.

## AI-assisted cross-evidence challenge (v3)

The Evidence Lab now includes **Challenge the evidence** after a message inspection and at least one user-reported source. With explicit browser consent, the message and observation texts are sent to Groq for a constrained *cross-evidence comparison*. The model must return **two exact original substrings** (one from the message, one from an observation) and one of a small allowlist of discrepancy types. The server rejects invented quotes, unrecognized categories and model-generated addresses or verdicts, and annotates each hypothesis with the provenance engine's actual source classification. **An AI comparison never authenticates a source or establishes which claim is correct.** When the provider is not configured or fails, the interface clearly states that no semantic comparison occurred. The endpoint shares the in-memory public-demo rate limit with message inspection.

If recording a demo, enable this feature only with fictional messages/observations and show its AI/fallback label honestly; the model may return no discrepancies. See the judge walkthrough.

## Demo in three cases

1. **Payment request:** select the first example. A red flag appears, with no safe/verified label.
2. **Plausible interview:** select the second. No flag is found, yet the result remains unverified.
3. **Identity request:** select the third. The app says to stop sending sensitive documents.
4. **Evidence provenance:** log a search result found through the message, then a careers page that came through that search result. Even if the second page is labeled “found independently,” its recorded dependency reveals a source collapse. Finally log a separately found channel. None authenticate the sender.
5. **Response:** select “I shared a password” and display password reset and multi-factor authentication steps.

If AI is configured, `AI quoted claims from the message` appears. Each quote is accepted only if it occurs verbatim in the pasted text. Any AI-generated URL or verdict is discarded. The heuristic warning list is deterministic and limited; it cannot detect every scam, and negated phrases or unusual wording can still create false alarms or missed signals.

## Architecture

`Browser message → local Python HTTP server → bounded AI claim extraction (optional) → verbatim-quote filter + deterministic warning rules → unverified result`. The source-provenance ledger and response endpoint are separate deterministic paths.

The AI is used for exact quoted claim extraction and tentative, source-bound caution signals, not for a risk score or a legitimacy verdict. AI cautions are limited to a predefined set of non-authoritative explanations; invented snippets and untrusted model prose are dropped. A warning rule can escalate the status to `red_flag_observed`; no rule or model can set `verified=true`. A directed dependency chain excludes observations derived from the original message or an AI suggestion, even when a later observation is labeled independent. Evidence observations and dependency labels are user reports; the service does not independently verify the claims or URLs. Notes remain in the tab only; no message or note is persisted by the server. External AI processing sends the message to Groq when the key is configured, so fictional messages are preferable for the demo. Do not paste sensitive personal data.

## Testing and evidence

Run `python -m unittest discover -s tests -v`. CI also executes `node --check dashboard.js` and a Playwright Chromium user-flow smoke test, capturing desktop and mobile screenshots. The included 12 fictional cases are a **development smoke set**; the warning rules were refined after seeing these cases, so scores on them are not blinded evidence of superiority over FTC advice. A valid impact claim would require a separate frozen holdout set, a randomized checklist comparison, and independent usability sessions. None have been completed. See `docs/research/2026-10-05-research-revision.json` for the research gates.

Strategic assessment: this is a relevant cybersecurity prototype, but its current AI component is narrow and its impact and novelty have not been established against comparable tools. There is no credible basis for a winning claim. The next strongest evidence would be a live provider demonstration, outside-user task completion, and an independent holdout comparison, with failures reported as well as successes.
See [strategy decision](docs/strategy-decision-2026-10-08.md) for alternatives, a named competitor, and evidence gates.

## Hackathon presentation

Show a 2–4 minute screen recording: first the problem, then the three cases, then one live AI extraction with the configured server (without exposing the key), then the independent verification boundary and limitations. Present the result as an educational prototype, not a deployed scam detector. See `docs/demo-script.md`.

References: [ForgeHacks prompt](https://forgehacks.vercel.app/) · [ForgeHacks submission](https://forgehacks-2026.devpost.com/) · [FTC job scam advice](https://consumer.ftc.gov/articles/job-scams).

Groq references: [supported model and JSON mode](https://console.groq.com/docs/model/qwen/qwen3.8-27b) · [rate limits](https://console.groq.com/docs/rate-limits). The published free-plan table currently lists `qwen/qwen3.8-27b` at 30 requests/minute, 1,000 requests/day, 8,000 tokens/minute and 200,000 tokens/day; the exact limits for your organization are shown in your Groq account. When a provider request fails or is rate-limited, extraction falls back to rules only. More calls by themselves do not improve accuracy or hackathon judging.

Substantial application code and interface were written during the October 3–10 hackathon; the older repository contained only pre-event research. Open-source project, no affiliation with FTC or any employer.
