# AI Workflow Template

Use this to design a single end-to-end AI-driven process (e.g. "AI grading triage," "at-risk student detection," "parent communication drafting").

## 1. Trigger

What starts the workflow? (scheduled job, event like "quiz submitted," user request)

## 2. Step-by-Step Flow

| Step | Actor (AI/Human/System) | Input | Action | Output | Failure handling |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

## 3. Prompt/Logic Spec (for the AI steps)

For each AI step, specify:
- **Context provided:** exactly what data goes into the prompt/context window.
- **Task instruction:** the actual ask, in plain language.
- **Output format:** structured (JSON/schema) vs. free text — structured almost always wins for downstream automation.
- **Guardrails:** what the model must NOT do (e.g. never state a final grade without rubric citation).

## 4. Human Oversight Point(s)

- Where does a human review before action is taken?
- What does the human see (full context, or just AI's summary + confidence)?
- What's the SLA for human review (so the workflow doesn't stall)?

## 5. Exception Paths

- Low-confidence output -> ?
- Missing/incomplete input data -> ?
- Conflicting signals (e.g. high grades but high absence) -> ?
- Student/parent disputes AI decision -> ?

## 6. Feedback Loop

- How do outcomes (did the intervention work?) get captured and routed back to improve the workflow (prompt tuning, retraining, threshold adjustment)?

## 7. Example Workflows to Practice On

1. AI-assisted essay feedback (formative, not final grade)
2. Early-warning at-risk student flagging from attendance + grades + engagement
3. Personalized curriculum pacing recommendation
4. Auto-drafted parent progress-update emails (human approves before send)
5. Tutoring chatbot escalation to human tutor
6. Course-scheduling/conflict resolution recommendation engine
