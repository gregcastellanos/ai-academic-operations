# Customer Success AI Workflow Simulation

A runnable, single-command simulation of an AI-assisted B2B SaaS customer success operation. Built for the Crossover AI System Design Assessment. It is a workflow simulation, not production software — the point is to show the reasoning and routing logic an AI system would need, with token/cost math that transfers directly into the Token Math Sheet.

## Setup

No dependencies beyond Python 3 standard library.

```bash
cd cs_workflow_simulation
python3 workflow.py
```

## What it does

Loads the 7 input CSVs in `data/` and runs them through 8 workflow stages, end to end, for the full 18-account portfolio. Writes results to `outputs/`.

## Scale: 18-account demo vs. 750-account production scope

This simulation runs against a fixed 18-account dataset so the assessment run is small, deterministic, and reviewable line by line. The actual assignment scope is a **750-account production portfolio** with ~30 inbound support tickets/week and ~12 scheduled check-ins/week, with targeted interventions reviewed roughly every two weeks for Urgent/Watch/Expansion accounts and account monitoring running every business day.

The 18-account run is never used directly as the production estimate. It is used only to **measure real per-run token/cost footprints** for each stage (`outputs/token_cost_summary.csv`), which are then scaled by volume ratio and annualized by cadence factor to the 750-account scope in the Token Math Sheet (`outputs/Token_Math_Sheet_Completed.xlsx`). That sheet's `Candidate Assumptions` tab labels every figure as **Measured** (straight from this simulation), **Scaled estimate** (measured value × a documented production-volume ratio), or **Assumption** (not measured or derived, e.g. retry/QA multipliers) — so production-scope conclusions are traceable back to either a measured number or an explicitly stated assumption, never blended silently.

## 24/7 responsiveness

The escalation stage (stage 7, `escalation_followup_routing`) is modeled as event-driven rather than cadence-batched: it runs continuously against whatever stages 3 and 5 have flagged, instead of waiting for the next business-day or weekly batch. In the Token Math Sheet this is reflected as the "24/7 responsiveness / escalation" operating area, priced on Claude Opus 4.7 (highest stakes, lowest volume) and annualized on a business-day-equivalent escalation-event cadence rather than a fixed daily/weekly run count, since escalation-worthy events don't arrive on a schedule.

## Workflow stages

0. **Memory & context retrieval** (`memory_context_retrieval`) — runs first, before any other stage. For every account, pulls account profile, call history, open support tickets, the latest usage event, and the next scheduled check-in into one concise memory packet. This is the retrieval step a production RAG pipeline would do via vector search over a much larger corpus; with this small fixed dataset, a direct per-account lookup produces the same result without the added machinery. Stage 4 (check-in preparation) consumes this stage's output directly rather than re-deriving context from scratch.
1. **Daily account review** (`daily_account_review`) — pulls the latest usage event, health-score delta, ticket count, and NPS for every account into one reviewable record. High-volume, low-judgment — this is the stage that runs every business day across the whole book.
2. **Account prioritization** (`account_prioritization`) — scores each account on a transparent `risk_score` (health decline, usage trend, ticket volume, NPS) and `opportunity_score` (expansion signal, high health/NPS), then assigns a tier: **Urgent** / **Watch** / **Expansion** / **Stable**. The score formula is in the code, not a black box — anyone reviewing this can recompute it by hand.
3. **Inbound support issue routing** (`route_ticket`) — every ticket gets a route: `escalation`, `standard_resolution`, or `immediate_resolution`. High severity always escalates. Medium severity escalates only on Urgent/Watch accounts (risk compounding). Low severity resolves immediately unless sentiment is negative.
4. **Customer check-in preparation** (`customer_checkin_preparation`) — for each scheduled check-in, builds a brief around the retrieved memory packet from stage 0, plus next-step actions derived from outstanding follow-up items and any open tickets — so the CSM walks in with full context instead of re-discovering it live.
5. **Customer-facing output quality review** (`output_quality_review`) — checks each junior-drafted output against the specific quality standards (QS001–QS006) it was tagged with. This stage uses deterministic heuristics (keyword overlap, action-word detection, risk-language proportionality) rather than an actual LLM call — see "What's heuristic vs. what would be a real model call" below.
6. **Targeted intervention planning** (`targeted_intervention_planning`) — for every Urgent/Watch/Expansion account, generates a recommended action, owner, due window, and rationale tied to the specific risk/opportunity signals found.
7. **Escalation / follow-up / immediate-resolution routing** (`escalation_followup_routing`) — the final consolidation pass: every routed ticket and every reviewed output lands in exactly one bucket (`escalation`, `follow_up`, or `immediate_resolution`), so nothing produced by stages 3 or 5 is left unresolved.

## Output files (`outputs/`)

- **`memory_context_retrieval.csv`** — one memory packet per account: open ticket count, last call date/follow-up, usage trend, next check-in date, and the assembled `memory_packet` text consumed by stage 4.
- **`account_prioritization.csv`** — all 18 accounts, ranked, with risk/opportunity scores and tier.
- **`issue_routing.csv`** — every support ticket with its route and the reason for that route.
- **`checkin_briefs.md`** — one brief per scheduled check-in, human-readable.
- **`quality_review.csv`** — every junior output, which standards passed/failed, and the resulting recommendation (Approve / Revise / Escalate to senior CSM review).
- **`intervention_plan.md`** — recommended action per Urgent/Watch/Expansion account, grouped by tier.
- **`run_summary.json`** — aggregate counts, the evaluation check results, and 5 fully expanded end-to-end account runs (every stage's output for one account, including its memory packet, in one place) for accounts A008, A005, A014, A010, A017 — chosen because they have data in every input file.
- **`evaluation_failures.json`** — written every run; contains one entry per failed evaluation check (check name, detail, recommended remediation route). Empty on the current dataset since all four checks pass. See "Failure handling" below.
- **`token_cost_summary.csv`** — per-stage token/cost rollup. Columns are named to map directly onto the Token Math Sheet's "Token Math Template" tab (`workflow_component`, `operating_area`, `model`, input/output $ per 1M, tokens per run). The `notebook_measured_avg_cost_per_run` column is what you transfer into that sheet's "Notebook measured avg cost/run" field for the estimate-vs-measured variance check.

## Evaluation checks

Run automatically at the end of every execution and printed to console plus written into `run_summary.json`:

- Every Urgent-tier account has a recommended action in the intervention plan.
- Every high-severity ticket routes to `escalation` or `immediate_resolution` (never sits in a standard queue).
- Every check-in brief contains both prior context and next steps.
- Every junior output is checked against all of its tagged quality standards (none silently skipped).

All four pass on the current dataset (verified by running `workflow.py`).

## Model routing and why

| Stage | Model | Why |
|---|---|---|
| Memory & retrieval | text-embedding-3-small | The Pricing Reference tab calls this model out specifically for "memory/retrieval indexing, RAG embeddings." It has input-token cost only (no generation), matching what this stage actually does: assemble and (in a real RAG build) index context, not draft prose. |
| Account monitoring | Claude Haiku 4.5 | Highest volume (runs daily across the full portfolio), lowest judgment — pure data assembly. |
| Prioritization | Claude Haiku 4.5 | Same volume profile; scoring logic is rules-based, not reasoning-heavy. |
| Inbound issue handling | Claude Sonnet 4.6 | Needs judgment to weigh severity against account context, not just a lookup table. |
| Customer check-in support | Claude Sonnet 4.6 | Synthesizing call history + tickets + goals into a coherent brief benefits from a stronger model. |
| Output quality review | GPT-5.4 mini | Rubric-based evaluation against named standards — strong enough for structured judging, cheaper than a frontier model, and demonstrates routing across providers rather than defaulting to one. |
| Targeted intervention planning | Claude Sonnet 4.6 | Multi-signal reasoning (risk score + call notes + open tickets) per account, but bounded to Urgent/Watch/Expansion accounts only, so volume is naturally low. |
| Escalation / 24-7 responsiveness | Claude Opus 4.7 | Highest stakes, lowest volume stage — reserved for the final consolidation of anything already flagged as escalation-worthy. |

This mirrors the assessment's stated principle: cheap models for high-volume/simple work, stronger models only where the reasoning is actually hard.

## What's heuristic vs. what would be a real model call

This simulation does not call any LLM API — it estimates token/cost footprint and implements the *decision logic* an LLM-backed system would need, in plain Python, so it's auditable line by line and gives the same output on every run. In a real build:

- Stages 0–4 and 7 are good candidates to stay mostly rules-based even in production, with a cheap embedding/retrieval model (stage 0) and a cheap generation model only for any free-text summarization.
- Stage 5 (quality review) and stage 6 (intervention planning) are where an actual LLM call earns its cost — judging tone, risk-proportionality, and drafting a tailored recommendation are not reliably rule-based. The heuristics here (`ACTION_WORDS`, `OVERSTATE_WORDS`, keyword overlap) are a deliberately simple stand-in for what an LLM-as-judge would do against the same `quality_standards.csv` rubric.

### Prompt templates (`prompts/`)

The code stays deterministic intentionally — it needs to produce the same result on every run for this assessment to be reviewable and re-runnable. The `prompts/` folder is where the production-equivalent LLM prompts live instead of in the code: one markdown file per workflow stage, each documenting the model assigned to that stage, the prompt template a live system would send, and the output shape that matches what the deterministic code already produces. Swapping the simulation's rule-based logic for these prompts (one stage at a time, against a real model) is the natural next step beyond this assessment's scope — the templates are written so that substitution is direct.

| Stage | Prompt template |
|---|---|
| Memory & retrieval | `prompts/memory_retrieval_prompt.md` |
| Account monitoring | `prompts/account_monitoring_prompt.md` |
| Prioritization | `prompts/prioritization_prompt.md` |
| Inbound issue handling | `prompts/inbound_issue_routing_prompt.md` |
| Customer check-in support | `prompts/checkin_preparation_prompt.md` |
| Output quality review | `prompts/output_quality_review_prompt.md` |
| Targeted intervention planning | `prompts/intervention_planning_prompt.md` |
| 24/7 responsiveness / escalation | `prompts/escalation_prompt.md` |
| Evaluation / QA (sampled review) | `prompts/evaluation_qa_prompt.md` |

## Failure handling

The four automated evaluation checks (below) all pass on the current dataset. If any check ever fails, `main()` writes the failure(s) to `outputs/evaluation_failures.json` instead of only printing to console, with one entry per failed check containing the check name, the specific item(s) that failed it, and a recommended remediation route:

| Failed check | Recommended remediation route |
|---|---|
| Urgent account missing an intervention action | Route to CSM Manager queue for manual intervention plan within 1 business day |
| High-severity ticket not escalated/resolved | Route to immediate escalation queue — treat as a routing-logic defect, not just a one-off miss |
| Check-in brief missing context or next steps | Route back to Customer check-in support stage for regeneration before the scheduled check-in |
| Junior output not checked against a tagged standard | Route to Output quality review stage for a full re-check before Approve/Revise/Escalate is finalized |

If no checks fail, `evaluation_failures.json` is not written (or is written empty) — its presence/absence is itself a signal of run health, separate from the human-readable PASS/FAIL summary already in `run_summary.json`.

## Assumptions

- Token estimates use the standard rule-of-thumb `tokens ≈ characters / 4` against the actual JSON-serialized input/output for each simulated call — this is the same heuristic most teams use for back-of-envelope estimation before measuring real usage.
- Pricing constants mirror the Token Math Sheet's Pricing Reference tab (effective 2026-05-17): Claude Haiku 4.5 ($1/$5 per 1M), Claude Sonnet 4.6 ($3/$15), Claude Opus 4.7 ($5/$25), GPT-5.4 mini ($0.75/$4.50), text-embedding-3-small ($0.02 input / $0.00 output, per the sheet's note that embedding models have input-only cost).
- The 5 "representative end-to-end" accounts (A008, A005, A014, A010, A017) were chosen because they're the only accounts with rows in every single input file — call notes, a junior output, a support ticket, a scheduled check-in, and usage events — so picking them demonstrates every stage working on the same account rather than stitching together partial coverage.
- Risk/opportunity scoring weights (e.g. `usage_trend_weight * 6`, `risk_score >= 30` for Urgent) are illustrative and documented in code; in a real deployment these would be calibrated against actual churn/renewal outcomes, not picked once and left alone.
- Quality-review heuristics are intentionally simple keyword/structure checks, not semantic understanding — they're meant to demonstrate the *shape* of automated rubric scoring, not to be production-accurate.
- Health score, ticket volume, product usage, NPS, and engagement are leading indicators, not the outcome itself — the real outcomes are retention, expansion, customer satisfaction, and long-term account health. This workflow uses the leading indicators to prioritize staff attention early, before those signals show up in renewal or churn numbers. Because they're a proxy, the thresholds and scoring rules behind them aren't set-and-forget: they should be reviewed quarterly against actual account outcomes and staff feedback, and recalibrated using human overrides and outcome data so the system improves over time instead of drifting from what it's actually trying to predict.

## How token and cost estimates are calculated

For every simulated call, the script logs the JSON-serialized input payload and the JSON-serialized output, converts each to a token estimate (`len(text) // 4`), and prices it using that stage's assigned model:

```
cost = (input_tokens / 1,000,000) * input_price_per_1M + (output_tokens / 1,000,000) * output_price_per_1M
```

`token_cost_summary.csv` aggregates this per stage across all runs in this single execution (18 accounts, 12 tickets, 12 check-ins, 8 junior outputs). To project an annual figure for the Token Math Sheet, multiply each stage's `avg_input_tokens_per_run` / `avg_output_tokens_per_run` by the real expected daily/weekly/monthly volume and the appropriate cadence-annualization factor — this simulation gives you the per-run numbers; the sheet's cadence math does the annualizing.
