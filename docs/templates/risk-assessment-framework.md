# Risk Assessment Framework

## 1. Risk Register Table

| Risk | Category | Likelihood (L/M/H) | Impact (L/M/H) | Mitigation | Owner |
|---|---|---|---|---|---|
| Model gives factually wrong academic content | Quality | | | RAG grounding + citation requirement + human spot-check | |
| Model produces biased recommendation (e.g. under-flags ELL students as at-risk) | Fairness | | | Subgroup eval, fairness audit cadence | |
| Student PII exposed via prompt/logging | Privacy/Security | | | PII redaction, least-privilege logging, encryption at rest | |
| Over-automation causes missed at-risk student (false negative on safety) | Safety | | | Conservative threshold + mandatory human review for safety-adjacent flags | |
| Parent/student distrust of AI-driven decision | Trust/Adoption | | | Transparency: explain AI's role, always allow human appeal | |
| Vendor/model outage disrupts instruction | Availability | | | Fallback to cached/rules-based path, SLA with vendor | |
| Cost overrun at scale | Financial | | | Cost modeling sensitivity analysis, usage caps/alerts | |
| Regulatory non-compliance (FERPA/COPPA/state law) | Compliance | | | Legal review before pilot, data minimization | |
| Model drift over time (curriculum changes, model updates) | Quality | | | Scheduled re-evaluation, version pinning | |
| Academic integrity (students using AI tutor to cheat) | Misuse | | | Usage policy, output design discourages direct answer-giving | |

## 2. Categories to Always Cover

1. **Quality/Accuracy** — hallucination, wrong grading, bad recommendations.
2. **Fairness/Bias** — disparate impact on protected/vulnerable groups (IEP/504, ELL, low-income, race).
3. **Privacy/Security** — student data (FERPA), under-13 data (COPPA), breach exposure.
4. **Safety** — self-harm/abuse disclosures, mandatory-reporting triggers — these must route to humans, always.
5. **Trust/Adoption** — will teachers/parents/students actually use and believe the system?
6. **Operational/Availability** — what breaks the workflow, and what's the fallback?
7. **Financial** — cost overrun, vendor lock-in, pricing changes.
8. **Compliance/Legal** — education-sector-specific regulation, accessibility (ADA/Section 508).
9. **Misuse/Academic Integrity** — gaming the system, cheating, prompt injection by students.

## 3. Risk Scoring

`Risk Score = Likelihood x Impact` (use a simple 1-3 scale each, 9-point matrix). Anything scoring 6+ requires a documented mitigation before pilot approval, not just "monitor it."

## 4. Human Oversight as a Risk Control

State explicitly, per risk: is the mitigation **preventive** (stops it happening — e.g. won't act without grounding), **detective** (catches it after — e.g. audit log review), or **corrective** (fixes it after the fact — e.g. appeal process)? Assessments reward this distinction.

## 5. Red Lines (non-negotiable, never automate)

- Final grade/credit decisions without human sign-off.
- Disciplinary or expulsion actions.
- Safety/mandatory-reporting disclosures — always route to a designated human immediately.
- Any action that cannot be reversed or appealed.
