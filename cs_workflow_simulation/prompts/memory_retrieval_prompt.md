# Memory & Context Retrieval Prompt Template

**Stage:** Memory & retrieval
**Model:** text-embedding-3-small
**Maps to:** `memory_context_retrieval()` in `workflow.py`

## Production usage

This stage is input-only (embeddings, no generation), so there is no completion
prompt in the usual sense. In production this template represents the
retrieval query used to assemble each account's context packet via vector
search over the account's CRM record, call notes, support tickets, usage
events, and check-in calendar, instead of the direct lookup the simulation
uses against its small fixed dataset.

## Retrieval query template

```
Retrieve the most relevant context for account {account_id} ({account_name})
needed to support today's account review and any scheduled customer
interaction. Pull from:
- Account profile (segment, ACV, renewal date, health score history)
- Most recent product usage event and trend
- Open support tickets (exclude closed/resolved)
- Most recent call note (customer goal, blocker, follow-up items)
- Next scheduled check-in (date, type, topics)

Return a concise packet (<= 150 words) combining only the fields above,
in plain prose suitable for a CSM or a downstream automated stage to read
without re-querying the source systems.
```

## Output shape (matches simulation's `memory_packet` field)

```
{account_name} ({segment}, ${contract_value} ACV, renews {renewal_date}).
Health {current_health_score} (was {previous_health_score}). Usage trend:
{usage_trend}. Last call: {summary} - goal: {customer_goal}, blocker:
{risk_or_blocker}, follow-up: {follow_up_items}. {n} open ticket(s):
{issue_summaries}. Next check-in {date}: {checkin_type}.
```

## Notes

- No judgment or recommendation is made at this stage -- it is pure
  retrieval/assembly, which is why it is routed to the cheapest model tier
  (embeddings) rather than a generative model.
- Consumed directly by the Customer check-in support stage; should not be
  re-derived from scratch downstream.
