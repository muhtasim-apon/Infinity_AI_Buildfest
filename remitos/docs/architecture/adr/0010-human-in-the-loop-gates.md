# ADR 0010 — No agent moves money without a human gate

**Status:** Accepted · **Date:** 2026-09-12

## Context

The system runs five autonomous agents (compliance, routing, support, research,
reconciliation) with tool access. Agents are probabilistic. Money is not.

Congress §15 requires transparency and active bias mitigation; §13.1 states that even
human mentors may not change the core direction of work without it being visible. The
same principle applied to software: an autonomous system's authority must be bounded and
its boundary must be inspectable.

## Decision

A four-level authority model, declared per tool in the MCP registry and enforced at the
tool boundary, not by prompt instruction.

| Level | Agent may | Examples |
|---|---|---|
| **L0 Read** | Retrieve, summarise, explain | Answer a user question from RAG; fetch a rate |
| **L1 Draft** | Prepare an action for approval | Draft a SAR narrative; propose a route |
| **L2 Act — reversible** | Execute within bounds, logged | Re-rank routes; open a case; send a notification |
| **L3 Act — irreversible** | **Never autonomous** | Move funds; release a held transfer; override a BLOCK; change a limit |

Mandatory human gates:

- Any AML score above `AML_HUMAN_REVIEW_SCORE` (default 0.70)
- Any sanctions hit, without exception, regardless of confidence
- Any transfer above the corridor's review threshold
- Any override of a prior BLOCK
- Any change to a regulatory limit or fee schedule
- Any model promotion to production

Each gate records **who** decided, **when**, **what they saw** (the exact evidence bundle
presented to them) and **why** — into the immutable audit log. "What they saw" matters:
an officer's decision can only be assessed against the information they actually had.

Escalations are routed by n8n workflow 05 with an SLA, and an unactioned escalation ages
into an alert rather than silently expiring.

## Consequences

**Positive** — no autonomous failure can move money; regulatory defensibility; the
audit trail captures human reasoning, not merely machine output; the team can honestly
answer the judging question "what happens when your model is wrong?" with a mechanism
rather than a reassurance.

**Negative** — human review is a throughput ceiling and an operating cost. This is
modelled explicitly in the unit economics (`docs/product/prd.md`) rather than wished
away. It also means the product cannot claim full automation — which is the honest
claim, and §20.9 prohibits misrepresenting technical capability.

**Rejected** — full autonomy with post-hoc review (money has already moved); confidence
thresholds alone (a miscalibrated model is confidently wrong, and calibration drifts);
human review of everything (no scale, and reviewer fatigue degrades decision quality on
the cases that matter).
