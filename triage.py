"""
SentinelDesk - Local Ticket Triage Engine
-------------------------------------------
Reads a CSV of support/trust & safety tickets, scores each one for
urgency and risk, and outputs a prioritized report.

This is the local, no-cloud version of the triage logic. The scoring
rubric here is the same kind of thinking a Trust & Safety or Support
team applies when deciding what to escalate first.
"""

import csv
from datetime import datetime

# ---------------------------------------------------------------------
# STEP 1: Define the risk rubric.
# Each category below maps to a list of keywords/phrases. If a ticket's
# message contains one of these, it gets flagged into that category.
# Categories are ordered from highest risk to lowest.
# ---------------------------------------------------------------------

RISK_CATEGORIES = {
    "self_harm_risk": {
        "keywords": ["hurt themselves", "suicide", "self harm", "self-harm", "kill myself", "end my life"],
        "score": 100,
        "label": "Self-Harm / Safety Risk",
    },
    "account_takeover": {
        "keywords": ["changed my email", "changed my password without", "account takeover", "someone accessed my account", "without my permission"],
        "score": 90,
        "label": "Account Takeover / Security",
    },
    "harassment_abuse": {
        "keywords": ["threatening", "harassment", "harassing", "threatened me", "scared to use"],
        "score": 85,
        "label": "Harassment / Abuse",
    },
    "suspicious_activity": {
        "keywords": ["suspicious login", "tried to log into my account", "country i have never"],
        "score": 70,
        "label": "Suspicious Account Activity",
    },
    "graphic_content": {
        "keywords": ["graphic", "violent content", "inappropriate content"],
        "score": 65,
        "label": "Policy-Violating Content",
    },
    "access_issue": {
        "keywords": ["cannot log in", "cannot access my account", "reset my password"],
        "score": 40,
        "label": "Account Access Issue",
    },
    "billing": {
        "keywords": ["charge", "invoice", "refund", "payment failed", "card", "billing"],
        "score": 25,
        "label": "Billing / Payment",
    },
    "performance": {
        "keywords": ["slow", "loading", "performance", "lag"],
        "score": 15,
        "label": "Performance Issue",
    },
    "feature_request": {
        "keywords": ["feature request", "would be great if", "dark mode", "typo", "spelling mistake"],
        "score": 5,
        "label": "Low Priority / Cosmetic",
    },
}

# Urgency language that bumps the score up regardless of category
URGENCY_BOOST_KEYWORDS = ["urgent", "scared", "worried", "asap", "immediately", "right away"]
URGENCY_BOOST_VALUE = 10


def score_ticket(message: str):
    """
    Looks at a ticket's message text and returns:
    - the matched category key (or None if nothing matched)
    - the base risk score
    - a human-readable label
    - whether an urgency boost applied
    """
    message_lower = message.lower()

    matched_category = None
    matched_score = 0
    matched_label = "Uncategorized"

    # Walk through categories in the order defined above (highest risk first).
    # First match wins, since categories are already ordered by severity.
    for category_key, details in RISK_CATEGORIES.items():
        for keyword in details["keywords"]:
            if keyword in message_lower:
                matched_category = category_key
                matched_score = details["score"]
                matched_label = details["label"]
                break
        if matched_category:
            break

    # Check for urgency language that should push this ticket up the queue
    urgency_boost_applied = any(word in message_lower for word in URGENCY_BOOST_KEYWORDS)
    final_score = matched_score + (URGENCY_BOOST_VALUE if urgency_boost_applied else 0)

    return {
        "category": matched_category or "uncategorized",
        "label": matched_label,
        "base_score": matched_score,
        "urgency_boost": urgency_boost_applied,
        "final_score": final_score,
    }


def load_tickets(csv_path: str):
    """Reads the tickets CSV into a list of dictionaries."""
    tickets = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickets.append(row)
    return tickets


def triage_tickets(tickets: list):
    """Scores every ticket and returns them sorted highest priority first."""
    scored = []
    for ticket in tickets:
        result = score_ticket(ticket["message"])
        scored.append({
            "ticket_id": ticket["ticket_id"],
            "subject": ticket["subject"],
            "reported_by": ticket["reported_by"],
            "category": result["category"],
            "label": result["label"],
            "score": result["final_score"],
            "urgency_boost": result["urgency_boost"],
        })

    # Sort highest score first (most urgent at the top)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def print_report(scored_tickets: list):
    """Prints a clean, readable triage report to the terminal."""
    print("=" * 70)
    print("SENTINELDESK TRIAGE REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Total tickets processed: {len(scored_tickets)}")
    print("=" * 70)
    print()

    for ticket in scored_tickets:
        boost_flag = " [URGENCY LANGUAGE DETECTED]" if ticket["urgency_boost"] else ""
        print(f"[{ticket['score']:>3}] Ticket #{ticket['ticket_id']} - {ticket['label']}{boost_flag}")
        print(f"      Subject: {ticket['subject']}")
        print(f"      Reported by: {ticket['reported_by']}")
        print()


def save_report_csv(scored_tickets: list, output_path: str):
    """Saves the triage results to a CSV file for record-keeping."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ticket_id", "subject", "reported_by", "category", "label", "score", "urgency_boost"])
        writer.writeheader()
        writer.writerows(scored_tickets)


if __name__ == "__main__":
    tickets = load_tickets("tickets.csv")
    scored = triage_tickets(tickets)
    print_report(scored)
    save_report_csv(scored, "triage_report.csv")
    print(f"Full report saved to triage_report.csv")
