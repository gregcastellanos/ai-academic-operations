# Session Log — Crossover AI System Design Assessment

## Project Overview

The goal of this project was to design and implement an AI-assisted customer
success workflow capable of supporting a 750-account B2B SaaS portfolio
while maintaining output quality, responsiveness, and human oversight. The
deliverable is a runnable, deterministic Python simulation
(`cs_workflow_simulation/`) that demonstrates the full decision logic an
AI-backed customer success operation would need — account monitoring,
prioritization, issue routing, check-in preparation, quality review,
intervention planning, and escalation — together with a production-scale
token/cost model (Token Math Sheet), a set of production-equivalent LLM
prompt templates, and the supporting documentation needed for an evaluator
to verify the design without re-deriving it.

## AI Tools Used

**Primary tool: Claude Code**
- Repository setup and file/folder structure
- Architecture design (workflow stage breakdown, model routing)
- Workflow implementation (`workflow.py`, all 8 stages)
- Debugging (data flow between stages, evaluation-check logic,
  spreadsheet formula verification)
- Cost modeling (Token Math Sheet construction, measured-vs-scaled
  framework, scenario analysis)
- Prompt template creation (9 production-equivalent prompt files)
- Documentation (README, this session log, submission exports)

**Secondary tool: ChatGPT**
- Architecture review of the proposed 8-stage workflow before implementation
- Assessment preparation — clarifying what the Crossover rubric expects
  from a "workflow simulation" deliverable
- Systems-design critique of the risk/opportunity scoring approach
- Token-math review — sanity-checking the cadence-annualization and
  measured-vs-scaled framing before it was finalized in Claude Code
- Submission review and final narrative refinement across Submissions A, B,
  and C

## Major Milestones

1. **Repository creation** — initial repo structure and README established
   for the AI Academic Operations assessment context, with the assessment
   prep templates and worked examples added first.
2. **Dataset inspection** — reviewed the 7 provided CSVs (`accounts.csv`,
   `usage_events.csv`, `support_tickets.csv`, `call_notes.csv`,
   `scheduled_checkins.csv`, `junior_outputs.csv`, `quality_standards.csv`)
   to confirm what real fields existed before designing any stage logic
   against them.
3. **Workflow architecture design** — defined the 8 workflow stages, their
   inputs/outputs, and a transparent risk/opportunity scoring formula
   before writing implementation code, so the design could be reviewed on
   its own merits.
4. **Workflow implementation** — built `workflow.py`: account review,
   prioritization, ticket routing, check-in preparation, output quality
   review, intervention planning, and escalation/follow-up consolidation,
   each as an independently testable function.
5. **Evaluation framework** — added four automated evaluation checks run
   at the end of every execution (Urgent accounts have an action,
   high-severity tickets are never left unrouted, check-in briefs carry
   both context and next steps, every junior output is checked against
   all of its tagged standards).
6. **Memory/retrieval stage addition** — identified during self-review that
   a memory/context retrieval stage was missing from the original 7-stage
   design; added it as Stage 0 so check-in preparation could consume a
   single assembled context packet instead of re-deriving context inline.
7. **Token math development** — built the Token Math Sheet from measured
   per-run simulation data, then corrected and rebuilt it on the
   assignment's actual 750-account production scope (30 tickets/week, 12
   check-ins/week, biweekly interventions) after a self-audit against the
   assignment PDF caught that the first pass had scaled off the 18-account
   demo dataset instead.
8. **Prompt template creation** — wrote 9 production-equivalent prompt
   templates (one per AI-backed stage) documenting the prompts a live LLM
   system would use, without converting the deterministic simulation to
   live API calls.
9. **Documentation updates** — expanded `README.md` to cover setup,
   per-stage explanation, output file meanings, model routing rationale,
   the 18-account-to-750-account scaling logic, 24/7 responsiveness,
   failure handling, human-in-the-loop design, and known limitations.
10. **Final audit and submission preparation** — ran a strict pass/fail
    self-audit against the assignment's explicit Submission A/B/C
    requirements, fixed every gap found, and prepared the Token Math Sheet
    export (Submission A), the final workflow repository (Submission B),
    and this session log (Submission C).

## Key Design Decisions

### Deterministic simulation vs. live API calls

**Problem:** Demonstrate the reasoning and routing logic of an AI-backed
workflow without making the assessment deliverable dependent on live API
keys, network calls, or non-reproducible model output.

**Alternatives considered:** (a) call a real LLM API for every stage; (b)
mock LLM responses with canned strings; (c) implement the decision logic
deterministically in Python and represent the production LLM calls
separately as prompt templates.

**Final decision:** Option (c) — a fully deterministic, rule-based
simulation, with a parallel `prompts/` folder showing the production
prompts each stage would use against a real model.

**Rationale:** A deterministic implementation is auditable line by line,
re-runs identically every time (important for grading), and requires no
credentials or network access. It still demonstrates the actual decision
logic — severity-vs-tier routing, risk scoring, quality-standard checks —
that an LLM-backed system would need to encode in its prompts, which is
what the prompt templates capture separately.

### Human-in-the-loop review

**Problem:** An AI system touching customer-facing communication and
account risk decisions cannot be allowed to act unsupervised.

**Alternatives considered:** (a) fully autonomous send/resolve actions;
(b) human approval gates at every single step; (c) targeted human
checkpoints only where the cost of an error is highest.

**Final decision:** Option (c). Every stage produces a recommendation or
routing decision, never a final customer-facing action. Output quality
review's only outcomes are Approve/Revise/Escalate (never auto-send);
intervention plans are assigned to a named human owner with a due window;
escalations route to a human queue rather than auto-resolving.

**Rationale:** Full autonomy is the highest-risk option for
customer-facing actions; full human gating at every step defeats the
purpose of automation. Concentrating human checkpoints at quality review,
intervention ownership, and escalation keeps oversight where mistakes are
costliest while letting low-judgment stages (monitoring, prioritization)
run unattended.

### Model routing strategy

**Problem:** Different stages have very different volume and judgment
profiles; routing all of them to one model wastes budget or under-powers
hard reasoning.

**Alternatives considered:** (a) single frontier model for every stage;
(b) single cheap model for every stage; (c) per-stage routing matched to
volume and judgment difficulty.

**Final decision:** Option (c) — embeddings for retrieval, Claude Haiku
4.5 for high-volume/low-judgment monitoring and prioritization, Claude
Sonnet 4.6 for judgment-heavy routing/check-in/intervention stages, GPT-5.4
mini for rubric-based quality review (cross-provider routing), and Claude
Opus 4.7 reserved for the lowest-volume/highest-stakes escalation
consolidation.

**Rationale:** Matches the assessment's explicit principle — cheap models
for high-volume/simple work, stronger models only where reasoning is
genuinely hard — and keeps the resulting annual cost (~$223/year on the
750-account base case) a small fraction of the $50,000 budget rather than
inflating spend to use it up.

### Memory/context retrieval stage

**Problem:** The original 7-stage design had check-in preparation
re-deriving account context (profile, tickets, call notes, usage) inline
every time, with no single place that context was assembled once.

**Alternatives considered:** (a) leave context assembly inline in
check-in preparation; (b) add a dedicated memory/retrieval stage that runs
first and produces one packet per account that other stages consume.

**Final decision:** Option (b), added as Stage 0.

**Rationale:** Mirrors how a production RAG pipeline would work — index
and retrieve once, consume downstream — and is consistent with the
assignment's stated requirement that memory/retrieval be a distinct
operating area in the Token Math Sheet, not folded into check-in support.

### Cost optimization strategy

**Problem:** Demonstrate defensible, non-inflated token/cost math against
a fixed $50,000/year budget without either inflating spend to "use" the
budget or under-scoping the workload.

**Alternatives considered:** (a) build the cost model directly off the
18-account demo dataset's absolute numbers; (b) measure real per-run token
sizes on the demo dataset, then explicitly scale those measured per-run
costs to the assignment's actual 750-account production volumes.

**Final decision:** Option (b), with every line item labeled Measured,
Scaled estimate, or Assumption in the Candidate Assumptions tab.

**Rationale:** The 18-account dataset is too small to represent production
volume directly, but it is real, measured per-run data — discarding it
would lose a verifiable foundation. Scaling it by a documented ratio to the
correct production volume, while labeling exactly which numbers are
measured vs. assumed, satisfies the assessment's "defensible cell by cell"
bar without fabricating precision that doesn't exist.

### Evaluation framework

**Problem:** Need an auditable way to confirm the workflow doesn't silently
drop high-risk accounts, unresolved tickets, incomplete briefs, or
unchecked outputs.

**Alternatives considered:** (a) trust each stage's internal logic and
report no aggregate checks; (b) add explicit end-to-end evaluation checks
that re-verify completeness across stage boundaries.

**Final decision:** Option (b) — four automated checks run after every
execution, plus a failure-handling path (`evaluation_failures.json`) that
records a recommended remediation route if any check ever fails.

**Rationale:** Per-stage logic can be individually correct yet still leave
gaps at the seams (e.g. an Urgent account with no intervention plan because
of a tier-recalculation timing issue). End-to-end checks catch exactly that
class of bug, and writing failures to a dedicated file (rather than only
printing PASS/FAIL to console) gives a future failure a concrete next
action instead of just a red flag.

### Escalation logic

**Problem:** Decide which tickets and quality-review misses require
immediate human escalation vs. standard handling, without a flat
severity-only rule that ignores account risk context.

**Alternatives considered:** (a) route purely on ticket severity; (b)
route on severity weighted by account priority tier, so the same ticket
severity can produce different routes depending on account risk.

**Final decision:** Option (b) — high severity always escalates
regardless of tier; medium severity escalates only on Urgent/Watch
accounts (risk compounding); low severity resolves immediately unless
sentiment is negative. A QS003 (risk accuracy) or QS005 (escalation
judgment) quality-review failure forces escalation regardless of other
standards passed.

**Rationale:** A flat severity-only rule would either over-escalate low-
risk accounts or under-escalate genuinely at-risk ones; weighting by tier
reflects how a real CS organization actually triages — the same complaint
is a bigger problem on an account that's already failing than on a
healthy one.

## Files Created

| File | Purpose |
|---|---|
| `cs_workflow_simulation/workflow.py` | Core deterministic simulation — all 8 workflow stages, scoring logic, evaluation checks, failure handling, and token/cost ledger |
| `cs_workflow_simulation/README.md` | Setup/run instructions, stage-by-stage explanation, model routing rationale, scale mapping, failure handling, human-in-the-loop design, and known limitations |
| `session_log.md` | This document — Submission C deliverable |
| `cs_workflow_simulation/outputs/token_cost_summary.csv` | Measured per-stage token/cost rollup from the 18-account simulation run; source data for the Token Math Sheet |
| `cs_workflow_simulation/outputs/run_summary.json` | Aggregate run counts, evaluation check results, and 5 fully expanded representative end-to-end account runs |
| `cs_workflow_simulation/outputs/memory_context_retrieval.csv` | One memory packet per account (Stage 0 output) |
| `cs_workflow_simulation/outputs/account_prioritization.csv` | All 18 accounts ranked with risk/opportunity scores and tier |
| `cs_workflow_simulation/outputs/issue_routing.csv` | Every support ticket with its route and routing reason |
| `cs_workflow_simulation/outputs/checkin_briefs.md` | Human-readable check-in briefs per scheduled check-in |
| `cs_workflow_simulation/outputs/quality_review.csv` | Every junior output's standards-checked results and recommendation |
| `cs_workflow_simulation/outputs/intervention_plan.md` | Recommended actions for Urgent/Watch/Expansion accounts, grouped by tier |
| `cs_workflow_simulation/outputs/evaluation_failures.json` | Evaluation-check failures (if any) with recommended remediation routes; empty on the current dataset |
| `cs_workflow_simulation/outputs/Token_Math_Sheet_Completed.xlsx` | Completed Token Math Sheet on the 750-account production base case |
| `cs_workflow_simulation/outputs/Submission_A_Token_Math_Sheet.xlsx` | Clean renamed export of the Token Math Sheet for Submission A |
| `cs_workflow_simulation/outputs/Submission_A_Token_Math_Template.csv` | CSV export of the Token Math Template tab |
| `cs_workflow_simulation/prompts/memory_retrieval_prompt.md` | Production prompt template for the memory/retrieval stage |
| `cs_workflow_simulation/prompts/account_monitoring_prompt.md` | Production prompt template for daily account monitoring |
| `cs_workflow_simulation/prompts/prioritization_prompt.md` | Production prompt template for account prioritization |
| `cs_workflow_simulation/prompts/inbound_issue_routing_prompt.md` | Production prompt template for inbound ticket routing |
| `cs_workflow_simulation/prompts/checkin_preparation_prompt.md` | Production prompt template for check-in brief preparation |
| `cs_workflow_simulation/prompts/output_quality_review_prompt.md` | Production prompt template for junior-output quality review |
| `cs_workflow_simulation/prompts/intervention_planning_prompt.md` | Production prompt template for targeted intervention planning |
| `cs_workflow_simulation/prompts/escalation_prompt.md` | Production prompt template for 24/7 escalation consolidation |
| `cs_workflow_simulation/prompts/evaluation_qa_prompt.md` | Production prompt template for sampled QA review |

## Issues Encountered

- **Missing workflow stage (memory/retrieval).** The first implementation
  pass had check-in preparation re-deriving account context inline, with
  no dedicated retrieval stage. Caught during architecture self-review,
  before the assignment's explicit memory/retrieval requirement was
  re-checked against the PDF. **Resolved** by adding Stage 0
  (`memory_context_retrieval`), which now runs first and is consumed
  directly by check-in preparation.
- **Token math scaling concerns.** The first Token Math Sheet pass used
  the 18-account demo dataset's absolute numbers as the base case, which
  understated real production cost and risked confusing demo-scale numbers
  with production-scale conclusions. **Resolved** by rebuilding the base
  case at the assignment's actual 750-account scope and using the
  18-account run strictly as the measured per-run source, scaled by a
  documented volume ratio.
- **750-account portfolio assumptions.** Several volumes (30 tickets/week,
  12 check-ins/week, biweekly interventions, business-day monitoring) are
  given in the assignment but ticket/intervention volume by tier still had
  to be derived from the simulation's own risk-tier output rather than
  invented. **Resolved** by deriving intervention volume from the actual
  Urgent/Watch/Expansion tier counts produced by `account_prioritization()`
  on the measured dataset, scaled proportionally to 750 accounts, and
  documenting that derivation in the Candidate Assumptions tab.
- **Prompt template requirement gap.** The original deliverable had zero
  prompt templates — the simulation's deterministic logic stood in for
  every stage with no documented production-equivalent prompt. **Resolved**
  by adding all 9 required prompt template files in `prompts/`, each
  grounded in the actual function signature and output shape of its
  corresponding stage, without altering the deterministic code itself.
- **Evaluation coverage concerns.** The original 4 evaluation checks
  verified structural completeness but had no failure-handling path if a
  check ever failed — a failure would only print to console and be easy to
  miss. **Resolved** by adding `write_evaluation_failures()`, which writes
  every failed check to `outputs/evaluation_failures.json` with a named
  recommended remediation route, run automatically every execution.

## Testing and Validation

- **Workflow execution:** `python3 cs_workflow_simulation/workflow.py` was
  re-run from the repository root after every substantive change (stage
  additions, failure-handling logic, README updates) to confirm the script
  completes without errors and produces identical, reproducible output
  given the static dataset.
- **Evaluation checks:** all 4 automated checks — every Urgent account has
  an action, every high-severity ticket is escalated or resolved, every
  check-in brief has context and next steps, every junior output is
  checked against all tagged standards — were confirmed PASS on every
  re-run of the final implementation.
- **Representative account runs:** verified 5 fully expanded end-to-end
  account runs exist in `run_summary.json` (A008, A005, A014, A010, A017),
  each showing every stage's output for the same account, confirmed by
  direct inspection of the JSON structure.
- **Quality-review testing:** spot-checked `quality_review.csv` output
  against the QS001–QS006 standards each junior output was tagged with,
  confirming recommendations (Approve / Revise / Escalate to senior CSM
  review) matched the underlying pass/fail pattern (e.g. a QS005 failure
  on an account with an open high-severity ticket correctly forced an
  Escalate recommendation).
- **Escalation testing:** confirmed every high-severity ticket in
  `issue_routing.csv` routed to `escalation` (none left in
  `standard_resolution`), and confirmed medium-severity tickets only
  escalated on Urgent/Watch-tier accounts as designed.
- **Token-cost validation:** independently re-computed the Token Math
  Sheet's formula logic in a standalone Python script (pricing lookups ×
  cadence annualization) and cross-checked the result against the sheet's
  computed totals — confirmed $223.27/year estimated annual cost and
  0.4465% budget utilization on the 750-account base case, with formula
  recalculation also verified once the file was opened in a spreadsheet
  application.

**Final evaluation results (last run):**
```
Accounts reviewed: 18 (Urgent: 8, Watch: 2, Expansion: 5, Stable: 3)
Tickets routed: 12 | Check-in briefs: 12 | Junior outputs reviewed: 8 | Intervention plans: 15
[PASS] every_high_risk_account_has_action
[PASS] every_high_severity_ticket_escalated_or_resolved
[PASS] every_checkin_has_context_and_next_steps
[PASS] every_junior_output_checked_against_standards
evaluation_failures.json: 0 failures
```

## Final Outcome

- The 8-stage workflow (memory/retrieval through escalation consolidation)
  is implemented, runnable end to end with a single command, and produces
  reproducible output against the provided dataset.
- All required operating areas are covered: memory/retrieval, account
  monitoring, prioritization, inbound issue handling, customer check-in
  support, output quality review, targeted intervention planning,
  escalation/follow-up/resolution routing, and evaluation/QA.
- The Token Math Sheet is completed on the assignment's actual 750-account
  production base case, with every figure labeled Measured, Scaled
  estimate, or Assumption, and a Scenario Analysis covering Base, Stress,
  and Optimized cases.
- All 9 production-equivalent prompt templates are completed, one per
  AI-backed stage, without converting the deterministic simulation to live
  API calls.
- The evaluation framework (4 automated checks plus failure-handling
  output) is implemented and passing on every run.
- Submission artifacts are prepared: Submission A (Token Math Sheet
  export), Submission B (audited, documented, runnable repository), and
  Submission C (this session log).

## Lessons Learned

Get the context assembled before any decision logic runs — the
memory/retrieval stage almost got skipped because it felt like overhead
next to "real" stages like routing and escalation, but every downstream
decision (check-in briefs, intervention plans) was weaker without a single
place that context was assembled once and trusted afterward. Build
retrieval first, decide second.

Keep humans in the loop at the points where being wrong is expensive, not
at every point. Gating every single stage behind human approval would have
defeated the purpose of automation; gating none of it would have been
reckless given this touches customer communication and account risk. The
right design concentrates oversight at quality review, intervention
ownership, and escalation — exactly where a bad call costs the most — and
lets the high-volume, low-judgment stages run unattended.

Cost-aware design means measuring before scaling, not scaling before
measuring. The first token-math pass made the mistake of treating the demo
dataset's absolute numbers as the production estimate; the fix wasn't to
guess bigger numbers, it was to measure real per-run cost on whatever data
existed, then scale that measured number by a documented ratio. Defensible
math is built from measured units, not estimated totals.

Scalable operations need rules that are recomputable by hand. Every
scoring formula and routing rule in this system is something a CSM
manager could re-derive on a whiteboard — that's not an accident, it's
what makes the system auditable and recalibratable later. An AI system a
human can't explain is an AI system a human can't fix when it's wrong.

Outcomes have to be measured against the real target, not the proxy. Health
score, ticket volume, and NPS are leading indicators for retention and
churn — useful for early action, but not the actual goal. A system that
optimizes the proxy without periodically checking it against the real
outcome will eventually drift from what it was built to predict.

## Appendix: Prompt History Summary

A concise chronological summary of the major Claude Code prompts, revisions,
and decisions across this engagement:

1. **Initial build request** — build a runnable AI-assisted customer
   success workflow simulation for the Crossover assessment, covering
   account review, prioritization, issue routing, check-in preparation,
   quality review, intervention planning, and escalation.
2. **Self-review prompt** — review the workflow for missing stages,
   resulting in the addition of the memory/context retrieval stage as
   Stage 0.
3. **Token Math Sheet build request** — build the Token Math Sheet from
   measured simulation values across the required operating areas, with
   cost-per-run/day/month/year and documented assumptions.
4. **Pre-submission audit request** — audit the full repository against
   the actual assignment PDF (10-point checklist), which surfaced the
   18-vs-750-account scale error, missing prompt templates, missing
   session log, and missing shared submission links.
5. **Token Math Sheet correction request** — rebuild the Token Math Sheet
   on the assignment's actual 750-account production scope, using the
   18-account simulation strictly as the measured per-run baseline, with
   explicit measured/scaled/assumption labeling.
6. **5-priority ordered build-out request** — (1) confirm the 750-account
   base case, (2) add 9 prompt templates without converting the workflow
   to live LLM calls plus README updates, (3) add evaluation
   failure-handling, (4) write a session log, (5) re-run and final-audit,
   then commit and push.
7. **Submission A request** — locate, verify, and export the completed
   Token Math Sheet as a clean `.xlsx`/`.csv` pair, with upload/sharing
   instructions for Google Drive.
8. **Submission B request** — final strict-evaluator audit of the full
   repository against every Submission B requirement; identified and
   fixed two remaining README gaps ("how humans stay in the loop," "known
   limitations") before final commit/push.
9. **Submission C request** — produce this polished, professional session
   log (this document), structured to read as a project record rather than
   a transcript, followed by a self-audit against the Submission C
   requirements.

---

## Submission C Self-Audit

| Requirement | Status |
|---|---|
| Project Overview section | PASS |
| AI Tools Used (Primary: Claude Code, Secondary: ChatGPT, each with sub-bullets) | PASS |
| Major Milestones (10 phases, in order) | PASS |
| Key Design Decisions (problem/alternatives/decision/rationale, covering all 7 required topics) | PASS |
| Files Created (workflow.py, README.md, session_log.md, token_cost_summary.csv, run_summary.json, all prompt templates, all workflow outputs) | PASS |
| Issues Encountered (all 5 required topics, each with resolution) | PASS |
| Testing and Validation (execution, evaluation checks, representative runs, quality-review testing, escalation testing, token-cost validation, final results) | PASS |
| Final Outcome (workflow, operating areas, token math, prompt templates, evaluation framework, submission artifacts) | PASS |
| Lessons Learned (practical operator voice; context, oversight, cost-aware design, scalable operations, measurable outcomes) | PASS |
| Appendix: chronological prompt/decision summary (not a transcript dump) | PASS |
| Reads as a professional project record, not a chat log | PASS |

**Result: 11/11 PASS — Submission C is ready.**
