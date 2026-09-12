# AML / KYC / CFT Policy

> Specification for a system in design. Any real deployment requires approval by
> Bangladesh Bank and the Bangladesh Financial Intelligence Unit (BFIU), and a licensed
> operating entity. See `docs/product/regulatory-path.md`.

## 1. Customer Due Diligence

| Tier | Trigger | Requirements |
|---|---|---|
| **Simplified (SDD)** | Low value, low risk, payout to an existing verified wallet | Name, phone, device binding |
| **Standard (CDD)** | Default for all senders | Government ID with OCR + liveness, address, source-of-funds category, sanctions screening |
| **Enhanced (EDD)** | High value, high-risk corridor, PEP, adverse media, or graph proximity to a flagged entity | Documentary source of funds, senior approval, ongoing enhanced monitoring |

Re-verification on: document expiry, material behaviour change, adverse-media hit, or a
periodic cycle by risk tier.

**Design note.** KYC friction is one of the most common reasons a user abandons a formal
channel and returns to hundi. The response is not to weaken due diligence — it is to make
it fast (OCR extraction rather than typing), assisted (agent-assisted capture), and honest
about how long it will take. A ten-minute clear answer beats a two-day silence.

## 2. Screening

| Check | When | Source |
|---|---|---|
| Sanctions (OFAC, UN, EU, UK-HMT) | Onboarding, every transfer, daily re-screen of the whole book | n8n workflow 02 |
| PEP | Onboarding and periodically | Commercial data provider |
| Adverse media | EDD and periodically | Provider plus research agent |

Matching is deterministic and tuned: exact, phonetic, transliteration-aware and fuzzy.
**Semantic similarity is not used for name screening** — it is the wrong tool and produces
both misses and unexplainable hits.

Bangla–English transliteration is non-deterministic; the same name legitimately romanises
several ways (রহিমা → Rahima / Rohima / Rahema). Exact string matching would both miss
real hits and generate unfair false positives, so fuzzy plus phonetic matching is
mandatory, with thresholds tuned against a labelled set and reviewed quarterly.

**Every sanctions hit goes to a human. No exceptions, regardless of model confidence.**

## 3. Transaction monitoring

**Real-time** (synchronous, sub-second): velocity, amount deviation from the user's own
baseline, new-beneficiary risk, sanctions, device and geo anomaly.

**Near-real-time** (event-driven): AML risk model, graph network signals, structuring
detection, typology matching.

**Periodic** (batch): cross-user pattern discovery, agent-concentration analysis, dormant
account reactivation review.

Thresholds are configuration with effective dates, never hard-coded. Every change is
audited with a named approver.

## 4. Reporting

| Report | Trigger | Route |
|---|---|---|
| Suspicious Transaction Report (STR/SAR) | Officer determination | BFIU, within the prescribed window |
| Cash Transaction Report | Threshold breach | BFIU |
| Travel Rule payload | Transfer at or above `TRAVEL_RULE_THRESHOLD_USD` | Beneficiary institution, with the transfer |
| Regulatory returns | Scheduled | Bangladesh Bank, from `services/reporting` |

The compliance agent may **draft** an STR narrative (authority L1). An officer reviews,
edits and files it. The agent never files.

## 5. Record keeping

Retention per BFIU requirement, in-country, immutable, retrievable within the mandated
period. Records include the decision, the evidence presented to the decision-maker, the
model version in force, and the retrieved citations — see ADR 0009 and
`services/audit/`.

## 6. Governance

| Role | Responsibility |
|---|---|
| Compliance Officer (named) | Owns the programme; final authority on escalations |
| MLRO | Files reports to BFIU |
| Model owner | Accuracy, fairness and drift of AML models |
| Internal audit | Independent periodic review, including blind re-adjudication |

**Blind re-adjudication** is the control that keeps the human gate real. A random sample
of decisions — including ones the model passed — is re-decided by a senior officer without
sight of the original decision or the model score. Sustained agreement with the model on
cases the officer would independently have decided differently is evidence of
rubber-stamping, and is treated as a control failure rather than as validation.
