# ADR 0007 — Encode regulatory ceilings as optimiser constraints

**Status:** Accepted · **Date:** 2026-09-12

## Context

Bangladesh Bank's Payment Systems Department re-fixed MFS limits in March 2025:

| Limit | Daily | Monthly |
|---|---|---|
| Cash-in at agent | Tk 50,000 | Tk 300,000 |
| **Cash-out at agent** | **Tk 30,000** | **Tk 200,000** |
| P2P transfer | Tk 50,000 | Tk 300,000 |
| Maximum wallet balance | — | Tk 500,000 |

Consider a routine case. A construction worker in Riyadh sends the equivalent of
Tk 120,000 for a medical emergency. Every conventional product quotes a price, accepts
the money, and pays out to a wallet. The recipient — often an older woman in a rural
upazila who has travelled to reach the agent point — can withdraw Tk 30,000. The rest
sits in a wallet she may not know how to move, in the middle of an emergency.

The money was never lost. The *product* simply never modelled the constraint.

## Decision

Regulatory ceilings are **inputs to the optimiser**, not validations after the fact. The
routing engine's constraint filter runs before a price is ever shown, and the engine
returns one of three honest outcomes:

1. **Single compliant path** — one endpoint clears the full amount legally.
2. **Proposed legal split** — e.g. Tk 30,000 to wallet for immediate cash-out today,
   Tk 90,000 to a linked bank account, with both legs priced, timed and explained in
   Bangla on one screen.
3. **Explicit infeasibility** — the amount cannot be delivered as requested within the
   limits, stated *before* the sender pays, with the alternatives listed.

The limits live in configuration (`BB_MFS_*` in `.env.example`), are versioned with an
effective date, and are refreshed by n8n workflow 07 when a circular changes them. A
limit change is a config change, never a code change.

## Consequences

**Positive** — this is the difference between a product that has read the regulation and
one that has read only the API documentation. It is also directly commercial: the split
recommendation is a genuinely better outcome that no incumbent currently offers, and it
is demonstrable on stage in thirty seconds.

**Negative** — a materially more complex optimiser (multi-endpoint, multi-leg, each leg
with its own cost and ETA) and a more complex UI, which must explain a split without
confusing a low-literacy user. The UX for this is specified in
`docs/product/user-journeys.md` and is icon-and-voice-led.

Limits change by circular, sometimes at short notice, including temporary election-period
caps. The config-with-effective-date design is what makes that survivable.

**Rejected** — validating after quote (the failure described above); silently capping the
transfer at Tk 30,000 (hides money from the user); ignoring limits and letting the
partner rail reject (produces the worst possible failure point: after the sender has paid).
