# Cost Modeling Template

Crossover assessments often probe whether you can reason about unit economics, not just architecture. Always express cost **per student per month** and **at scale** (e.g. 10k, 100k students).

## 1. Cost Components

| Component | Driver | Formula | Notes |
|---|---|---|---|
| LLM inference | tokens/call x calls/student/month | `(input_tokens + output_tokens) x price_per_1k x calls` | Separate input/output pricing; cache repeated context |
| Embeddings/RAG | docs indexed + queries | `index_cost (one-time) + query_cost x queries/month` | |
| Vector DB / storage | GB stored, query volume | vendor pricing tiers | |
| Human review labor | reviews/month x minutes x hourly rate | `reviews x (minutes/60) x rate` | This is often the dominant cost, not the model |
| Infra (orchestration, hosting) | requests/sec, compute | | |
| Third-party tools (SIS integration, comms platform) | per-seat or per-API-call | | |
| Compliance/security overhead | audits, logging storage | | |

## 2. Worked Example Skeleton

Assume: 10,000 students, 1 AI interaction/student/day, average 800 input + 300 output tokens, model price $X/1M input, $Y/1M output tokens.

```
Daily calls          = 10,000
Monthly calls         = 10,000 x 30 = 300,000
Input tokens/mo       = 300,000 x 800 = 240,000,000
Output tokens/mo      = 300,000 x 300 = 90,000,000
Inference cost/mo     = (240M/1M x $X) + (90M/1M x $Y)
Cost per student/mo   = Inference cost/mo / 10,000
```

Fill in real pricing for the model you'd choose (state assumptions explicitly — graders expect you to show the formula even if pricing is approximate).

## 3. Human-in-the-Loop Cost

```
Reviews needed/mo     = % of AI outputs requiring human review x monthly calls
Reviewer cost/mo      = Reviews x avg_review_minutes/60 x hourly_rate
```

This is frequently the line item that makes or breaks ROI — call it out explicitly.

## 4. Cost vs. Baseline (build the business case)

| | Current (manual) process | Proposed AI-assisted process |
|---|---|---|
| Cost per student/month | | |
| Staff hours/month | | |
| Turnaround time | | |
| Error/quality rate | | |

## 5. Scaling Sensitivity

State how cost scales as student count grows 10x:
- Linear costs (inference, per-call): scale directly.
- Fixed costs (infra, integration, one-time indexing): amortize, decreasing cost-per-student.
- Step-function costs (need more reviewers at some threshold): call out the threshold.

## 6. Cost Levers (be ready to defend trade-offs)

- Smaller/cheaper model for triage, larger model only for escalated cases (cascade architecture).
- Caching/batching to cut redundant calls.
- Reducing context size (RAG retrieval vs. full document dump).
- Async/batch processing instead of real-time where latency tolerates it.
- Raising/lowering the human-review threshold (cost vs. risk trade-off — tie back to Risk Assessment doc).
