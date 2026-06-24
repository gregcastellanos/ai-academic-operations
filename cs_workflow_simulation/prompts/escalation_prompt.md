# Escalation / 24-7 Responsiveness Prompt Template

**Stage:** 24/7 responsiveness / escalation
**Model:** Claude Opus 4.7
**Maps to:** `escalation_followup_routing()` in `workflow.py`

## Production usage

The final consolidation pass: every routed ticket (stage 3) and every
reviewed output (stage 5) must land in exactly one bucket. This is the
highest-stakes, lowest-volume stage -- it runs continuously (event-driven,
24/7) but only against items already flagged as escalation-worthy, so it
gets the frontier model reserved for cases where getting the call wrong has
the most consequence (e.g. a major account churning, a mishandled
high-severity ticket).

## Prompt template

```
You are the final escalation consolidation step, available 24/7. Given the
following items already flagged upstream:

Routed tickets: {ticket_routes} (route per ticket: escalation /
standard_resolution / immediate_resolution)
Quality review outcomes: {quality_outcomes} (Approve / Revise / Escalate to
senior CSM review)

For each item, confirm its final bucket -- escalation, follow_up, or
immediate_resolution -- and, for anything landing in escalation, draft a
2-3 sentence handoff summary a human senior CSM or support lead can act on
immediately without re-reading the full ticket/output history.

Every item must land in exactly one bucket. Do not leave anything
unclassified.
```

## Output shape (matches simulation's consolidated routing record)

```
{item_id}: bucket={escalation|follow_up|immediate_resolution},
handoff_summary="{summary if escalation}"
```

## Notes

- Lowest call volume in the system but highest per-call stakes -- the
  opposite profile from Account monitoring, which is the explicit rationale
  for putting it on Claude Opus 4.7 while monitoring runs on Haiku.
- "Every high-severity ticket routes to escalation or immediate_resolution,
  never sits in a standard queue" is one of the four automated evaluation
  checks enforced against this stage's output.
