# Personas

> These are composites built from the research in `docs/research/data/`, not invented
> characters. Each one exists to make a specific design constraint unavoidable.

---

## P1 — Abul Kashem · the sender

**42 · construction supervisor · Riyadh · 9 years abroad · sends monthly**

Android mid-tier phone, good wifi at the labour camp. Reads Bangla fluently, functional
English. Sends Tk 35,000–60,000 monthly, occasionally much more for an emergency.
Currently uses a mix: an exchange house near the camp when the rate looks good, and hundi
through a known intermediary when it looks better or when he needs same-day delivery.

**What he actually optimises for:** *how many taka reach his mother.* Not the fee — the
landed amount. He does the arithmetic himself, badly, across three providers, every month.

**Pain**
- Cannot compare true landed cost across providers; each shows a different piece
- Exchange-house queues on his one day off
- No idea when the money actually arrives — "2–3 days" means nothing
- The 2.5 % government incentive is real money and he is unsure which channels carry it
- Hundi is faster and sometimes better-rated; he knows it is not legal and uses it anyway

**Design consequences**
- Show **landed BDT**, prominently, as the headline number. Never lead with the fee.
- Show a real ETA with an interval, and be accountable for it afterwards
- Make the incentive eligibility explicit and automatic
- To beat hundi, beat it on rate, speed and certainty — not on compliance messaging

---

## P2 — Rahima Begum · the recipient

**58 · Abul's mother · village in Kishoreganj · limited literacy · no smartphone**

Owns a feature phone. Her neighbour's son helps her with anything on a screen. Travels
about 40 minutes to the nearest agent point. Has been told a wallet balance exists but
has never moved money herself.

**She is the user this product is actually for, and she is the user most fintech
products silently exclude.**

**Pain**
- Cannot read a transaction SMS reliably; asks someone else, which means her balance is
  not private
- Does not know money has arrived until someone tells her
- Cash-out limits she has never been told about interrupt her at the counter
- Has been targeted by a phone scam once already
- Agent sometimes charges more than the posted rate; she has no way to check

**Design consequences**
- **IVR in Bangla** is her primary interface, not a fallback (ADR 0008)
- Voice arrival notification, not only SMS
- Amounts spoken in Bengali numerals and lakh/crore convention (ADR 0012)
- Limits explained *before* she travels, not at the counter (ADR 0007)
- Scam warnings spoken, concrete, and dismissible
- Agent-assisted mode that logs the agent's identity on every action

---

## P3 — Tanvir Ahmed · the freelancer

**26 · software developer · Dhaka · earns in USD from overseas clients**

The population created by the PayPal gap. Cannot hold a PayPal balance or send
internationally, because Bangladesh restricts outbound transactions; Xoom is inbound and
non-commercial only. Receives through a patchwork of Payoneer, wire transfers and
occasionally a friend abroad.

**Pain**
- No clean, legal, low-friction path for commercial inbound payment
- Wire fees are brutal on small invoice amounts
- Documentation burden for declaring foreign income
- No way to pay for foreign SaaS subscriptions he needs to do the work

**Design consequences**
- Commercial-inbound is a distinct product surface with distinct compliance treatment
- Documentation and declaration support as a feature, not a PDF the user must interpret
- Honest limits: **we cannot solve outbound.** That is a capital-account policy question,
  not a product question, and claiming otherwise would be dishonest (see report §10)

---

## P4 — Shirin Akter · the agent

**34 · runs a mobile-recharge shop that doubles as an MFS agent point · peri-urban Bogura**

Handles 30–60 transactions a day. Her float is her working capital and running out of it
mid-afternoon costs her the rest of the day's business.

**Pain**
- Float management is guesswork
- Customers arrive for amounts she cannot pay out
- Commission structure is opaque
- She is the human face of every failure she did not cause

**Design consequences**
- Agent mode with float forecasting, so she can rebalance before she runs dry
- Advance notice of large inbound payouts heading to her point
- Transparent commission
- Agent identity logged on assisted transactions — protects honest agents as much as it
  deters dishonest ones

---

## P5 — Nusrat Jahan · the compliance officer

**31 · former bank AML analyst · Dhaka**

Reviews escalated alerts. Her queue is the throughput ceiling of the entire system
(ADR 0010).

**Pain**
- Alert volume dominated by false positives
- Each investigation means pulling context from four systems by hand
- Justifying decisions to a supervisor months later from memory and fragments
- Genuine fear of missing something real inside the noise

**Design consequences**
- Evidence bundles that assemble the context she would have gathered anyway
- **Contradictory evidence shown explicitly**, so the bundle informs rather than persuades
- Graph subgraph as a diagram — far more legible in a case file than a score
- Decision rationale captured at decision time, never reconstructed
- Blind re-adjudication protects her too: it is evidence she was deciding, not stamping

---

## What the personas jointly require

| Requirement | Driven by |
|---|---|
| Landed-amount-first UI | P1 |
| Bangla-first, voice-capable, IVR-reachable | P2 |
| Limits as pre-transaction constraints | P1, P2, P4 |
| Agent tooling and identity logging | P4, P2 |
| Officer evidence bundles with contradictions | P5 |
| Honest statements about what we cannot do | P3 |
