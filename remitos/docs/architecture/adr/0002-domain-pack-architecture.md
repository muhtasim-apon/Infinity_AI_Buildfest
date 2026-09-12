# ADR 0002 — Domain-pack architecture for fintech verticals

**Status:** Accepted · **Date:** 2026-09-12 · **Deciders:** whole team

## Context

FinSphere AI names five challenge areas: CreditForAll, FraudShield, WealthPilot, SME
Capital Engine and Borderless Money. We are building Borderless Money, but two pressures
argue against hard-coding it:

1. **Strategic.** A remittance orchestrator that cannot extend into credit or fraud is a
   feature, not a company. The Congress explicitly rewards "capacity to scale to millions
   and international markets" and a "realistic path to a sustainable, monetizable
   business" (§11.1).
2. **Practical.** Requirements shift across a six-month journey. A team that must rewrite
   its core to change vertical loses the journey.

Meanwhile roughly 70 % of what any of these five products needs is identical: identity,
KYC, a ledger, risk scoring, a knowledge layer, agents, automation, observability,
audit.

## Decision

Split the system into a **domain-agnostic core** and **swappable domain packs**. A pack
supplies exactly four things and may supply nothing else:

| Pack element | What it is | Where it lives |
|---|---|---|
| **Config** | Feature flags, limits, rails, fee schedules, workflow bindings | `domain_packs/<pack>/config/` |
| **Schemas** | Domain entities and events, versioned | `domain_packs/<pack>/schemas/` |
| **Prompts** | System prompts, tool descriptions, retrieval templates | `domain_packs/<pack>/prompts/` |
| **Models** | Domain-specific ML models and their cards | `ml/models/` tagged by pack |

The core exposes stable extension points; it never imports from a pack.

```
        ┌──────────────────── domain-agnostic core ────────────────────┐
        │ identity · kyc · ledger · rag · agents · n8n · observability │
        └────────────────────────┬─────────────────────────────────────┘
                                 │ extension points
     ┌──────────┬────────────────┼────────────────┬──────────┐
 borderless   credit          fraud            wealth       sme
  money      (stub)          (stub)            (stub)      (stub)
 [ACTIVE]
```

## Consequences

**Positive**

- Switching or adding a vertical is a pack, not a rewrite. This is the property the user
  explicitly asked for and it is also a genuine commercial moat.
- The core gets hardened five times over rather than once.
- Judges can see the abstraction is real because four stub packs exist alongside the
  active one, with their extension points already declared.

**Negative**

- Upfront abstraction cost before any vertical is finished. Mitigated by building the
  abstraction *from* Borderless Money rather than speculatively ahead of it — the stubs
  declare interfaces, they do not implement speculative features.
- Risk of a leaky abstraction where a vertical needs a core change. Governed by a rule:
  **a core change to accommodate a vertical requires a new ADR.** If that happens twice
  for the same reason, the abstraction is wrong and gets redrawn.

**Rejected alternatives**

| Option | Why not |
|---|---|
| Build Borderless Money monolithically, generalise later | "Later" does not arrive; the generalisation becomes a rewrite |
| Build a generic fintech framework first | No forcing function; produces an abstraction nobody has validated against a real product |
| Separate repository per vertical | Duplicates the 70 % core; diverges within weeks |

## Related

ADR 0003 (service boundaries), ADR 0006 (n8n as automation plane).
