# Regulatory & Go-to-Market Path

> This is the chapter most student fintech projects skip, and it is the one that decides
> whether the product can legally exist. Congress §11.1 scores "a realistic path to a
> sustainable, monetizable business" — realistic includes lawful.

## 1. What we are not

RemitOS as designed does **not**:

- hold customer funds
- operate as a money transfer operator
- issue accounts or wallets
- set exchange rates

It orchestrates across licensed parties. That is a deliberate regulatory posture, not a
limitation we discovered late: the orchestration layer is both the defensible product and
the only position a new entrant can occupy without years of licensing first.

We are, however, **not licence-free**. Processing payment instructions and personal data
on behalf of licensed institutions carries its own obligations.

## 2. The relevant regimes

| Regime | Authority | Relevance |
|---|---|---|
| Payment and Settlement Systems regulation | Bangladesh Bank | PSP/PSO categories; who may touch an instruction |
| MFS regulation | Bangladesh Bank | The ceilings encoded in ADR 0007 |
| Foreign Exchange regulation | Bangladesh Bank | Inbound remittance treatment; the outbound restriction |
| AML/CFT | BFIU | CDD, screening, reporting, retention |
| FATF Travel Rule | International, via BFIU | Originator/beneficiary data with transfers |
| Data protection | Evolving national framework | Residency, consent, user rights |
| Sending-country regimes | SAMA, CBUAE, BNM, FCA, FinCEN | The *sending* side is licensed there, not here |

The last row matters and is routinely missed: a corridor has two regulators. Origination
in Riyadh is regulated by SAMA regardless of what Bangladesh permits.

## 3. Sequenced path

| Stage | Duration (planning assumption) | What happens |
|---|---|---|
| **0 — Design & counsel** | Now → Phase 3 | Written legal opinion on whether the orchestration model is licensable as designed. **This precedes engineering commitments, not follows them.** |
| **1 — Regulatory sandbox** | Phase 4–6 | Apply to the Bangladesh Bank sandbox with a bounded pilot: one corridor, capped volume, capped ticket size |
| **2 — Partner-of-record pilot** | Post-Congress, 6–12 mo | Operate under a licensed PSP/bank partner's authorisation. They hold the licence and the float; we supply intelligence and orchestration |
| **3 — Own authorisation** | 12–30 mo | Apply in our own right once volume, controls and audit history justify it |
| **4 — Corridor expansion** | Continuous | Each new corridor needs sending-side licensing, not just Bangladeshi approval |

Stage 2 is the commercially serious one. It is how a new entrant reaches real users
without a licence it cannot yet obtain, and it is why "compliance-as-a-service" appears
in the business model — it is the same capability sold to the partner who is carrying us.

## 4. Partnership dependencies

| Partner type | What we need | What they get | Risk |
|---|---|---|---|
| Licensed PSP / bank | Authorisation, settlement, float | Intelligence layer, better conversion, automated compliance | They can build it themselves |
| MFS operator | Payout endpoints and reach | Incremental inbound volume | Low incentive to help a disintermediator |
| Sending-side MTO | Corridor origination | Better BD payout economics | Relationship-driven, slow |
| Telco aggregator | USSD short code and IVR | Revenue share | Long procurement cycles |
| Sanctions/PEP data provider | Screening data | Subscription | Cost scales with volume |

**The MFS row is the strategic tension of the entire venture**, and it should be stated
plainly rather than glossed: bKash has no obvious reason to help a layer that sits above
it and commoditises it. The counter-arguments — incremental inbound volume it does not
currently capture, and formalising flow that presently goes to hundi — are real but not
guaranteed to persuade. This is the single largest commercial risk in the project and it
belongs in the risk register with an owner.

## 5. Compliance obligations we carry from day one

Even without our own licence, operating as a processor for a licensed partner means:

- CDD execution to the partner's standard, evidenced
- Sanctions screening with retained evidence
- Travel Rule payload construction and transmission
- Record retention per BFIU, in-country
- Incident and breach notification
- Auditability sufficient for the partner's own supervisor to inspect

These are not deferred to Stage 3. They are the reason `services/compliance`,
`services/audit` and the ledger are v1 scope rather than v2 ambitions.

## 6. Honest position

We do not have a licence, a float, an agent network or a supervisory relationship. Those
are stated as gaps in the report's gap-analysis chapter with mitigations and a
partnership path, not omitted.

A project claiming to have solved cross-border payments without addressing licensing has
not solved cross-border payments — it has built a demo. Congress §20.9 prohibits
misrepresenting technical capability, and the same standard reasonably applies to
regulatory capability.
