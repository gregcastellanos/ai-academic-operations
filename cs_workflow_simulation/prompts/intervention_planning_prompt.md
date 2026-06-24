# Targeted Intervention Planning Prompt Template

**Stage:** Targeted intervention planning
**Model:** Claude Sonnet 4.6
**Maps to:** `intervention_plan_for_account()` / `targeted_intervention_planning()` in `workflow.py`

## Production usage

Bounded to Urgent/Watch/Expansion-tier accounts only, so volume is
naturally low (biweekly cadence in production) even though each call is the
richest in the pipeline -- it combines the risk/opportunity score, the most
recent call note, and open tickets into a tailored recommendation, which is
multi-signal reasoning rather than a lookup.

## Prompt template

```
Account {account_id} is tier {tier} (risk_score={risk_score},
opportunity_score={opportunity_score}). Using the most recent call note and
open tickets below, recommend one targeted intervention.

Call note: "{note_summary}" (goal: {customer_goal}, blocker: {risk_or_blocker})
Open tickets: {issue_summaries}

Produce:
- action: a specific, owner-executable next action (not generic advice)
- owner: the role best positioned to execute it (CSM / Support / Sales / CSM Manager)
- due_window: a concrete time window (e.g. "within 5 business days")
- rationale: 1-2 sentences tying the action directly to the risk or
  opportunity signal that triggered it

Do not recommend an intervention for Stable-tier accounts.
```

## Output shape (matches simulation's intervention plan record)

```
{account_id} ({tier}): action="{action}", owner={owner},
due_window={due_window}, rationale="{rationale}"
```

## Notes

- Runs roughly biweekly across the Urgent/Watch/Expansion subset of the
  750-account portfolio, not the full book -- volume is gated by the tier
  output of the Prioritization stage.
- Every Urgent-tier account having a recommended action is one of the four
  automated evaluation checks.
