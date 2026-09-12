# Product Requirements — RemitOS (Borderless Money pack)

## 1. Problem statement

Bangladesh received **USD 35.56 bn** in formal remittances in FY 2025-26 and is the
world's 7th largest recipient. Roughly **49 %** of the total flow is estimated to arrive
outside formal channels, and the global average cost of sending USD 200 remains **6.36 %**
against an SDG target of 3 %.

The binding constraint is not volume or technology. It is that **no neutral party computes
the routing decision** — which rail, which FX window, which payout endpoint delivers the
most taka, soonest, within regulatory limits. Senders guess across three providers;
recipients discover constraints at the counter; compliance is manual and therefore
expensive, and that expense is the cost floor everyone pays.

Full sourcing: `docs/research/data/`.

## 2. Target users

P1 sender · P2 rural recipient · P3 freelancer · P4 agent · P5 compliance officer.
See `personas.md`.

## 3. Scope

### In scope (v1)

| Capability | Notes |
|---|---|
| Least-cost / fastest-path routing across rails | The core differentiator |
| Regulatory limits as optimiser constraints, with legal split proposals | ADR 0007 |
| RAG-grounded compliance decisioning with citations | ADR 0004 |
| Predictive FX timing guidance | Advisory only |
| Bangla-first Flutter client, Android / iOS / Web | ADR 0001, 0012 |
| Offline-first with outbox queue | ADR 0008 |
| USSD + Bangla IVR path | ADR 0008 |
| Agent mode with float forecasting | P4 |
| Officer console with evidence bundles | P5 |
| Double-entry event-sourced ledger | ADR 0009 |
| Immutable audit + generated audit report | `docs/security/audit-readiness.md` |

### Explicitly out of scope

| Excluded | Why |
|---|---|
| **Outbound payments from Bangladesh** | Capital-account policy, not a product problem. See report §10 |
| Holding customer funds | Requires licences we do not have; we orchestrate |
| Building our own agent network | Cannot out-build bKash; partner instead |
| Crypto / stablecoin rails in v1 | Regulatory position in Bangladesh does not support it |
| Lending, savings, insurance | Future domain packs, not v1 |

Naming what is out of scope, and why, is how the scope stays real.

## 4. Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Return ranked routes with landed BDT and ETA interval within 400 ms p95 | P0 |
| FR-02 | Reject or split any route violating a BB ceiling **before quoting** | P0 |
| FR-03 | Every compliance decision carries a reason code and, on RAG paths, citations | P0 |
| FR-04 | Any AML score above threshold routes to a human gate | P0 |
| FR-05 | All user-facing text available in Bangla; CI fails on missing strings | P0 |
| FR-06 | Core flows reachable by USSD and Bangla IVR | P0 |
| FR-07 | Transfers composable offline, queued with idempotency, honest "queued" state | P0 |
| FR-08 | Every state change emits an immutable audit event | P0 |
| FR-09 | Voice-captured amounts read back and confirmed before execution | P0 |
| FR-10 | Held transfers notify immediately with a plain-Bangla reason and SLA | P0 |
| FR-11 | FX timing guidance with explicit uncertainty; suppressed on urgent transfers | P1 |
| FR-12 | Agent float forecasting and large-payout advance notice | P1 |
| FR-13 | Officer evidence bundles including contradictory evidence | P1 |
| FR-14 | Realised-vs-predicted cost and ETA shown in transfer history | P1 |
| FR-15 | Domain pack swappable without core changes | P1 |

FR-14 is unusual and deliberate: the product is held publicly accountable for its own
estimates, which is also the fastest way to find out the model is wrong.

## 5. Non-functional requirements

See `docs/architecture/system-overview.md`. Summary: quote p95 under 400 ms · payout
initiation p95 under 3 s · 99.9 % core availability · RPO 0 for the ledger · under 50 KB
per screen in low-bandwidth mode · PII in-country only.

## 6. Business model

| Line | Mechanism |
|---|---|
| Transaction take-rate | Basis points on landed value, below incumbent effective cost |
| FX spread share | Shared with the partner, disclosed to the user |
| Compliance-as-a-service | Licensing the screening and decisioning stack to smaller PSPs |
| Agent SaaS | Float forecasting and reconciliation tooling |
| Data products | **Aggregated, anonymised corridor benchmarks only.** Never user-level |

The last row carries an absolute constraint: selling anything derived from identifiable
user behaviour is prohibited, not merely discouraged.

### Unit economics — the model, not the answer

The template below is what the team fills with real numbers during Phase 3 validation.
**No illustrative figures are stated here**, because a fabricated unit-economics table
presented as analysis is exactly what Congress §20.4 prohibits.

```
Contribution per transfer
  = (take_rate × landed_value) + fx_spread_share
  − partner_rail_cost
  − payout_cost
  − variable_compliance_cost        ← incl. human review minutes × loaded cost
  − variable_infrastructure_cost    ← incl. LLM tokens and in-boundary GPU

Break-even monthly volume = fixed_cost ÷ contribution_per_transfer
```

`variable_compliance_cost` is the term most fintech models omit and the one ADR 0010
makes unavoidable: a mandatory human gate is a real, measurable cost per escalated
transfer, and modelling it honestly is what makes the rest of the model credible.

## 7. Success metrics

| Metric | Why it is the right metric |
|---|---|
| **Landed amount delivered per USD 100 sent, vs the corridor benchmark** | The only user-truthful measure of value |
| Median time to recipient availability | The hundi-beating metric |
| Share of transfers completing without human intervention | Efficiency, honestly measured |
| **Group-wise false-positive rate spread** | Fairness as an operating metric, not a report line |
| Active monthly senders (not registrations) | Registered accounts already exceed the population |
| Rural recipient share | Are we reaching the people we claim to serve |
| IVR/USSD flow completion rate | Is the accessibility path real |
| Realised-vs-predicted cost error | Are we honest about our own estimates |

Deliberately **not** a headline metric: registered users. Bangladesh already has more
registered MFS accounts than people, which makes registration a vanity number.
