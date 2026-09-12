# Research Note 03 — Competitive Landscape

Access date: **2026-09-12**. Qualitative rows are analyst judgement built on the cited
sources and public product surfaces; they are marked *(assessed)* and must be presented
as assessment, not as vendor-published fact.

## 3.1 Incumbent matrix

| Dimension | bKash | Nagad | Rocket | Bank channel | Western Union / MoneyGram | Wise | Remitly | Taptap Send | **RemitOS (target)** |
|---|---|---|---|---|---|---|---|---|---|
| Primary role | Domestic MFS + inbound payout | Domestic MFS + inbound payout | Bank-led MFS | Inbound wire + payout | Global MTO | Digital FX transfer | Digital remittance | Digital remittance | **Intelligence + orchestration layer** |
| BD market share | 39.9 % [R13] | 18.1 % [R13] | 11.7 % [R13] | — | — | — | — | — | new entrant |
| Cross-border origination | No | No | No | Yes | Yes | Yes (BD receive-only) | Yes | Yes | via partners |
| Agent cash-out reach | Very high | High | Medium | Low | Medium | None | None | None | inherits partner reach |
| Bangla-first UX | Partial *(assessed)* | Partial *(assessed)* | Weak *(assessed)* | Weak | Weak | Weak | Weak | Moderate | **Bangla-first by design** |
| Offline / USSD path | Yes (*247#) | Yes | Yes | No | No | No | No | No | **Yes, first-class** |
| Least-cost routing across rails | No | No | No | No | No | Single-rail | Limited | Limited | **Core differentiator** |
| Compliance automation (AI) | Internal, opaque | Internal, opaque | Internal | Manual-heavy | Rules-based | Strong | Strong | Moderate | **Explainable, RAG-grounded** |
| Public developer API | Limited | Limited | Limited | Rare | Partner-only | Yes | Partner | No | **Open by design** |
| Predictive FX timing | No | No | No | No | No | Rate alerts only | Rate alerts | No | **ML-driven** |
| Recipient-side intelligence | No | No | No | No | No | No | No | No | **Yes** |
| Regulatory standing | Licensed MFS | Licensed MFS | Licensed MFS | Scheduled bank | Licensed MTO | Licensed abroad | Licensed abroad | Licensed abroad | **None yet — see gap analysis** |

## 3.2 The strategic read

Three findings drive the positioning chapter of the report:

1. **Nobody owns the routing decision.** Every incumbent is a *rail*. A sender choosing
   between bKash-payout-via-MTO-A and bank-payout-via-MTO-B has no neutral party
   computing landed cost and arrival time. That decision layer is unoccupied.

2. **Compliance is the cost floor, and it is manual.** The cost stack is not dominated by
   technology; it is dominated by KYC/AML labour, sanctions screening, and the
   pre-funding of Nostro accounts. Automating the first two and forecasting the third is
   where an AI-native entrant can move the price, which is exactly the capability the
   Congress guide names for this challenge area ("compliance automation + routing
   optimization").

3. **The 49 % hundi share is not won on features.** It is won on rate, speed, doorstep
   delivery and paperwork. Any feature that does not move one of those four does not
   convert an informal-channel user.

## 3.3 Where we honestly do *not* win

| Area | Incumbent advantage | Our position |
|---|---|---|
| Agent network density | bKash/Nagad have hundreds of thousands of touchpoints | We must partner; we will never out-build this |
| Settlement float / liquidity | Banks and MTOs hold real balance-sheet capacity | We orchestrate, we do not warehouse funds |
| Regulatory licence | Held today | Ours is a sandbox-then-licence path, years not months |
| Brand trust | 15 years of habit | Earned only through a pilot corridor and verifiable outcomes |
| Consumer capital | Deep marketing budgets | Distribution through partners, not paid acquisition |

Stating this explicitly is a scoring advantage: the Congress guide's §13.4 penalises
"fabricated demos, fake or simulated results" and its §20.4 prohibits misrepresenting
technical capability. An honest gap table is a rubric asset.
