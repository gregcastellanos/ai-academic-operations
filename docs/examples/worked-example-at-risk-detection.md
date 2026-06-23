# Worked Example: AI-Powered Early Warning System for At-Risk Students

This is a fully filled-in example using all six templates together, in the style/depth expected in a 60-90 minute timed assessment response.

## Problem

Academic ops staff manually review gradebook + attendance weekly to spot at-risk students; this doesn't scale past ~200 students per advisor and catches problems 2-3 weeks late.

## System Architecture (see system-architecture-template.md)

- **Data sources:** LMS (assignment scores, login activity), SIS (attendance, enrollment), comms platform (parent contact log).
- **Pipeline:** nightly batch ETL -> feature store (rolling 14-day attendance %, grade trend slope, engagement score) -> rules engine pre-filter (cheap) -> LLM reasoning step only for borderline/ambiguous cases (cascade architecture, controls cost) -> ranked risk list with rationale -> advisor dashboard.
- **Human-in-the-loop:** AI never contacts a student/parent directly. It produces a ranked, explained list; an advisor decides the intervention.
- **Action layer:** advisor-approved action (email, meeting request) logged back into SIS.

## AI Workflow

1. Trigger: nightly batch job after SIS/LMS sync.
2. Rules pre-filter: any student with attendance < 85% OR grade drop > 15% in 14 days enters the candidate pool (cheap, deterministic, catches obvious cases without AI cost).
3. LLM reasoning step (only on candidate pool, not full population): given the student's structured trend data, produce (a) a risk rationale in plain language, (b) suggested intervention type, (c) confidence score. Output is structured JSON, not free text.
4. Human review: advisor sees ranked list + rationale, approves/edits/dismisses.
5. Feedback loop: outcome (did the student's metrics improve within 30 days of intervention?) is logged and used to recalibrate the rules-engine thresholds quarterly.

## Cost Model

Assume 10,000 students, ~8% enter the candidate pool nightly after rules pre-filter (~800/night, but most are repeats — dedupe to ~150 *new* LLM evaluations/week realistically). At ~1,200 input + 200 output tokens per evaluation:
- LLM cost is small (low call volume due to rules pre-filter doing the heavy lifting — this is the cost lever to highlight).
- Dominant cost is advisor review time: assume 5 min/review x ~150/week x advisor hourly rate — call this out as the real budget line, not inference.

## Risks

- False negative on a safety-relevant case (e.g. attendance drop due to abuse at home) — mitigate with mandatory escalation rule: any case mentioning safety keywords routes directly to a counselor, bypassing the standard queue.
- Bias: rules thresholds (attendance %, grade slope) may disadvantage students with unstable home internet (engagement metric penalizes them unfairly) — mitigate with quarterly subgroup audit.
- Over-reliance: advisors rubber-stamping AI suggestions without review — mitigate by tracking Override Rate KPI; if it drops near 0%, audit whether review is meaningful.

## KPIs

North Star: Intervention Success Rate. Guardrails: Subgroup Performance Gap, Cost Per Student, Override Rate, Safety-Flag Response Time.

## Implementation Plan

Discovery (2 wks, confirm data access) -> Prototype (3 wks, rules engine + LLM rationale on historical data, backtest against known past at-risk cases) -> Pilot (6 wks, one grade level, shadow mode first 2 weeks) -> Scale (rollout by grade level over a semester) -> Continuous improvement (quarterly threshold recalibration + fairness audit).
