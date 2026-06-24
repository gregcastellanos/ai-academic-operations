"""
End-to-end Customer Success AI workflow simulation.

This is a deterministic simulation, not a live LLM integration. It models what
each stage of an AI-assisted CS workflow would receive as input and produce as
output, and estimates the token/cost footprint of running each stage with a
specific model. The routing logic (risk scoring, ticket routing, quality
checks) is implemented as transparent rule-based heuristics so the workflow
is reviewable line-by-line. In production, the "Output quality review" and
"Targeted intervention planning" stages are the ones most likely to actually
call an LLM (as a judge / as a drafting assistant); the others are good
candidates for a cheap model or even pure rules once the heuristics are
validated against real LLM output.

Run with: python3 workflow.py
"""

import csv
import json
import os
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "outputs")

# ---------------------------------------------------------------------------
# Pricing constants (USD per 1,000,000 tokens). Mirrors the Pricing Reference
# tab of the Token Math Sheet (effective 2026-05-17) so numbers transfer
# directly without re-deriving them.
# ---------------------------------------------------------------------------
MODEL_PRICING = {
    "Claude Haiku 4.5": {"input": 1.00, "output": 5.00},
    "Claude Sonnet 4.6": {"input": 3.00, "output": 15.00},
    "Claude Opus 4.7": {"input": 5.00, "output": 25.00},
    "GPT-5.4 mini": {"input": 0.75, "output": 4.50},
    "text-embedding-3-small": {"input": 0.02, "output": 0.00},
}

CHARS_PER_TOKEN = 4  # standard rule-of-thumb estimate (tokens ~= chars / 4)

# Model routing per workflow stage: cheap model for high-volume/simple work,
# stronger models reserved for judgment-heavy or escalation-heavy stages.
STAGE_MODEL = {
    "Memory & retrieval": "text-embedding-3-small",
    "Account monitoring": "Claude Haiku 4.5",
    "Prioritization": "Claude Haiku 4.5",
    "Inbound issue handling": "Claude Sonnet 4.6",
    "Customer check-in support": "Claude Sonnet 4.6",
    "Output quality review": "GPT-5.4 mini",
    "Targeted intervention planning": "Claude Sonnet 4.6",
    "24/7 responsiveness / escalation": "Claude Opus 4.7",
}

# The 5 accounts with full coverage across every input file, used to
# demonstrate complete end-to-end runs (all 7 stages, one account at a time).
DEMO_ACCOUNTS = ["A008", "A005", "A014", "A010", "A017"]


def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def estimate_tokens(text):
    return max(1, len(text) // CHARS_PER_TOKEN)


class TokenLedger:
    """Accumulates input/output text per workflow stage for cost estimation."""

    def __init__(self):
        self.records = []

    def log(self, stage, input_text, output_text):
        model = STAGE_MODEL[stage]
        price = MODEL_PRICING[model]
        in_tok = estimate_tokens(input_text)
        out_tok = estimate_tokens(output_text)
        cost = (in_tok / 1_000_000) * price["input"] + (out_tok / 1_000_000) * price["output"]
        self.records.append(
            {
                "stage": stage,
                "model": model,
                "input_tokens_estimate": in_tok,
                "output_tokens_estimate": out_tok,
                "estimated_cost": round(cost, 6),
            }
        )

    def summary_by_stage(self):
        agg = defaultdict(lambda: {"runs": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0})
        for r in self.records:
            a = agg[r["stage"]]
            a["runs"] += 1
            a["input_tokens"] += r["input_tokens_estimate"]
            a["output_tokens"] += r["output_tokens_estimate"]
            a["cost"] += r["estimated_cost"]
        return agg


ledger = TokenLedger()


# ---------------------------------------------------------------------------
# Stage 0: Memory & context retrieval
# ---------------------------------------------------------------------------
def latest_usage_by_account(usage_events):
    latest = {}
    for ev in usage_events:
        acct = ev["account_id"]
        if acct not in latest or ev["event_date"] > latest[acct]["event_date"]:
            latest[acct] = ev
    return latest


def memory_context_retrieval(accounts, call_notes_by_account, tickets_by_account, usage_events, checkins):
    """Assemble a concise per-account memory packet from every available source
    (account profile, call history, support history, usage trend, next
    check-in) before any other stage runs. This is the retrieval step a RAG
    pipeline would normally do via vector search; here, with a small fixed
    dataset, a direct per-account lookup is the simpler and equally correct
    way to assemble the same context."""
    latest_usage = latest_usage_by_account(usage_events)
    next_checkin_by_account = {}
    for c in checkins:
        acct = c["account_id"]
        if acct not in next_checkin_by_account or c["scheduled_date"] < next_checkin_by_account[acct]["scheduled_date"]:
            next_checkin_by_account[acct] = c

    packets = []
    for acct in accounts:
        acct_id = acct["account_id"]
        notes = call_notes_by_account.get(acct_id, [])
        last_note = notes[-1] if notes else None
        open_tix = [t for t in tickets_by_account.get(acct_id, []) if t["current_status"] != "closed"]
        usage = latest_usage.get(acct_id)
        next_checkin = next_checkin_by_account.get(acct_id)

        memory_packet = (
            f"{acct['account_name']} ({acct['segment']}, ${acct['contract_value']} ACV, renews {acct['renewal_date']}). "
            f"Health {acct['current_health_score']} (was {acct['previous_health_score']}). "
            f"Usage trend: {usage['usage_trend'] if usage else acct['product_usage_trend']}. "
            + (f"Last call: {last_note['summary']} - goal: {last_note['customer_goal']}, blocker: {last_note['risk_or_blocker']}, follow-up: {last_note['follow_up_items']}. "
               if last_note else "No prior call notes. ")
            + (f"{len(open_tix)} open ticket(s): {'; '.join(t['issue_summary'] for t in open_tix)}. " if open_tix else "No open tickets. ")
            + (f"Next check-in {next_checkin['scheduled_date']}: {next_checkin['checkin_type']}." if next_checkin else "No check-in scheduled.")
        )

        packet = {
            "account_id": acct_id,
            "account_name": acct["account_name"],
            "open_ticket_count": len(open_tix),
            "last_call_date": last_note["call_date"] if last_note else "",
            "last_call_followup": last_note["follow_up_items"] if last_note else "",
            "usage_trend": usage["usage_trend"] if usage else acct["product_usage_trend"],
            "next_checkin_date": next_checkin["scheduled_date"] if next_checkin else "",
            "memory_packet": memory_packet,
        }
        packets.append(packet)

        ledger.log(
            "Memory & retrieval",
            input_text=json.dumps(acct) + json.dumps(notes) + json.dumps(open_tix) + json.dumps(usage or {}) + json.dumps(next_checkin or {}),
            output_text=memory_packet,
        )
    return packets


# ---------------------------------------------------------------------------
# Stage 1: Daily account review
# ---------------------------------------------------------------------------
USAGE_TREND_WEIGHT = {"declining": 2, "flat": 1, "growing": 0}
EXPANSION_WEIGHT = {"high": 2, "medium": 1, "low": 0}


def daily_account_review(accounts, usage_events):
    """Pull the latest signals together per account. This is the lightweight,
    high-volume stage that runs every business day across the full portfolio."""
    latest_usage = {}
    for ev in usage_events:
        acct = ev["account_id"]
        if acct not in latest_usage or ev["event_date"] > latest_usage[acct]["event_date"]:
            latest_usage[acct] = ev

    reviewed = []
    for acct in accounts:
        acct_id = acct["account_id"]
        usage = latest_usage.get(acct_id)
        trend = usage["usage_trend"] if usage else acct["product_usage_trend"]
        notable_change = usage["notable_change"] if usage else ""
        health_delta = int(acct["previous_health_score"]) - int(acct["current_health_score"])

        record = {
            "account_id": acct_id,
            "account_name": acct["account_name"],
            "csm_owner": acct["csm_owner"],
            "health_delta": health_delta,
            "current_health_score": int(acct["current_health_score"]),
            "usage_trend": trend,
            "notable_change": notable_change,
            "nps_score": int(acct["nps_score"]),
            "expansion_signal": acct["expansion_signal"],
            "support_ticket_count_30d": int(acct["support_ticket_count_30d"]),
        }
        reviewed.append(record)

        ledger.log(
            "Account monitoring",
            input_text=json.dumps(acct) + json.dumps(usage or {}),
            output_text=json.dumps(record),
        )
    return reviewed


# ---------------------------------------------------------------------------
# Stage 2: Account prioritization
# ---------------------------------------------------------------------------
def account_prioritization(reviewed, tickets):
    """Rank accounts into Urgent / Watch / Expansion / Stable using a
    transparent weighted score, not a black-box model call."""
    open_high_sev = defaultdict(bool)
    for t in tickets:
        if t["severity"] == "High" and t["current_status"] != "closed":
            open_high_sev[t["account_id"]] = True

    prioritized = []
    for r in reviewed:
        usage_weight = USAGE_TREND_WEIGHT.get(r["usage_trend"], 1)
        expansion_weight = EXPANSION_WEIGHT.get(r["expansion_signal"], 0)
        nps_risk = max(0, 7 - r["nps_score"])

        risk_score = (
            max(0, r["health_delta"]) * 2
            + usage_weight * 6
            + r["support_ticket_count_30d"] * 2
            + nps_risk * 2
        )
        opportunity_score = expansion_weight * 10 + max(0, r["current_health_score"] - 75) + max(0, r["nps_score"] - 7) * 3

        if open_high_sev[r["account_id"]] or risk_score >= 30:
            tier = "Urgent"
        elif risk_score >= 15:
            tier = "Watch"
        elif opportunity_score >= 20 and risk_score < 10:
            tier = "Expansion"
        else:
            tier = "Stable"

        rec = dict(r)
        rec.update(
            {
                "risk_score": risk_score,
                "opportunity_score": opportunity_score,
                "priority_tier": tier,
                "has_open_high_severity_ticket": open_high_sev[r["account_id"]],
            }
        )
        prioritized.append(rec)

        ledger.log(
            "Prioritization",
            input_text=json.dumps(r),
            output_text=json.dumps({"priority_tier": tier, "risk_score": risk_score}),
        )

    prioritized.sort(key=lambda x: (-x["risk_score"], -x["opportunity_score"]))
    return prioritized


# ---------------------------------------------------------------------------
# Stage 3: Inbound support issue routing
# ---------------------------------------------------------------------------
def route_ticket(ticket, tier_by_account):
    sev = ticket["severity"]
    tier = tier_by_account.get(ticket["account_id"], "Stable")

    if sev == "High":
        route = "escalation"
        reason = "High-severity ticket always escalates regardless of account tier."
    elif sev == "Medium":
        if tier in ("Urgent", "Watch"):
            route = "escalation"
            reason = f"Medium-severity ticket on a {tier} account escalates due to compounding risk."
        else:
            route = "standard_resolution"
            reason = "Medium-severity ticket on a stable/expansion account handled by standard queue."
    else:  # Low
        if ticket["customer_sentiment"] in ("positive", "neutral"):
            route = "immediate_resolution"
            reason = "Low-severity, non-negative sentiment ticket resolved immediately by frontline/AI draft."
        else:
            route = "standard_resolution"
            reason = "Low-severity but negative sentiment ticket routed to standard queue for a human read."
    return route, reason


def inbound_support_issue_routing(tickets, tier_by_account):
    routed = []
    for t in tickets:
        route, reason = route_ticket(t, tier_by_account)
        rec = {
            "ticket_id": t["ticket_id"],
            "account_id": t["account_id"],
            "severity": t["severity"],
            "customer_sentiment": t["customer_sentiment"],
            "account_priority_tier": tier_by_account.get(t["account_id"], "Stable"),
            "route": route,
            "routing_reason": reason,
            "issue_summary": t["issue_summary"],
        }
        routed.append(rec)
        ledger.log(
            "Inbound issue handling",
            input_text=json.dumps(t),
            output_text=json.dumps({"route": route, "reason": reason}),
        )
    return routed


# ---------------------------------------------------------------------------
# Stage 4: Customer check-in preparation
# ---------------------------------------------------------------------------
def customer_checkin_preparation(checkins, accounts_by_id, call_notes_by_account, tickets_by_account, tier_by_account, memory_packets_by_account):
    briefs = []
    for c in checkins:
        acct_id = c["account_id"]
        acct = accounts_by_id.get(acct_id, {})
        notes = call_notes_by_account.get(acct_id, [])
        last_note = notes[-1] if notes else None
        open_tix = [t for t in tickets_by_account.get(acct_id, []) if t["current_status"] != "closed"]
        memory = memory_packets_by_account.get(acct_id)

        prior_context = (
            f"[Retrieved memory] {memory['memory_packet']}"
            if memory
            else "No prior call notes on file."
        )
        next_steps = (
            f"Confirm status of: {last_note['follow_up_items']}." if last_note else "Establish baseline goal and owner."
        )
        if open_tix:
            next_steps += " Address open ticket(s): " + "; ".join(t["issue_summary"] for t in open_tix) + "."

        brief = {
            "checkin_id": c["checkin_id"],
            "account_id": acct_id,
            "account_name": acct.get("account_name", ""),
            "priority": c["priority"],
            "checkin_type": c["checkin_type"],
            "scheduled_date": c["scheduled_date"],
            "topics_to_cover": c["topics_to_cover"],
            "account_priority_tier": tier_by_account.get(acct_id, "Stable"),
            "prior_context": prior_context,
            "next_steps": next_steps,
        }
        briefs.append(brief)

        ledger.log(
            "Customer check-in support",
            input_text=json.dumps(c) + (json.dumps(last_note) if last_note else "") + json.dumps(open_tix),
            output_text=prior_context + next_steps,
        )
    return briefs


# ---------------------------------------------------------------------------
# Stage 5: Customer-facing output quality review
# ---------------------------------------------------------------------------
ACTION_WORDS = ["will ", "by ", "schedule", "plan", "confirm", "send", "share", "provide", "draft", "escalate", "investigate"]
VAGUE_WORDS = ["soon", "sometime", "probably", "we think", "let us know if"]
OVERSTATE_WORDS = ["churn", "immediately", "urgent crisis"]
ESCALATION_WORDS = ["escalate", "specialist", "executive", "priority response"]


def _overlap(a, b):
    sa = set(w.strip(".,").lower() for w in a.split() if len(w) > 4)
    sb = set(w.strip(".,").lower() for w in b.split() if len(w) > 4)
    return len(sa & sb) > 0


def check_qs001_context(draft, note):
    if not note:
        return False, "No prior call note available to verify context grounding."
    grounded = _overlap(draft["draft_text"], note["customer_goal"]) or _overlap(draft["draft_text"], note["risk_or_blocker"])
    return grounded, "References customer goal/risk context." if grounded else "Draft reads generically; no clear tie to this account's specific goal or blocker."


def check_qs002_actionability(draft):
    text = draft["draft_text"].lower()
    has_action = any(w in text for w in ACTION_WORDS)
    only_vague = any(v in text for v in VAGUE_WORDS) and not has_action
    passed = has_action and not only_vague
    return passed, "Concrete next step present." if passed else "Vague language without a specific committed action/owner/timing."


def check_qs003_risk_accuracy(draft, tier):
    text = draft["draft_text"].lower()
    overstates = any(w in text for w in OVERSTATE_WORDS)
    if tier == "Urgent":
        passed = True  # urgency language is warranted on an Urgent account
        note = "Risk framing is proportionate for an Urgent-tier account."
    else:
        passed = not overstates
        note = "Risk framing proportionate." if passed else f"Draft uses alarming language ({tier} account does not warrant it)."
    return passed, note


def check_qs004_tone_clarity(draft):
    words = draft["draft_text"].split()
    passed = 8 <= len(words) <= 60 and not draft["draft_text"].isupper()
    return passed, "Concise and professional length." if passed else "Too short/long or improperly formatted for customer/internal use."


def check_qs005_escalation_judgment(draft, tier, has_open_high_sev):
    text = draft["draft_text"].lower()
    mentions_escalation = any(w in text for w in ESCALATION_WORDS)
    if tier == "Urgent" and has_open_high_sev:
        passed = mentions_escalation
        note = "Correctly signals escalation for a high-severity Urgent account." if passed else "Account has an open high-severity issue but draft does not signal escalation."
    else:
        passed = not mentions_escalation
        note = "No unnecessary escalation language." if passed else "Escalation language used on a low-risk account; likely overreaction."
    return passed, note


def check_qs006_followup_continuity(draft, note):
    if not note or not note.get("follow_up_items"):
        return True, "No outstanding follow-up to carry forward."
    passed = _overlap(draft["draft_text"], note["follow_up_items"]) or _overlap(draft["intended_customer_action"], note["follow_up_items"])
    return passed, "Carries forward prior follow-up." if passed else f"Prior follow-up item ('{note['follow_up_items']}') is not addressed."


QS_CHECKS = {
    "QS001": check_qs001_context,
    "QS002": check_qs002_actionability,
    "QS003": check_qs003_risk_accuracy,
    "QS004": check_qs004_tone_clarity,
    "QS005": check_qs005_escalation_judgment,
    "QS006": check_qs006_followup_continuity,
}


def output_quality_review(junior_outputs, call_notes_by_account, tier_by_account, open_high_sev_by_account, qs_lookup):
    reviewed = []
    for o in junior_outputs:
        acct_id = o["account_id"]
        note = call_notes_by_account.get(acct_id, [None])[-1] if call_notes_by_account.get(acct_id) else None
        tier = tier_by_account.get(acct_id, "Stable")
        has_open_high_sev = open_high_sev_by_account.get(acct_id, False)
        standard_ids = [s.strip() for s in o["quality_standard_ids"].split(";") if s.strip()]

        passed_list, failed_list, notes = [], [], []
        for qs_id in standard_ids:
            fn = QS_CHECKS[qs_id]
            if qs_id == "QS001":
                ok, note_text = fn(o, note)
            elif qs_id == "QS002":
                ok, note_text = fn(o)
            elif qs_id == "QS003":
                ok, note_text = fn(o, tier)
            elif qs_id == "QS004":
                ok, note_text = fn(o)
            elif qs_id == "QS005":
                ok, note_text = fn(o, tier, has_open_high_sev)
            elif qs_id == "QS006":
                ok, note_text = fn(o, note)
            (passed_list if ok else failed_list).append(qs_id)
            notes.append(f"{qs_id}: {'PASS' if ok else 'FAIL'} - {note_text}")

        if any(f in ("QS003", "QS005") for f in failed_list):
            recommendation = "Escalate to senior CSM review"
        elif failed_list:
            recommendation = "Revise before sending"
        else:
            recommendation = "Approve"

        rec = {
            "output_id": o["output_id"],
            "account_id": acct_id,
            "output_type": o["output_type"],
            "standards_checked": ";".join(standard_ids),
            "standards_passed": ";".join(passed_list),
            "standards_failed": ";".join(failed_list),
            "overall_recommendation": recommendation,
            "review_notes": " | ".join(notes),
        }
        reviewed.append(rec)

        ledger.log(
            "Output quality review",
            input_text=json.dumps(o) + json.dumps(qs_lookup),
            output_text=json.dumps(rec),
        )
    return reviewed


# ---------------------------------------------------------------------------
# Stage 6: Targeted intervention planning
# ---------------------------------------------------------------------------
def intervention_plan_for_account(rec, note, tickets):
    acct_id = rec["account_id"]
    open_tix = [t for t in tickets if t["account_id"] == acct_id and t["current_status"] != "closed"]
    tier = rec["priority_tier"]

    if tier == "Urgent":
        action = f"Schedule an executive recovery call within 5 business days; {rec['csm_owner']} to bring a written remediation plan with dated milestones."
    elif tier == "Watch":
        action = f"{rec['csm_owner']} to run a proactive usage review within 2 weeks and document a recovery goal with the customer."
    elif tier == "Expansion":
        action = f"{rec['csm_owner']} to prepare an expansion proposal and loop in the customer's identified champion within 3 weeks."
    else:
        action = f"{rec['csm_owner']} to maintain standard quarterly check-in cadence; no immediate intervention required."

    rationale_parts = [f"Risk score {rec['risk_score']}, opportunity score {rec['opportunity_score']}, tier {tier}."]
    if note:
        rationale_parts.append(f"Last contact flagged: {note['risk_or_blocker']}.")
    if open_tix:
        rationale_parts.append(f"{len(open_tix)} open ticket(s): {'; '.join(t['issue_summary'] for t in open_tix)}.")

    return {
        "account_id": acct_id,
        "account_name": rec["account_name"],
        "tier": tier,
        "csm_owner": rec["csm_owner"],
        "recommended_action": action,
        "rationale": " ".join(rationale_parts),
        "due_window": {"Urgent": "5 business days", "Watch": "2 weeks", "Expansion": "3 weeks", "Stable": "Next quarterly cycle"}[tier],
    }


def targeted_intervention_planning(prioritized, call_notes_by_account, tickets):
    plans = []
    for rec in prioritized:
        if rec["priority_tier"] in ("Urgent", "Watch", "Expansion"):
            note = call_notes_by_account.get(rec["account_id"], [None])[-1] if call_notes_by_account.get(rec["account_id"]) else None
            plan = intervention_plan_for_account(rec, note, tickets)
            plans.append(plan)
            ledger.log(
                "Targeted intervention planning",
                input_text=json.dumps(rec) + (json.dumps(note) if note else ""),
                output_text=json.dumps(plan),
            )
    return plans


# ---------------------------------------------------------------------------
# Stage 7: Escalation / follow-up / immediate-resolution routing (final pass)
# ---------------------------------------------------------------------------
def escalation_followup_routing(routed_tickets, quality_reviews, prioritized):
    tier_by_account = {r["account_id"]: r["priority_tier"] for r in prioritized}
    final_routes = []

    for rt in routed_tickets:
        final_routes.append(
            {
                "source": "support_ticket",
                "reference_id": rt["ticket_id"],
                "account_id": rt["account_id"],
                "final_route": rt["route"],
                "reason": rt["routing_reason"],
            }
        )

    for qr in quality_reviews:
        if qr["overall_recommendation"] == "Escalate to senior CSM review":
            route = "escalation"
        elif qr["overall_recommendation"] == "Revise before sending":
            route = "follow_up"
        else:
            route = "immediate_resolution"
        final_routes.append(
            {
                "source": "junior_output",
                "reference_id": qr["output_id"],
                "account_id": qr["account_id"],
                "final_route": route,
                "reason": qr["overall_recommendation"],
            }
        )

    for ref in final_routes:
        ledger.log(
            "24/7 responsiveness / escalation",
            input_text=json.dumps(ref),
            output_text=ref["final_route"],
        )

    return final_routes


# ---------------------------------------------------------------------------
# Evaluation checks
# ---------------------------------------------------------------------------
def run_evaluation_checks(prioritized, plans, routed_tickets, briefs, quality_reviews):
    checks = {}

    urgent_accounts = {r["account_id"] for r in prioritized if r["priority_tier"] == "Urgent"}
    planned_accounts = {p["account_id"] for p in plans}
    missing_plans = urgent_accounts - planned_accounts
    checks["every_high_risk_account_has_action"] = {
        "passed": len(missing_plans) == 0,
        "detail": f"{len(urgent_accounts)} Urgent accounts; {len(missing_plans)} missing a plan: {sorted(missing_plans)}",
    }

    high_sev_bad_routes = [
        rt for rt in routed_tickets if rt["severity"] == "High" and rt["route"] not in ("escalation", "immediate_resolution")
    ]
    checks["every_high_severity_ticket_escalated_or_resolved"] = {
        "passed": len(high_sev_bad_routes) == 0,
        "detail": f"{len(high_sev_bad_routes)} high-severity tickets misrouted: {[t['ticket_id'] for t in high_sev_bad_routes]}",
    }

    incomplete_briefs = [
        b for b in briefs if not b["prior_context"] or not b["next_steps"] or "No prior call notes" in b["prior_context"]
    ]
    checks["every_checkin_has_context_and_next_steps"] = {
        "passed": all(b["prior_context"] and b["next_steps"] for b in briefs),
        "detail": f"{len(briefs)} briefs generated; {len(incomplete_briefs)} had no prior call-note context (still received next steps): {[b['checkin_id'] for b in incomplete_briefs]}",
    }

    unchecked_outputs = [qr for qr in quality_reviews if not qr["standards_checked"]]
    checks["every_junior_output_checked_against_standards"] = {
        "passed": len(unchecked_outputs) == 0,
        "detail": f"{len(quality_reviews)} outputs reviewed; {len(unchecked_outputs)} had no standards checked.",
    }

    return checks


REMEDIATION_ROUTES = {
    "every_high_risk_account_has_action": "Route to CSM Manager queue for manual intervention plan within 1 business day",
    "every_high_severity_ticket_escalated_or_resolved": "Route to immediate escalation queue -- treat as a routing-logic defect, not just a one-off miss",
    "every_checkin_has_context_and_next_steps": "Route back to Customer check-in support stage for regeneration before the scheduled check-in",
    "every_junior_output_checked_against_standards": "Route to Output quality review stage for a full re-check before Approve/Revise/Escalate is finalized",
}


def write_evaluation_failures(checks, path):
    failures = [
        {
            "check": name,
            "detail": result["detail"],
            "recommended_remediation_route": REMEDIATION_ROUTES.get(name, "Route to CSM Manager for manual review"),
        }
        for name, result in checks.items()
        if not result["passed"]
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"failures": failures}, f, indent=2)
    return failures


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------
def write_csv(filename, rows, fieldnames):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_checkin_briefs_md(briefs, path):
    lines = ["# Customer Check-In Briefs", ""]
    for b in briefs:
        lines += [
            f"## {b['account_name']} ({b['account_id']}) - {b['checkin_type']}",
            f"- Scheduled: {b['scheduled_date']} | Priority: {b['priority']} | Account tier: {b['account_priority_tier']}",
            f"- Topics to cover: {b['topics_to_cover']}",
            f"- Prior context: {b['prior_context']}",
            f"- Next steps: {b['next_steps']}",
            "",
        ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_intervention_plan_md(plans, path):
    lines = ["# Targeted Intervention Plan", ""]
    for tier in ("Urgent", "Watch", "Expansion"):
        tier_plans = [p for p in plans if p["tier"] == tier]
        if not tier_plans:
            continue
        lines.append(f"## {tier} accounts")
        for p in tier_plans:
            lines += [
                f"### {p['account_name']} ({p['account_id']})",
                f"- Owner: {p['csm_owner']} | Due: {p['due_window']}",
                f"- Recommended action: {p['recommended_action']}",
                f"- Rationale: {p['rationale']}",
                "",
            ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    accounts = load_csv("accounts.csv")
    usage_events = load_csv("usage_events.csv")
    tickets = load_csv("support_tickets.csv")
    checkins = load_csv("scheduled_checkins.csv")
    call_notes = load_csv("call_notes.csv")
    junior_outputs = load_csv("junior_outputs.csv")
    quality_standards = load_csv("quality_standards.csv")

    accounts_by_id = {a["account_id"]: a for a in accounts}
    call_notes_by_account = defaultdict(list)
    for n in call_notes:
        call_notes_by_account[n["account_id"]].append(n)
    tickets_by_account = defaultdict(list)
    for t in tickets:
        tickets_by_account[t["account_id"]].append(t)
    qs_lookup = {q["standard_id"]: q for q in quality_standards}

    # Stage 0
    memory_packets = memory_context_retrieval(accounts, call_notes_by_account, tickets_by_account, usage_events, checkins)
    memory_packets_by_account = {p["account_id"]: p for p in memory_packets}

    # Stage 1 + 2
    reviewed = daily_account_review(accounts, usage_events)
    prioritized = account_prioritization(reviewed, tickets)
    tier_by_account = {r["account_id"]: r["priority_tier"] for r in prioritized}
    open_high_sev_by_account = {
        r["account_id"]: r["has_open_high_severity_ticket"] for r in prioritized
    }

    # Stage 3
    routed_tickets = inbound_support_issue_routing(tickets, tier_by_account)

    # Stage 4
    briefs = customer_checkin_preparation(
        checkins, accounts_by_id, call_notes_by_account, tickets_by_account, tier_by_account, memory_packets_by_account
    )

    # Stage 5
    quality_reviews = output_quality_review(
        junior_outputs, call_notes_by_account, tier_by_account, open_high_sev_by_account, qs_lookup
    )

    # Stage 6
    plans = targeted_intervention_planning(prioritized, call_notes_by_account, tickets)

    # Stage 7
    final_routes = escalation_followup_routing(routed_tickets, quality_reviews, prioritized)

    # Evaluation checks
    checks = run_evaluation_checks(prioritized, plans, routed_tickets, briefs, quality_reviews)
    eval_failures = write_evaluation_failures(checks, os.path.join(OUT_DIR, "evaluation_failures.json"))

    # ---- Write outputs ----
    write_csv(
        "memory_context_retrieval.csv",
        memory_packets,
        fieldnames=[
            "account_id", "account_name", "open_ticket_count", "last_call_date",
            "last_call_followup", "usage_trend", "next_checkin_date", "memory_packet",
        ],
    )

    write_csv(
        "account_prioritization.csv",
        prioritized,
        fieldnames=[
            "account_id", "account_name", "csm_owner", "priority_tier", "risk_score",
            "opportunity_score", "health_delta", "current_health_score", "usage_trend",
            "nps_score", "expansion_signal", "support_ticket_count_30d",
            "has_open_high_severity_ticket", "notable_change",
        ],
    )

    write_csv(
        "issue_routing.csv",
        routed_tickets,
        fieldnames=["ticket_id", "account_id", "severity", "customer_sentiment", "account_priority_tier", "route", "routing_reason", "issue_summary"],
    )

    write_checkin_briefs_md(briefs, os.path.join(OUT_DIR, "checkin_briefs.md"))

    write_csv(
        "quality_review.csv",
        quality_reviews,
        fieldnames=["output_id", "account_id", "output_type", "standards_checked", "standards_passed", "standards_failed", "overall_recommendation", "review_notes"],
    )

    write_intervention_plan_md(plans, os.path.join(OUT_DIR, "intervention_plan.md"))

    # Token/cost summary, shaped to drop into the Token Math Sheet template.
    stage_summary = ledger.summary_by_stage()
    token_rows = []
    for stage, agg in stage_summary.items():
        model = STAGE_MODEL[stage]
        price = MODEL_PRICING[model]
        token_rows.append(
            {
                "workflow_component": stage,
                "operating_area": stage,
                "model": model,
                "input_dollar_per_1m": price["input"],
                "output_dollar_per_1m": price["output"],
                "runs_in_this_simulation": agg["runs"],
                "total_input_tokens_estimate": agg["input_tokens"],
                "total_output_tokens_estimate": agg["output_tokens"],
                "avg_input_tokens_per_run": round(agg["input_tokens"] / agg["runs"], 1) if agg["runs"] else 0,
                "avg_output_tokens_per_run": round(agg["output_tokens"] / agg["runs"], 1) if agg["runs"] else 0,
                "estimated_cost_this_simulation": round(agg["cost"], 6),
                "notebook_measured_avg_cost_per_run": round(agg["cost"] / agg["runs"], 8) if agg["runs"] else 0,
            }
        )
    write_csv(
        "token_cost_summary.csv",
        token_rows,
        fieldnames=[
            "workflow_component", "operating_area", "model", "input_dollar_per_1m", "output_dollar_per_1m",
            "runs_in_this_simulation", "total_input_tokens_estimate", "total_output_tokens_estimate",
            "avg_input_tokens_per_run", "avg_output_tokens_per_run", "estimated_cost_this_simulation",
            "notebook_measured_avg_cost_per_run",
        ],
    )

    # Representative end-to-end account runs
    demo_runs = []
    for acct_id in DEMO_ACCOUNTS:
        rec = next((r for r in prioritized if r["account_id"] == acct_id), None)
        if not rec:
            continue
        demo_runs.append(
            {
                "account_id": acct_id,
                "account_name": rec["account_name"],
                "priority_tier": rec["priority_tier"],
                "risk_score": rec["risk_score"],
                "memory_context_retrieval": memory_packets_by_account.get(acct_id),
                "tickets_routed": [r for r in routed_tickets if r["account_id"] == acct_id],
                "checkin_brief": next((b for b in briefs if b["account_id"] == acct_id), None),
                "quality_review": [q for q in quality_reviews if q["account_id"] == acct_id],
                "intervention_plan": next((p for p in plans if p["account_id"] == acct_id), None),
            }
        )

    run_summary = {
        "accounts_reviewed": len(prioritized),
        "memory_packets_generated": len(memory_packets),
        "priority_tier_counts": {
            tier: sum(1 for r in prioritized if r["priority_tier"] == tier)
            for tier in ("Urgent", "Watch", "Expansion", "Stable")
        },
        "tickets_routed": len(routed_tickets),
        "checkin_briefs_generated": len(briefs),
        "junior_outputs_reviewed": len(quality_reviews),
        "intervention_plans_generated": len(plans),
        "final_routing_decisions": len(final_routes),
        "evaluation_checks": checks,
        "representative_end_to_end_runs": demo_runs,
        "total_estimated_simulation_cost": round(sum(r["estimated_cost"] for r in ledger.records), 6),
    }
    with open(os.path.join(OUT_DIR, "run_summary.json"), "w", encoding="utf-8") as f:
        json.dump(run_summary, f, indent=2)

    # ---- Console report ----
    print("=== CS AI Workflow Simulation: run complete ===")
    print(f"Memory packets generated: {len(memory_packets)}")
    print(f"Accounts reviewed: {len(prioritized)}")
    for tier in ("Urgent", "Watch", "Expansion", "Stable"):
        n = run_summary["priority_tier_counts"][tier]
        print(f"  {tier}: {n}")
    print(f"Tickets routed: {len(routed_tickets)}")
    print(f"Check-in briefs: {len(briefs)}")
    print(f"Junior outputs reviewed: {len(quality_reviews)}")
    print(f"Intervention plans: {len(plans)}")
    print(f"Total estimated simulation cost: ${run_summary['total_estimated_simulation_cost']:.6f}")
    print()
    print("Evaluation checks:")
    for name, result in checks.items():
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  [{status}] {name}: {result['detail']}")
    if eval_failures:
        print(f"  -> {len(eval_failures)} failure(s) written to evaluation_failures.json with remediation routes")
    print()
    print(f"Outputs written to: {OUT_DIR}")


if __name__ == "__main__":
    main()
