# Worked Example: AI-Powered Academic Coaching System

Goal framing for this prompt: the system must *improve outcomes* and *reduce human intervention* — these can trade off against each other, so the design has to show how it earns reduced human load rather than just cutting it (i.e., automation must be justified by demonstrated AI quality, not assumed).

## Problem

Human academic coaches currently run weekly 1:1 check-ins with every student to review progress, set goals, and nudge on missed work. This caps coach caseload at ~80 students each and is the single largest line item in academic ops labor. Most check-ins are routine (on-track students); only a minority need real coaching judgment.

## System Architecture

- **Data sources:** LMS (assignment completion, scores, pacing vs. plan), SIS (enrollment, attendance), goal-setting tool (student-set weekly goals), prior coaching notes.
- **Pipeline:**
  ```
  [LMS/SIS/goals/notes] -> nightly ETL -> student progress feature store
        -> tiering engine (rules: on-track / watch / needs-coach)
              -> Tier "on-track": AI coach generates personalized check-in message
                    (progress summary, goal nudge, encouragement) -> student, no human review
              -> Tier "watch": AI drafts coaching talking points + flags reason
                    -> async human coach review (batched, not live meeting) -> approved message sent
              -> Tier "needs-coach": AI summarizes context -> routed straight to a live
                    human coaching session, AI does not draft outreach
  -> all tiers log outcome (goal completion, next-week trend) back into feature store
  ```
- **Orchestration:** tiering is a deterministic rules engine (cheap, auditable); the LLM is only used for tier-appropriate content generation/summarization, never for the tiering decision itself — keeps the highest-stakes routing decision out of model hands.
- **Retrieval:** RAG over the student's own history (past goals, past notes) so messages are personalized and consistent, not generic.
- **Human-in-the-loop tiers** (mirrors the architecture template's 3-tier model):
  - Autonomous: routine on-track check-ins.
  - Human-reviewed: watch-tier coaching drafts, reviewed in a batch queue (not a live call) — this is the actual labor reduction, turning a 30-min meeting into a 2-min approval.
  - Human-only: needs-coach tier and any safety/mental-health signal, always a live human session, never AI-drafted outreach.
- **Action layer:** approved messages send via the comms platform; all sends logged with tier, draft, edits, and human ID for audit.
- **Failure mode:** if tiering engine or LLM is unavailable, default every student to "needs-coach" (fail safe toward more human attention, never fewer reviews).

## AI Workflow (weekly cycle)

| Step | Actor | Input | Action | Output | Failure handling |
|---|---|---|---|---|---|
| 1 | System | LMS/SIS sync | Compute progress features (pacing delta, goal completion %, attendance) | Feature record/student | Missing data -> default to "needs-coach" tier |
| 2 | Rules engine | Feature record | Assign tier (on-track/watch/needs-coach) | Tier label | Ambiguous/borderline -> escalate to watch |
| 3 | AI | Tier + student history (RAG) | Generate check-in draft (structured: summary, nudge, tone) | Draft message + confidence | Low confidence -> force into watch-tier review |
| 4a | System (on-track) | Approved draft | Auto-send | Sent message, logged | n/a (no review) |
| 4b | Human coach (watch) | Draft + flag reason | Approve/edit/reject in batch queue | Sent message or escalation | SLA: queue cleared within 24h |
| 4c | Human coach (needs-coach) | AI context summary | Live coaching session | Session notes | n/a |
| 5 | System | Next week's outcome data | Compare predicted vs. actual trend | Feedback signal | Used to recalibrate tiering thresholds monthly |

**Guardrail:** any keyword/sentiment flag indicating safety/mental-health concern overrides tier assignment and routes to human-only immediately, regardless of where it surfaces in the pipeline.

## Cost Model

Assume 10,000 students, weekly cycle (~43,000 cycles/month at 4.3 weeks).

- **Tiering split (illustrative):** 70% on-track, 22% watch, 8% needs-coach.
- **LLM cost:** every student gets one generation/summarization call/week regardless of tier (~1,000 input tokens incl. RAG context + 250 output tokens). This is the bulk of inference volume but cheap per call — call out explicitly that inference is not the dominant cost here.
  ```
  Calls/month        = 10,000 x 4.3 = 43,000
  Input tokens/mo     = 43,000 x 1,000 = 43,000,000
  Output tokens/mo    = 43,000 x 250  = 10,750,000
  Inference cost/mo   = (43M/1M x $input_price) + (10.75M/1M x $output_price)
  ```
- **Human cost (the real budget line):**
  ```
  Watch-tier reviews/mo = 10,000 x 22% x 4.3 ≈ 9,460
  Review time           = 2 min/review (batch approval, not a meeting)
  Watch labor hrs/mo     = 9,460 x 2/60 ≈ 315 hrs

  Needs-coach sessions/mo = 10,000 x 8% x 4.3 ≈ 3,440
  Session time             = 30 min (unchanged from current process)
  Needs-coach labor hrs/mo = 3,440 x 30/60 ≈ 1,720 hrs

  Total coach hrs/mo (new)  ≈ 2,035 hrs
  Total coach hrs/mo (old, all students at 30 min/wk) ≈ 10,000 x 30/60 x 4.3 ≈ 21,500 hrs
  ```
  This is the headline number: ~90% reduction in coaching labor hours, with the saved time concentrated on the highest-need 8% rather than spread evenly — that's the "reduce human intervention while improving outcomes" thesis made concrete.
- **Cost per student/month:** `(Inference cost + Watch review labor + Needs-coach labor) / 10,000` — compare directly to the old all-human-meeting baseline cost/student.
- **Scaling sensitivity:** inference and watch-tier review cost scale linearly with enrollment; needs-coach labor is the step-function risk — if outcomes worsen and the needs-coach tier grows beyond ~8%, labor savings erode fast. This ratio is the single number to monitor for cost control.

## Risks

| Risk | Mitigation |
|---|---|
| Tiering misclassifies a struggling student as "on-track" (false negative) | Conservative thresholds; monthly recalibration against actual outcome data; any goal-completion miss 2 weeks running auto-escalates tier regardless of model output |
| Auto-sent on-track messages feel generic/impersonal, hurting trust | RAG personalization from student's own history; sample-audit a % of on-track messages weekly for quality |
| Coaches over-trust batched drafts and rubber-stamp without reading (Override Rate → 0) | Track Override Rate as a KPI; if it drops too low, randomly inject deliberately-flawed drafts into the review queue as a quality check (similar to spam-filter audits) |
| Safety/mental-health signal missed because system is optimized for academic pacing, not wellbeing | Independent keyword/sentiment safety classifier runs in parallel to tiering, not subordinate to it; any hit forces human-only regardless of academic tier |
| Equity: students with unstable home environments get systematically tiered "needs-coach," consuming coach capacity unevenly across demographics | Quarterly subgroup audit of tier distribution by demographic; investigate if any subgroup is structurally overrepresented in needs-coach beyond outcome-justified rates |
| Reduced human contact lowers student sense of being known/supported, even if metrics hold | Track a qualitative trust/satisfaction survey metric alongside quantitative KPIs; don't optimize on outcome metrics alone |
| Vendor/model outage disrupts weekly cycle | Fail-safe default (see architecture) routes everyone to needs-coach tier rather than silently skipping the cycle |

**Red line:** AI never independently decides a student needs no human contact for multiple consecutive cycles without a human coach's periodic spot-check, even if on-track every week — a fixed cadence (e.g. one human-reviewed touch every 6 weeks minimum) is mandatory regardless of tier.

## KPIs

- **North Star:** Intervention Success Rate (% of watch/needs-coach students who return to on-track within 4 weeks) and/or Mastery Rate trend.
- **Guardrails (must not regress while reducing human hours):**
  - Completion Rate and Mastery Rate — must hold or improve vs. pre-AI baseline.
  - Subgroup Performance Gap and tier-distribution-by-demographic — must not widen.
  - Student/parent trust survey score.
  - Override Rate — should be meaningfully above 0%, signaling real review not rubber-stamping.
- **Operational:**
  - Coach hours/student/month (the efficiency metric being optimized).
  - Escalation Rate from on-track → watch/needs-coach (catches tiering drift).
  - Safety-Flag Response Time (must stay near-zero tolerance for delay).

## Rollout Plan

- **Discovery (2 wks):** confirm LMS/SIS/goal-tool data access; baseline current coach hours, completion rate, mastery rate per coach.
- **Prototype (3 wks):** build tiering rules + AI draft generation; backtest tiering against last semester's actual outcomes to validate the 70/22/8 split assumption before touching live students.
- **Pilot (8 wks):** one coach's caseload (≈80 students) in shadow mode for 2 weeks (AI tiers and drafts, human coach still does full normal check-ins, compare AI tier vs. what the coach would have done), then live for 6 weeks with the batched-review workflow active.
- **Scale (one semester):** roll out coach-by-coach, not all at once; cap each coach's tier mix change to avoid a single coach absorbing a spike in needs-coach load.
- **Continuous improvement:** monthly tiering threshold recalibration from outcome data; quarterly subgroup fairness audit; quarterly trust survey; renegotiate model tier/cost as volume scales.
