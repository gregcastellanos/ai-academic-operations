# Educational KPI Dashboard Template

## 1. Metric Tree

Organize metrics by what they answer:

- **Are students learning?** -> Mastery Rate, Time to Mastery, Assessment Score Trend
- **Are students staying engaged/enrolled?** -> Completion Rate, Engagement (logins, time-on-task), Attrition/Churn Rate
- **Is the AI system working as intended?** -> AI Accuracy/Quality Score, Human Override Rate, Escalation Rate, Latency
- **Is it cost-effective?** -> Cost Per Student, Cost Per Intervention, Staff Hours Saved
- **Is it safe and fair?** -> Intervention Success Rate, Subgroup Performance Gap, Safety-Flag Response Time

## 2. KPI Definitions Table

| KPI | Definition | Formula | Target | Data source | Refresh cadence |
|---|---|---|---|---|---|
| Mastery Rate | % of students meeting mastery threshold on a skill/unit | `mastered_students / total_students` | | Assessment/LMS | Weekly |
| Time to Mastery | Avg. time from first exposure to mastery | `sum(time_to_mastery) / n` | | LMS event logs | Weekly |
| Completion Rate | % of enrolled students completing course/module | `completed / enrolled` | | SIS/LMS | Weekly |
| Engagement | Composite of logins, time-on-task, submissions | weighted index | | LMS | Daily |
| Cost Per Student | Total system cost / active students | `total_cost / active_students` | | Cost model | Monthly |
| Intervention Success Rate | % of AI-flagged at-risk students who improve post-intervention | `improved / flagged` | | SIS + outcome tracking | Monthly |
| AI Accuracy/Quality Score | Human-graded correctness of AI outputs (sampled) | `correct / sampled` | | Eval pipeline | Weekly |
| Human Override Rate | % of AI recommendations overridden by humans | `overridden / total_recommendations` | | Audit log | Weekly |
| Escalation Rate | % of interactions escalated to human | `escalated / total_interactions` | | Workflow logs | Weekly |
| Subgroup Performance Gap | Difference in outcome metric across student subgroups | `metric_groupA - metric_groupB` | trend toward 0 | SIS + demographic data | Quarterly |
| Safety-Flag Response Time | Time from safety flag to human acknowledgment | `ack_time - flag_time` | < target (e.g. 15 min) | Workflow logs | Real-time/daily |

## 3. Dashboard Layout Sketch

```
+--------------------------------------------------------------+
|  Header: cohort selector, date range, [Overall Health: G/Y/R]|
+----------------------+----------------------+----------------+
| Learning Outcomes    | Engagement/Retention  | Cost           |
| - Mastery Rate       | - Completion Rate     | - Cost/Student |
| - Time to Mastery    | - Engagement Index    | - Cost/Interv. |
| - Score Trend (line) | - Attrition (line)    | - Trend (line) |
+----------------------+----------------------+----------------+
| AI System Health                     | Risk & Fairness        |
| - Override Rate (gauge)              | - Subgroup Gap (bar)   |
| - Escalation Rate (gauge)            | - Safety Response Time |
| - Accuracy/Quality (trend)           | - Open incidents count |
+---------------------------------------+-------------------------+
```

## 4. North Star vs. Guardrail Metrics

State this distinction explicitly in any assessment answer:
- **North Star** (the metric the system optimizes for): e.g. Mastery Rate or Time to Mastery.
- **Guardrail metrics** (must not regress while optimizing North Star): Cost Per Student, Subgroup Gap, Override Rate. An AI system that improves the North Star metric while quietly worsening a guardrail metric is a failed design — call this out.

## 5. Alerting Thresholds

| Metric | Yellow alert | Red alert | Action |
|---|---|---|---|
| Override Rate | > 20% | > 40% | Review prompts/model, possible rollback |
| Subgroup Gap | widening trend | > X pts gap | Fairness audit |
| Safety Response Time | > 15 min | > 1 hr | Escalate to ops lead immediately |
| Cost Per Student | > 110% of budget | > 130% | Trigger cost-lever review |
