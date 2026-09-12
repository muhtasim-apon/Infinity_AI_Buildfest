# Research Note 02 — Bangladesh Market, Rails & Constraints

Access date for all rows: **2026-09-12**.

## 2.1 Mobile Financial Services (MFS) landscape

| Metric | Value | Source |
|---|---|---|
| Licensed MFS providers | **14** | Bangladesh Bank / industry reporting [R12] |
| Daily MFS value moved | ≈ **Tk 6,000 crore/day** (~USD 500 m) | The Daily Star [R13] |
| bKash market share | **39.9 %** | [R13] |
| Nagad market share | **18.1 %** | [R13] |
| Rocket market share | **11.7 %** | [R13] |
| bKash active users | **4.20 crore** (42.0 m) | [R13] |
| Nagad active users | **2.82 crore** (28.2 m) | [R13] |
| Registered MFS accounts | exceed the national population | [R13] |
| MFS industry age | launched 2011 | [R14] |

> **Interpretation for the report:** registered accounts > population proves that
> *account registration is not the bottleneck*. Active-vs-registered divergence
> (42 m active on 39.9 % share) is the real inclusion story. Our KPI must be
> **active usage**, never registrations.

## 2.2 Regulatory transaction ceilings (Bangladesh Bank, Payment Systems Dept., re-fixed Mar 2025)

| Limit | Daily | Monthly |
|---|---|---|
| Cash-in (agent point) | Tk 50,000 | Tk 300,000 |
| Cash-out (agent point) | Tk 30,000 | Tk 200,000 |
| P2P transfer | Tk 50,000 | Tk 300,000 |
| Max wallet balance | — | Tk 500,000 |

Source: Bangladesh Bank circular as reported by TBS / BSS [R15][R16].

> **Design consequence:** any remittance payout above Tk 30,000/day cannot clear to a
> single MFS wallet in one movement. The routing engine must therefore treat
> *payout-capacity* as a first-class routing constraint, and be able to split or
> re-route to a bank account. Most competitor UX simply fails the user here.

## 2.3 Interoperability — Binimoy / IDTP

| Fact | Detail | Source |
|---|---|---|
| What | National Interoperable Digital Transaction Platform linking banks ↔ MFS ↔ PSPs | [R17] |
| Launched | 13 November 2022 | [R17][R18] |
| MFS→MFS cost | Tk 5 per thousand (0.5 %) | [R19] |
| MFS→bank cost | Tk 10 per thousand (1.0 %) | [R19] |
| MFS→PSP cost | Tk 5 per thousand (0.5 %) | [R19] |

> Binimoy is the domestic interoperability rail. It exists, it is under-used, and it is
> the natural last-mile settlement fabric for a cross-border orchestration layer.
> We build **on** it, not against it.

## 2.4 The hundi problem (informal channel leakage)

| Metric | Value | Source |
|---|---|---|
| Estimated share of inflows via informal hundi | ≈ **49 %** (formal ≈ 51 %) | academic review in *Journal of Economic Criminology* [R20] |
| Estimated annual value lost to hundi | ≈ **USD 7.8 bn** (≈ Tk 75,000 crore) | CID investigation reporting [R21] |
| Short-window loss | ≈ Tk 25,000 crore over four months | The Daily Star [R22] |
| Reserve shortfall attributable | ≈ 19.2 % disparity between actual and potential reserves | [R20] |
| Identified channel abuse | ≥ 5,000 MFS agents implicated in laundering flows | [R21] |

> **This is the single largest addressable pool in the entire project.** Every formal
> product in Bangladesh competes for the 51 %. The 49 % is won by beating hundi on its
> own terms: rate, speed, doorstep payout, and zero paperwork. Estimates vary widely by
> methodology — the report must present this as a *range with attribution*, not a fact.

## 2.5 Connectivity and device base (BTRC, June 2026)

| Metric | Value | Source |
|---|---|---|
| Internet subscribers | **135.94 m** | BTRC via press [R23] |
| Of which mobile internet | **120.84 m** (88.9 %) | [R23] |
| Active mobile subscribers | **189.83 m** | [R23] |
| Grameenphone / Robi / Banglalink / Teletalk | 86.59 m / 58.57 m / 37.86 m / 6.80 m | [R23] |
| Smartphone adoption | 63.3 % → **72.8 %** (2023 → 2025) | GSMA-referenced reporting [R24] |

> **Design consequence:** 189.83 m mobile subscribers vs 120.84 m mobile-internet users
> leaves roughly **69 m connections without mobile data**. A remittance product that is
> smartphone-and-data-only is structurally excluded from the poorest quartile of
> recipients. This is why USSD/IVR fallback is in scope, not a nice-to-have.

## 2.6 The PayPal gap

| Fact | Detail | Source |
|---|---|---|
| Standard PayPal accounts for BD residents | **Not available** — cannot register, hold balance, or send | [R25][R26] |
| Root cause | Bangladesh's restrictions on **outbound** current/capital-account transactions are incompatible with PayPal's two-way model | [R25] |
| Xoom (PayPal subsidiary) | Inbound remittance to BD only; **non-commercial transfers only** — commercial use can trigger account termination | [R27][R28] |
| Freelancer consequence | Cannot receive commercial marketplace payouts natively | [R29] |
| Partial workaround | Payoneer–PayPal integration launched late 2025 for eligible BD freelancers | [R25] |

> **Why this belongs in the report:** the PayPal absence is the clearest proof that
> Bangladesh's problem is not technological but *regulatory-architectural* — the country
> is a receive-only node in the global money graph. Any honest "borderless money" thesis
> must state that and design within it rather than pretend it away.

---

## References

- [R12] Future Startup, State of MFS in Bangladesh — https://futurestartup.com/2025/05/06/the-state-of-mobile-financial-services-mfs-industry-in-bangladesh/
- [R13] The Daily Star, "Tk 6,000cr moves daily. But not every wallet is winning" — https://www.thedailystar.net/business/news/tk-6000cr-moves-daily-not-every-wallet-winning-4220811
- [R14] The Financial Express, competition landscape of the MFS industry — https://thefinancialexpress.com.bd/views/views/competition-landscape-of-the-mfs-industry-in-bangladesh-1669733150
- [R15] The Business Standard, MFS transaction limit re-fixed — https://www.tbsnews.net/economy/mfs-transaction-limit-refixed-daily-maximum-cash-tk50000-cash-out-tk30000-1103256
- [R16] BSS, BB re-fixes MFS transaction limit — https://www.bssnews.net/business/258749
- [R17] UNB, Binimoy IDTP — https://unb.com.bd/category/business/binimoy-interoperable-digital-transaction-platform-could-open-a-new-horizon-in-money-transfer/104331
- [R18] The Business Standard, Binimoy launch — https://www.tbsnews.net/economy/interoperable-digital-transaction-platform-binimoy-be-launched-sunday-530666
- [R19] Biniyog, guide to IDTP — https://www.biniyog.com.bd/blogs/interoperable-digital-transaction-platform-idtp
- [R20] *Impact of informal remittance channels in Bangladesh: the role of hundi*, ScienceDirect — https://www.sciencedirect.com/science/article/pii/S2949791423000301
- [R21] Prothom Alo, "Bangladesh loses remittance worth Tk 750b in hundi: CID" — https://en.prothomalo.com/bangladesh/53w9yack4a
- [R22] The Daily Star, "Tk 25,000cr lost to hundi in last four months" — https://www.thedailystar.net/news/bangladesh/news/remittance-tk-25000cr-lost-hundi-4-months-3114701
- [R23] BTRC subscriber statistics via press — https://rtvonline.com/english/amp/bangladesh/274247
- [R24] AMTOB industry statistics — https://www.amtob.org.bd/home/industrystatics
- [R25] nsave, Is PayPal available in Bangladesh — https://www.nsave.com/bangladesh/paypal
- [R26] The Business Standard, "PayPal in Bangladesh: What's holding it back?" — https://www.tbsnews.net/features/panorama/paypal-bangladesh-whats-holding-back-965116
- [R27] Xoom, send money to Bangladesh — https://www.xoom.com/bangladesh/send-money
- [R28] New Age, "Freelancers benefited little from Xoom launch" — https://www.newagebd.net/article/27151/article/35972
- [R29] The Financial Express, freelancers call for full PayPal — https://thefinancialexpress.com.bd/trade/with-growing-xoom-use-freelancers-cry-for-full-fledged-paypal-service-1519581459
