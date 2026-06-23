# System Architecture Template

Use this for any "design an AI system for X academic process" prompt. Fill every section — blank sections read as gaps in a timed assessment.

## 1. Problem Framing

- **Business problem:** what operational pain point, in one sentence.
- **Why AI (not just software):** what judgment/scale/pattern-recognition does this need that a deterministic workflow can't give?
- **Scope boundary:** explicitly state what's OUT of scope.

## 2. Actors & Data Sources

| Actor | Role | Data they provide | Data they consume |
|---|---|---|---|
| Student | | | |
| Instructor | | | |
| Parent/Guardian | | | |
| Ops/Admin staff | | | |
| AI System | | | |

**Upstream systems:** SIS/LMS (e.g. Canvas, PowerSchool), gradebook, attendance, comms platform, payment/billing.

## 3. High-Level Architecture (layers)

```
[Data Sources] -> [Ingestion/ETL] -> [Feature/Context Store] -> [AI Orchestration Layer]
                                                                       |
                          +--------------------------------------------+
                          |                  |                  |
                     [LLM/Model calls]  [Rules engine]    [Retrieval/RAG]
                          |
                  [Human-in-the-loop gate] -> [Action layer: write to SIS, send comms, flag]
                          |
                     [Observability: logging, eval, audit trail]
```

- **Ingestion:** batch vs. event-driven? Latency requirement?
- **Orchestration:** single LLM call vs. multi-agent pipeline vs. workflow engine (state machine).
- **Retrieval:** what's the knowledge base (curriculum docs, policy handbook, student history)? Vector DB or structured query?
- **Action layer:** what can the system do autonomously vs. must propose for approval?
- **Audit trail:** every AI decision logged with input, output, confidence, and human override status.

## 4. Model & Tooling Choices

| Decision | Choice | Why |
|---|---|---|
| Model tier (e.g. small/fast vs. large/reasoning) | | |
| Fine-tuned vs. prompted | | |
| RAG vs. long-context vs. fine-tune | | |
| Synchronous vs. async/batch | | |
| Build vs. buy (vendor tutoring tool, etc.) | | |

## 5. Human-in-the-Loop Design

- **Autonomous actions** (no review needed): low-stakes, reversible, high-confidence.
- **Human-reviewed actions** (AI proposes, human approves): medium-stakes or borderline confidence.
- **Human-only actions** (AI flags, never acts): high-stakes — expulsion, grade changes, safety concerns, legal/compliance.
- **Escalation triggers:** confidence threshold, sentiment/safety keyword, repeated failure, student request.

## 6. Non-Functional Requirements

- **Latency:** real-time chat vs. overnight batch report.
- **Availability:** does downtime block instruction?
- **Privacy/Compliance:** FERPA (US K-12/higher-ed), COPPA (under-13), state student-data laws, data residency.
- **Security:** PII handling, model access to gradebook/SIS, least-privilege API keys.
- **Auditability:** can you reconstruct why the AI made a recommendation 6 months later?

## 7. Failure Modes & Degradation

- What happens when the model is down / rate-limited / hallucinates?
- Fallback path (cached answer, route to human, deterministic rule).
- Bias/fairness check: does the system perform worse for any subgroup (ELL, IEP/504, low-bandwidth households)?

## 8. Diagram Checklist (for whiteboard/diagram deliverables)

- [ ] Data sources labeled with system names, not generic boxes
- [ ] Arrows show direction and data type (not just "flow")
- [ ] Human checkpoints explicitly drawn, not implied
- [ ] At least one feedback loop (outcome data -> model/prompt improvement)
