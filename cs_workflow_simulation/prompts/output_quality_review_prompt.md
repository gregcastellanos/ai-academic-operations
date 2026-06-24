# Output Quality Review Prompt Template

**Stage:** Output quality review
**Model:** GPT-5.4 mini
**Maps to:** `output_quality_review()` and `check_qs001`-`check_qs006` in `workflow.py`

## Production usage

The simulation implements QS001-QS006 as deterministic keyword/structure
heuristics so the assessment run is auditable and repeatable. In production
this is exactly the kind of rubric-based judgment an LLM-as-judge earns its
cost on -- semantic overlap, tone, and risk-proportionality are not
reliably rule-based at scale. Routed cross-provider to GPT-5.4 mini to
demonstrate routing isn't locked to one vendor, and because rubric scoring
against named standards doesn't require a frontier model.

## Prompt template

```
Evaluate the following junior-drafted output against each quality standard
it is tagged with. Score each standard pass/fail and give a one-sentence
reason per standard.

Junior output: "{draft}"
Source call note (for context grounding): "{note_summary}"
Account tier: {tier}
Has open high-severity ticket: {bool}
Tagged standards: {qs_id_list}

Standards:
- QS001 Context grounding: does the draft reflect the actual call note content?
- QS002 Actionability: does the draft contain a concrete next action?
- QS003 Risk accuracy: does risk language match the account's actual tier?
- QS004 Tone/clarity: is the language clear and appropriately professional?
- QS005 Escalation judgment: if there's an open high-sev ticket or Urgent
  tier, does the draft correctly flag escalation?
- QS006 Follow-up continuity: does the draft address prior follow-up items?

Return: pass/fail per tagged standard, and an overall recommendation of
Approve (all pass), Revise (minor/non-escalation failures), or
Escalate to senior CSM review (QS003 or QS005 failure).
```

## Output shape (matches simulation's quality_review record)

```
{output_id}: failed=[{qs_ids}], recommendation={Approve|Revise|Escalate to senior CSM review}
```

## Notes

- None of an output's tagged standards may be silently skipped -- this is
  one of the four automated evaluation checks run at the end of every
  execution.
- A QS003 or QS005 failure forces escalation regardless of how many other
  standards passed, mirroring the code's `if any(f in ("QS003","QS005")...)` rule.
