# Customer Check-in Preparation Prompt Template

**Stage:** Customer check-in support
**Model:** Claude Sonnet 4.6
**Maps to:** `customer_checkin_preparation()` in `workflow.py`

## Production usage

This stage synthesizes the memory packet from stage 0 plus outstanding
follow-up items and open tickets into a brief a CSM can walk into a call
with. Synthesizing several sources into a coherent, prioritized narrative
benefits from a stronger generative model than the lookup/classification
stages above it.

## Prompt template

```
Using the account memory packet below, prepare a check-in brief for the
upcoming {checkin_type} with {account_name} on {date}.

Memory packet: "{memory_packet}"
Open tickets: {issue_summaries}
Outstanding follow-up items from the last call: {follow_up_items}

Produce a brief with two sections:
1. Context recap (<=80 words): what matters going into this call, drawn
   only from the memory packet -- do not invent facts not present in it.
2. Next steps (3-5 bullets): concrete actions tied to the follow-up items
   and any open tickets, ordered by priority.

Do not repeat the full memory packet verbatim -- synthesize it.
```

## Output shape (matches simulation's checkin brief)

```
## {account_name} -- {checkin_type} on {date}
**Context:** {context_recap}
**Next steps:**
- {step_1}
- {step_2}
...
```

## Notes

- Must not re-derive context from scratch -- it consumes stage 0's memory
  packet directly, which is also why this stage is documented as depending
  on Memory & retrieval running first.
- Evaluation check "every check-in brief contains both prior context and
  next steps" is enforced downstream against this stage's output.
