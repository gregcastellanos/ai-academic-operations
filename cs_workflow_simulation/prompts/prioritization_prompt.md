# Account Prioritization Prompt Template

**Stage:** Prioritization
**Model:** Claude Haiku 4.5
**Maps to:** `account_prioritization()` in `workflow.py`

## Production usage

The scoring logic itself is intentionally rules-based and transparent (see
`workflow.py`'s `risk_score` / `opportunity_score` formula) -- it should
stay deterministic in production too, not be handed to an LLM to "decide."
What a cheap model *can* usefully do at this stage is normalize/extract the
inputs (e.g. classifying a free-text usage note into up/down/flat) before
the deterministic formula runs. The prompt below reflects that narrow role,
not score invention.

## Prompt template

```
Given the following reviewed signals for account {account_id}:
- health_score_delta: {health_delta}
- usage_trend: {usage_trend}
- open_ticket_count: {ticket_count}
- nps_score: {nps_score}
- has_open_high_severity_ticket: {bool}

Classify usage_trend into exactly one of {up, down, flat} if not already
categorical, and classify nps_score into {promoter, passive, detractor, none}.
Do not compute a risk or opportunity score yourself -- that calculation is
performed deterministically downstream from your classified fields.
```

## Output shape (matches simulation's prioritized record)

```
{account_id}: risk_score={risk_score}, opportunity_score={opportunity_score},
tier={Urgent|Watch|Expansion|Stable}
```

## Notes

- Tier thresholds (Urgent if open high-sev ticket or risk_score>=30, Watch if
  >=15, Expansion if opportunity_score>=20 and risk_score<10, else Stable)
  live in code, not in a prompt -- keeping the scoring auditable and
  recalibratable without touching any model.
- Same volume/cadence profile as Account monitoring, so it stays on the same
  cheap model tier.
