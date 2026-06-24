# Session Log — AI System Design Assessment

This log documents how Claude Code was used to build the Customer Success
AI Workflow Simulation (`cs_workflow_simulation/`) and its supporting
deliverables for the Crossover AI System Design Assessment, plus the
secondary tools and review process used alongside it.

## Tools used

- **Claude Code** (this session) — primary build tool for the runnable
  Python simulation, the Token Math Sheet (via `openpyxl`), the prompt
  templates, README documentation, and this log.
- **ChatGPT** — used as a secondary planning and review tool outside this
  session: for early brainstorming on workflow stage breakdown and for a
  second pass sanity-check on the token-math approach (cadence
  annualization, measured-vs-scaled framing) before finalizing the
  spreadsheet in Claude Code.

## Major prompts issued to Claude Code (this session, summarized)

1. Line-by-line review of an in-progress Token Math Sheet: asked to flag
   missing workflow stages, unrealistic token assumptions, incorrect
   annualization, budget inconsistencies, weak model routing, and anything
   an evaluator could challenge.
2. Build the Token Math Sheet from `token_cost_summary.csv` measured
   values across 8 operating areas, with cost-per-run/day/month/year,
   documented and flagged assumptions, and a self-review pass.
3. Full pre-submission audit against the actual assignment PDF (10-point
   checklist: required workflow areas, Token Math Sheet completeness,
   README setup/scale explanation, 24/7 responsiveness, prompt templates,
   5 end-to-end runs, token/cost measurement, evaluation/failure handling,
   session log requirements, submission readiness).
4. Rebuild the Token Math Sheet on the assignment's actual 750-account
   production scope (30 tickets/week, 12 check-ins/week, biweekly
   interventions), using the 18-account simulation strictly as the
   measured per-run baseline, with explicit measured/scaled/assumption
   labeling throughout.
5. A 5-priority, ordered build-out: (1) confirm the 750-account base case,
   (2) add 9 prompt templates without converting the deterministic
   workflow to live LLM calls, plus README updates explaining the
   deterministic-vs-production-prompt split and the 750-account scale,
   (3) add evaluation failure-handling (code + docs), (4) write this
   session log, (5) re-run the workflow, final-audit, commit, and push.

## Files created or modified this session

- `cs_workflow_simulation/prompts/memory_retrieval_prompt.md` (new)
- `cs_workflow_simulation/prompts/account_monitoring_prompt.md` (new)
- `cs_workflow_simulation/prompts/prioritization_prompt.md` (new)
- `cs_workflow_simulation/prompts/inbound_issue_routing_prompt.md` (new)
- `cs_workflow_simulation/prompts/checkin_preparation_prompt.md` (new)
- `cs_workflow_simulation/prompts/output_quality_review_prompt.md` (new)
- `cs_workflow_simulation/prompts/intervention_planning_prompt.md` (new)
- `cs_workflow_simulation/prompts/escalation_prompt.md` (new)
- `cs_workflow_simulation/prompts/evaluation_qa_prompt.md` (new)
- `cs_workflow_simulation/workflow.py` (modified) — added
  `REMEDIATION_ROUTES` and `write_evaluation_failures()`, wired into
  `main()` to write `outputs/evaluation_failures.json` every run, plus a
  console summary line when failures exist.
- `cs_workflow_simulation/README.md` (modified) — added "Scale: 18-account
  demo vs. 750-account production scope," "24/7 responsiveness,"
  "Prompt templates," and "Failure handling" sections; added
  `evaluation_failures.json` to the output files list.
- `cs_workflow_simulation/outputs/Token_Math_Sheet_Completed.xlsx`
  (rebuilt, prior turn) — 750-account production base case, Scenario
  Analysis (Base/Stress/Optimized), and a rewritten Candidate Assumptions
  tab using the Measured / Scaled estimate / Assumption framework.
- `session_log.md` (this file, new).

## Errors and issues found, and how they were resolved

- **Wrong base-case scale.** The first Token Math Sheet pass scaled off
  the 18-account demo dataset directly instead of the assignment's actual
  750-account production scope, burying the real-scale numbers in a
  "Scaled scenario" instead of the base case. Caught during the
  pre-submission audit against the assignment PDF, not by the user
  pointing it out first. Fixed by rebuilding the base case at 750
  accounts / 30 tickets-week / 12 check-ins-week / biweekly interventions,
  keeping the 18-account run strictly as the measured per-run source.
- **Operating-area naming mismatch.** The user's requested 8 operating
  areas, the simulation's CSV stage names, and the spreadsheet template's
  own built-in coverage checklist used three different naming
  conventions that didn't map 1:1 to each other (e.g. "Support Triage" vs.
  "Inbound issue handling"; the template's checklist omits "Memory &
  retrieval" and "Evaluation/QA" as named rows). Resolved by using the
  union of all three — 9 data rows total — so no measured data was
  dropped and the template's own checklist could still be satisfied.
- **LibreOffice headless formula verification failed.** Attempted to
  recalculate the `.xlsx` via `soffice --headless --convert-to` to verify
  formula correctness; it failed with "source file could not be loaded"
  even against the original, unmodified template, confirming an
  environment limitation rather than a corruption introduced by edits.
  Worked around by independently re-implementing the same lookup/pricing
  math in a standalone Python script and hand-verifying the totals
  ($223.27/year, 0.4465% utilization) against what the Excel formulas
  should compute.
- **No failure-handling path existed.** `run_evaluation_checks()` only
  printed PASS/FAIL to console; nothing captured a failure for downstream
  remediation. Addressed by adding `write_evaluation_failures()`, which
  writes `outputs/evaluation_failures.json` with a recommended
  remediation route per check type, every run (empty list when all
  checks pass, as they currently do on this dataset).

## Debugging steps taken

- Re-read `workflow.py` in full before writing prompt templates, to
  ground every template's input/output fields in the actual function
  signatures and data structures rather than guessing at field names.
- Re-ran `python3 workflow.py` after the failure-handling change to
  confirm all 4 evaluation checks still pass and that
  `evaluation_failures.json` is written correctly (empty failures list,
  valid JSON) without altering any other output file's contents.
- Cross-checked the Token Math Sheet's per-row notes against
  `token_cost_summary.csv` to ensure every "Measured" label actually
  traces to a real simulation output column, not an assumed number.

## Outputs accepted, revised, or rejected

- **Rejected:** the first Token Math Sheet build (18-account-scale base
  case) — superseded once the scale error was caught; not used in the
  final submission.
- **Accepted with no changes:** the deterministic workflow logic itself
  (`workflow.py` stage functions, scoring formulas, quality-standard
  checks) — kept exactly as originally designed; only additive changes
  (failure-handling) were made, no rule logic was altered.
- **Revised:** README.md, expanded across this session to explain scale,
  24/7 responsiveness, the prompt-template split, and failure handling —
  none of these sections existed before the pre-submission audit
  identified them as gaps.
- **Accepted:** all 9 prompt templates as drafted in this session, each
  reviewed against the corresponding stage function's actual fields
  before being finalized.

## Notes

- ChatGPT was used as a secondary planning and review tool for early
  workflow-stage brainstorming and a sanity check on the token-math
  framing, outside of this Claude Code session; all code, spreadsheet
  formulas, and documentation in this repository were produced and
  verified in Claude Code.
- Submission packaging (uploading the completed Token Math Sheet to the
  assessment's required Google Sheet/Doc format and generating shareable
  links) is outside what this environment can do directly and remains a
  manual step for the candidate after pulling these files locally.
