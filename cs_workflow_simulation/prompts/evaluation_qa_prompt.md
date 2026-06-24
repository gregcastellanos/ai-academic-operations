# Evaluation / QA Prompt Template

**Stage:** Evaluation / QA
**Model:** GPT-5.4 mini
**Maps to:** `run_evaluation_checks()` in `workflow.py` (the 4 automated checks),
plus the weekly sampled-review row in the Token Math Sheet

## Production usage

Two distinct QA layers exist in this system:

1. **Automated structural checks** (`run_evaluation_checks()`) -- deterministic,
   run every execution, no LLM involved (e.g. "every Urgent account has an
   action," "every high-severity ticket is escalated or resolved"). These
   stay rule-based in production; they're verifying structural completeness,
   not judgment quality.
2. **Sampled output QA** -- a periodic (weekly) LLM-based review of a
   sample of actual outputs across all stages, checking for drift between
   what the rubric heuristics (stage 5) approved and what a reviewer would
   actually accept. This is the call this prompt template covers.

## Prompt template

```
You are performing weekly QA sampling. Review the following sample of
{n} outputs (junior drafts, check-in briefs, intervention plans) that were
already auto-approved or auto-routed by the system.

For each item, provide:
- agree_with_system: yes/no
- if no: what the system should have flagged and which evaluation check or
  quality standard (QS001-QS006, or one of the 4 structural checks) should
  be tightened to catch this case in future

Sampled items: {sampled_outputs_with_system_decisions}

Summarize patterns across the sample, not just per-item verdicts -- the
goal is identifying systematic gaps in the automated checks, not relitigating
individual decisions.
```

## Output shape

```
QA sample {date}: {n} items reviewed, {k} disagreements.
Disagreement summary: {pattern_description}
Recommended check/standard updates: {list}
```

## Notes

- This is the stage that should surface recalibration needs for the
  risk/opportunity scoring weights and QS001-QS006 heuristics referenced in
  the README's assumptions section -- it is the feedback loop, not a
  one-time check.
- Distinct from `outputs/evaluation_failures.json`, which logs *structural*
  check failures (see Priority 3 / README "Failure handling" section), not
  sampled judgment QA.
