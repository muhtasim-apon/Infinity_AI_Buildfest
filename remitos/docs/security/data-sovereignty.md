# Data Sovereignty

> Congress §11.1 scores data sovereignty as part of a full judging component, and §15
> requires "respect for governance, compliance, and ownership". This document states what
> we do, how it is enforced, and what it costs us.

## 1. The position

**Personal, identity and financial data belonging to Bangladeshi users is processed and
stored inside Bangladesh, and does not leave.**

This is not a marketing stance. A remittance recipient in a rural upazila has no
practical recourse if her identity data is mishandled in a jurisdiction she has never
visited, under a legal system she cannot access. Sovereignty here is about who bears the
consequence of a breach, and it is not us.

## 2. Classification and residency

| Class | Examples | Residency | May reach an external LLM? |
|---|---|---|---|
| **C1 Identity** | NID number, passport, biometric template, address | Bangladesh only | **Never** |
| **C2 Financial** | Amounts, account numbers, ledger entries, transfer history | Bangladesh only | **Never** |
| **C3 Behavioural** | Device, session, in-app events | In-country | **Never** |
| **C4 Derived** | Risk scores, model features, embeddings of C1–C3 | In-country | **Never** |
| **C5 Public** | FX rates, published fee benchmarks, circulars, ISO specs | Unrestricted | Yes |

**C4 includes embeddings.** An embedding of a personal record is a lossy but real
representation of it, and treating vectors as anonymous is a common and serious error.

## 3. How the boundary is enforced

Policy without a mechanism is a wish. Four mechanisms, in order of reliability:

### 3.1 Tokenisation proxy

Every call to an external model passes through a proxy that replaces identifiers with
opaque tokens and re-hydrates the response inside the boundary.

```
inside  │ "Rahima Begum, NID 1990123456789, BDT 45,000 from Riyadh, 3rd transfer this week"
        │    ↓ tokenise
outside │ "<PERSON_A>, <ID_1>, <AMOUNT_1> from <CORRIDOR_SA>, 3rd transfer this week"
        │    ↓ model reasons about structure and typology
inside  │    ↓ re-hydrate
```

The external model reasons about *pattern*, which is what it is genuinely good at. It
never sees identity, which it does not need in order to say "this frequency and amount
pattern resembles structuring".

### 3.2 Egress filter

A filter in front of every external call pattern-matches NID formats, Bangladeshi phone
numbers, account-number shapes and known-name lists. **A match fails the request and
raises a security event.** It does not warn and proceed.

### 3.3 CI enforcement

The same detector runs in CI against every prompt template and every fixture. A developer
cannot merge a template that would leak, and cannot merge a test fixture containing real
PII.

### 3.4 In-boundary model hosting

Workloads that can run locally, do — and these are specified as in-boundary in
`.env.example`:

| Workload | Hosting |
|---|---|
| Embeddings (`multilingual-e5-large`) | **In-boundary**, self-hosted |
| Reranking (`bge-reranker-v2-m3`) | **In-boundary** |
| Bangla ASR / TTS | **In-boundary** — voice is biometric |
| Tabular ML (fraud, AML, cost, FX) | **In-boundary** |
| Frontier reasoning over tokenised structure | External, tokenised only |

## 4. User ownership

| Right | Implementation |
|---|---|
| Know what is held | In-app data summary, in Bangla, in plain words |
| Export | Machine-readable export on request |
| Correct | Self-service where safe; assisted where it affects KYC |
| Delete | Honoured **except** where AML retention law requires retention — and the user is told which data is retained and why, rather than receiving a silent partial deletion |
| Understand automated decisions | Reason code plus plain-Bangla explanation for every money-affecting decision |
| Appeal | Human review route, visible in the app |

Retention requirements override deletion requests. Saying so clearly is more honest than
a "right to be forgotten" claim the system cannot actually keep.

## 5. What this costs us

Stating the cost is part of stating the position honestly:

- In-boundary GPU hosting for embeddings, reranking and ASR costs more than API calls
- The tokenisation proxy adds latency and engineering complexity
- Tokenised context measurably degrades some reasoning quality — measured in
  `ml/evaluation/`, not assumed acceptable
- Some managed services cannot be used at all
- In-country DR requires geographically separated in-country capacity

Accepted. A sovereignty claim that costs nothing is usually a sovereignty claim that
isn't being kept.

## 6. Cross-border reality

Cross-border payments are inherently cross-border in *data* as well as money: a partner
in Riyadh must receive beneficiary details to settle. We therefore distinguish:

- **Transaction data required for settlement** — shared with the specific partner, under
  the FATF Travel Rule, minimised to what the rule requires, logged per disclosure
- **Everything else** — never shared

Travel Rule data sharing is a legal obligation, not a residency breach, and every
disclosure is recorded in the audit log with its legal basis.
