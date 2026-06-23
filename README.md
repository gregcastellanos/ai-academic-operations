# AI Academic Operations

Repository for designing, documenting, and prototyping AI-powered academic operations systems.

## Objectives

- Improve student outcomes
- Reduce operational overhead
- Scale personalized learning
- Use AI for routine academic operations
- Use humans for oversight and exceptions

## Core Metrics

- Mastery Rate
- Time to Mastery
- Completion Rate
- Engagement
- Cost Per Student
- Intervention Success Rate

## System Components

- AI Tutor
- Curriculum Generator
- Student Risk Detection
- Parent Communication
- Academic Dashboard

## Assessment Prep Templates

For the Crossover AI System Design Assessment (Head of Academics), use these in order:

1. [`docs/templates/system-architecture-template.md`](docs/templates/system-architecture-template.md) — overall system design
2. [`docs/templates/ai-workflow-template.md`](docs/templates/ai-workflow-template.md) — single end-to-end AI process
3. [`docs/templates/cost-modeling-template.md`](docs/templates/cost-modeling-template.md) — unit economics, scaling sensitivity
4. [`docs/templates/risk-assessment-framework.md`](docs/templates/risk-assessment-framework.md) — risk register, red lines
5. [`docs/templates/implementation-plan-template.md`](docs/templates/implementation-plan-template.md) — phased rollout
6. [`docs/templates/kpi-dashboard-template.md`](docs/templates/kpi-dashboard-template.md) — metric tree, North Star vs. guardrails

Worked examples tying all six together:
- [`docs/examples/worked-example-at-risk-detection.md`](docs/examples/worked-example-at-risk-detection.md) — early-warning at-risk student detection
- [`docs/examples/worked-example-academic-coaching.md`](docs/examples/worked-example-academic-coaching.md) — AI-powered coaching system that reduces human intervention while improving outcomes

Legacy blank templates ([`docs/system-design-template.md`](docs/system-design-template.md), [`docs/implementation-plan.md`](docs/implementation-plan.md), [`docs/assessment-notes.md`](docs/assessment-notes.md)) are kept as quick fill-in-the-blank checklists for use during the timed assessment itself.

## Runnable Workflow Simulation

[`cs_workflow_simulation/`](cs_workflow_simulation/) is a separate, runnable deliverable for the assessment's B2B SaaS customer success scenario — a single-command Python simulation covering all 8 workflow stages (memory/context retrieval, account review, prioritization, issue routing, check-in prep, output quality review, intervention planning, escalation routing) over the provided dataset, with a token/cost summary shaped to drop directly into the assessment's Token Math Sheet. See its own README for setup, stage-by-stage explanation, and assumptions.
