# ForgeHacks adversarial review — 8 October 2026

## Verdict

**Do not describe OfferProof as ready to win or fully agent-reviewed.** The eight roles are defined in Programmed Minds, but the published ForgeHacks trail contains a `research_critic` verdict of `revise` and a research revision marked `blocked_pending_evidence`. There are no published improvement-critic, plan-critic, designer or post-build tester reports in this repository. A local Windows run may exist, but it is not visible here and cannot be counted. Building OfferProof before resolving the research gate broke our own workflow.

## What previous winners shipped

These are winners of **GenAI Genesis 2026**, a different hackathon. Their Devpost pages verify award labels and contain the teams' own descriptions of their systems; the technical and impact details are self-reported, not independently audited. They are comparisons, not a recipe that guarantees a ForgeHacks prize.

| Winner | Award and reported working system | Gap in OfferProof |
| --- | --- | --- |
| [OmenAI](https://devpost.com/software/omenai) | TD financial-fraud category. Ingested live trade data, deduplicated it, scored multiple signals, enriched suspicious wallets, ran Isolation Forest, streamed a dashboard, and explained findings. | We ingest only one pasted message. No external corroboration, trained model, calibrated evaluation, or live data. |
| [Eco-Pulse](https://devpost.com/software/eco-pulse-fpbo15) | Online top team. Combined geospatial heat/canopy/population inputs, clustering, map and street imagery, AI-generated intervention visuals, and estimated intervention effects. | Our AI only quotes text. The central provenance graph depends entirely on the user's own declarations; it does not collect or test sources. |
| [Q Labs](https://devpost.com/software/q-labs) | Sponsored QA category. Provisioned a sandbox from a Docker image, used an agent to inspect the DOM and click flows, captured failures and retested changed states. | Our 18 unit tests are internal behavior tests. No end-to-end browser run or actual user outcome has been recorded. |

## Specific failure modes

1. **AI judging weakness — critical.** Without a Groq key, the product is a rules-and-form workflow. With one, AI performs bounded substring extraction; the important source-collapse logic is deterministic and requires manual user entry. This can be judged as an AI wrapper, regardless of how many calls are permitted.
2. **Competitive weakness — critical.** [JobScamScore](https://jobscamscore.com/) already advertises text/URL/screenshot ingestion, multiple source checks, risk signals and actionable advice. Its claims are marketing until verified, but our visible feature set is narrower. A judge comparing screenshots may see a weaker checker. Our distinct promise must be explicitly the prevention of circular evidence, demonstrated on a case a conventional score gets wrong.
3. **Unfinished validation — critical.** The Groq critic requested a comparison with a static FTC checklist, at least two outside usability sessions, and live AI extraction. The current research revision marks these gates `not_run`. The twelve fictional scenarios are development smoke inputs, not independent evidence of safety or improvement.
4. **Source-authenticity illusion — high.** The UI lets users mark a source as independent. The graph detects only dependencies the user reports. A spoofed site typed independently could still mislead; no sender is authenticated. Keep this limitation prominent in the demo.
5. **Demonstration weakness — high.** A video outline exists, but there is no published app URL, recording, or verified end-to-end browser run. A Render blueprint and `ai_configured: true` do not demonstrate that the model answered successfully.
6. **Workflow honesty — high.** Programmed Minds' eight role definitions exist, yet their full sequence was not executed against this candidate in the published trail. We should not call the project eight-agent-approved.
7. **Unbounded calls do not add depth — medium.** The removed local 30-call cap only avoids an arbitrary demo cutoff. Groq's own free-plan quotas still apply; frequency is not a judging criterion.

## Highest-value repairs before 10 October, 12:00 EDT

1. **Real AI evidence:** configure the server-side key, run the fixed twelve cases through the actual model, publish aggregate schema-validity, omissions, latency and fallback counts without private data. If this fails, stop calling AI use demonstrated.
2. **Show the mechanism:** prepare a three-step fictional impersonation case where a plausible message has no obvious keyword flag, a careers page appears to corroborate it, and provenance reveals the page was reached through the recruiter's suggestion. A judge must see the source collapse and the still-unverified state within one minute. This is the claim we can demonstrate now, not automatic scam detection.
3. **Outside comparison:** run at least two people on a static FTC checklist and OfferProof in varied order, ask their next action without coaching, and record failures. Do not claim measured prevention from builder-authored fixtures alone.
4. **Complete the chain:** revise research; obtain an outside research critic decision; produce improvement and plan artifacts with their distinct critics, then a real user-flow test. If a critic remains blocked, label that status.
5. **Ship the presentation:** working public demo or reliable local launch, screen recording, concise Devpost write-up, README with exact limitations and post-start commit history. Confirm the published contest deadline in Devpost shortly before submission.

## Decision rule

Continue the current scope only if the live AI path works, the source-collapse demonstration is understandable without narration, and at least two outside users choose a safer next action without interpreting `unverified` as safe. Otherwise present this honestly as a prototype or narrow the claim. No outcome here establishes a probability of winning.

Sources: [ForgeHacks track prompts](https://forgehacks.vercel.app/), [ForgeHacks rules](https://forgehacks-2026.devpost.com/rules), [OmenAI](https://devpost.com/software/omenai), [Eco-Pulse](https://devpost.com/software/eco-pulse-fpbo15), [Q Labs](https://devpost.com/software/q-labs), [JobScamScore](https://jobscamscore.com/), [Programmed Minds role instructions](https://github.com/ahpa5246-lgtm/Programmed-Minds/blob/main/docs/codex-roles.md), [current research critic](research/2026-10-05-research-critic.json), [research revision](research/2026-10-05-research-revision.json).
