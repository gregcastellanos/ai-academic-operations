# Inbound Support Issue Routing Prompt Template

**Stage:** Inbound issue handling
**Model:** Claude Sonnet 4.6
**Maps to:** `route_ticket()` / `inbound_support_issue_routing()` in `workflow.py`

## Production usage

Routing needs to weigh ticket severity against account risk context (tier),
not just look severity up in a table -- e.g. a medium-severity ticket on an
Urgent-tier account should escalate, while the same ticket on a Stable
account should not. That conditional judgment is why this stage sits on a
stronger model than monitoring/prioritization.

## Prompt template

```
Route the following support ticket for account {account_id} (current
priority tier: {tier}):

Ticket: severity={severity}, sentiment={sentiment}, summary="{summary}"

Choose exactly one route:
- escalation: severity is high, OR severity is medium and the account is
  Urgent/Watch tier (risk compounding)
- immediate_resolution: severity is low and sentiment is not negative
- standard_resolution: everything else

Return the route and a one-sentence reason citing the specific severity,
tier, and sentiment values that drove the decision.
```

## Output shape (matches simulation's routed ticket record)

```
{ticket_id} ({account_id}): route={escalation|standard_resolution|immediate_resolution},
reason="{reason}"
```

## Notes

- High severity always escalates regardless of tier -- a hard rule, not a
  judgment call, and should remain a hard rule in the prompt's instructions
  even when an LLM is doing the routing.
- Output is consumed by Escalation/follow-up routing (stage 7) for final
  consolidation.
