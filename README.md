# SentinelDesk

A local ticket triage engine that scores and prioritizes support / trust & safety tickets by risk and urgency, the same kind of judgment call a Support or T&S analyst makes when deciding what to handle first.

## Why this exists

Support and Trust & Safety teams get flooded with tickets that all look equally "urgent" in a raw inbox. A typo report and a self-harm concern can land in the same queue with no visual difference. SentinelDesk reads ticket text, matches it against a risk rubric, and re-sorts the queue so the highest-risk items surface first, automatically.

## How it works

1. Tickets are loaded from a CSV (`tickets.csv`), simulating a support/T&S inbox.
2. Each ticket's message is checked against a tiered risk rubric (see below).
3. Tickets containing urgency language ("urgent", "scared", "immediately") get a score boost on top of their category score.
4. Results are sorted highest-priority first and printed as a readable report, plus saved to `triage_report.csv` for record-keeping.

## Risk rubric

| Category | Score | Example |
|---|---|---|
| Self-Harm / Safety Risk | 100 | Mentions of self-harm in user content |
| Account Takeover / Security | 90 | Unauthorized account changes |
| Harassment / Abuse | 85 | Threats from other users |
| Suspicious Account Activity | 70 | Unrecognized login attempts |
| Policy-Violating Content | 65 | Graphic/violent content reports |
| Account Access Issue | 40 | Login/password problems |
| Billing / Payment | 25 | Charges, refunds, failed payments |
| Performance Issue | 15 | Slow load times |
| Low Priority / Cosmetic | 5 | Typos, feature requests |

This rubric is intentionally simple and transparent. In a real environment, weights would be tuned against historical outcomes and reviewed regularly, the goal here is to demonstrate the *triage logic*, not to ship a production classifier.

## Running it

```
python triage.py
```

Reads `tickets.csv`, prints the prioritized report, and writes `triage_report.csv`.

## Note on data

All tickets in `tickets.csv` are synthetic, written to simulate realistic categories a support/T&S queue would see. No real user data is used.

## What I'd build next

- Swap the keyword-matching rubric for a proper sentiment/intent classifier (e.g. an NLP model) to catch phrasing the keyword list misses
- Add a simple web dashboard to view the report without reading a terminal
- Move from a single CSV run to a live queue (this is the natural next step toward a cloud-hosted version using a message queue and serverless functions)
