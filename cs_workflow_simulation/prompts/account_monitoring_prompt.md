# Account Monitoring Prompt Template

**Stage:** Account monitoring
**Model:** Claude Haiku 4.5
**Maps to:** `daily_account_review()` in `workflow.py`

## Production usage

In production this is a high-volume, business-day-cadence pass across the
full active portfolio (750 accounts). It does not draft prose for a human;
it produces a compact structured record per account that downstream stages
(prioritization, escalation) consume. Routed to the cheapest capable model
because the task is data assembly and light delta computation, not
open-ended reasoning.

## Prompt template

```
You are reviewing account {account_id} ({account_name}) as part of the daily
account health scan. Given the account's current and prior health score,
most recent product usage event, open ticket count, and most recent NPS
response, produce a structured record with:
- health_score (current) and health_score_delta vs. prior
- usage_trend (up/down/flat) based on the latest usage event
- open_ticket_count
- nps_score (most recent, or null if none on file)
- one-line flag if any of the above moved adversely since the last scan

Do not recommend actions. Do not editorialize. Output structured fields only.
```

## Output shape (matches simulation's reviewed record)

```
{account_id}: health {current_health_score} (delta {health_delta}),
usage_trend={usage_trend}, open_tickets={ticket_count}, nps={nps_score}
```

## Notes

- Runs once per business day (cadence factor 260/year) across the entire
  active portfolio -- by far the highest call volume in the system, which is
  why it sits on the cheapest non-embedding model tier.
- Output feeds directly into Account prioritization; no need to re-fetch
  source data there.
