# Implementation Plan Template

## Phase 0 - Discovery (1-2 weeks)

- Interview stakeholders (instructors, ops, students/parents if applicable).
- Map current workflow as-is (who does what, how long, error rate).
- Confirm data availability/quality (can you actually get the inputs the AI needs?).
- Define success metrics and baseline values (see KPI Dashboard template).
- Identify compliance constraints (FERPA/COPPA/state law) up front — not as an afterthought.

**Exit criteria:** signed-off problem statement, baseline metrics, data access confirmed.

## Phase 1 - Prototype (2-4 weeks)

- Build the smallest version that proves the AI step works (single workflow, no integrations).
- Evaluate on a held-out sample with human-graded accuracy/quality.
- Define the human-in-the-loop checkpoint and review UI (even a spreadsheet is fine at this stage).

**Exit criteria:** prototype hits target accuracy on offline eval; cost-per-call estimated.

## Phase 2 - Pilot (4-8 weeks)

- Deploy to a limited cohort (one class, one grade level, one campus).
- Run shadow mode first if stakes are high (AI recommends, human decides, compare to AI-only counterfactual).
- Instrument logging/observability from day one.
- Weekly review of false positives/negatives with stakeholders.

**Exit criteria:** pilot KPIs meet/exceed baseline; no critical safety/compliance incidents; staff sign-off to scale.

## Phase 3 - Scale (ongoing)

- Roll out cohort-by-cohort (not all-at-once) with rollback plan at each step.
- Automate the human-review sampling rate down as confidence in the model is validated over time.
- Set up ongoing model/prompt monitoring and retraining cadence.
- Establish an incident response process (what happens when the AI is wrong in a way that harms a student).

**Exit criteria:** full deployment, KPI dashboard live, support/escalation process staffed.

## Phase 4 - Continuous Improvement

- Feedback loop from outcomes back into prompts/model/thresholds (tie to AI Workflow template section 6).
- Quarterly bias/fairness audit across subgroups.
- Cost review against the Cost Modeling template — renegotiate model tier as volume changes.

## Cross-Cutting: RACI Sketch

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Model/prompt changes | | | | |
| Human review of AI output | | | | |
| Compliance sign-off | | | | |
| Incident response | | | | |

## Timeline Summary

| Phase | Duration | Key risk if skipped |
|---|---|---|
| Discovery | | Building the wrong thing |
| Prototype | | Sinking cost into a workflow that doesn't generalize |
| Pilot | | Scaling failures discovered at scale instead of small |
| Scale | | No rollback path if something breaks |
