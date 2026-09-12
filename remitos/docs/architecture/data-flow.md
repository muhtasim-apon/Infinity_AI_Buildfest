# Data Flow — how money and data actually move

## 1. The end-to-end send, as a sequence

```mermaid
sequenceDiagram
    autonumber
    participant S as Sender (Flutter)
    participant GW as gateway
    participant ID as identity
    participant FR as fraud
    participant RT as routing-engine
    participant FX as fx-service
    participant CP as compliance
    participant RG as rag-service
    participant OR as payments-orchestrator
    participant LD as ledger
    participant PR as Partner rail
    participant NT as notification
    participant AU as audit

    S->>GW: POST /quotes {corridor, amount, payout_pref}
    GW->>ID: verify session + device binding
    GW->>FR: pre-transaction risk score
    FR-->>GW: risk 0.12 (low)
    GW->>RT: request routes
    RT->>FX: current rate + forecast window
    RT->>RT: generate candidates, predict cost & ETA
    RT->>RT: filter by BB ceilings + partner liquidity
    RT-->>GW: ranked RouteDecision[] + Bangla rationale
    GW-->>S: quote shown (landed BDT, ETA, why)

    S->>GW: POST /transfers {quote_id}
    GW->>CP: screen sender + beneficiary
    CP->>RG: retrieve applicable rules (cited)
    RG-->>CP: passages + citations
    CP-->>GW: ALLOW / REVIEW / BLOCK + reason + citation
    alt REVIEW
        CP->>NT: escalate to human officer
        NT-->>S: "under review" (Bangla), SLA shown
    end
    GW->>OR: begin saga
    OR->>LD: reserve (double-entry, idempotency key)
    OR->>PR: execute payout leg
    PR-->>OR: accepted / failed
    alt failed
        OR->>LD: compensating entry
        OR->>RT: re-route to next-best path
    end
    OR->>LD: commit
    OR->>NT: notify sender + recipient (SMS/IVR if no data)
    OR->>AU: emit immutable audit event
    AU-->>AU: hash-chain append
```

**The step that does not exist in competing products is 9–11**: candidate generation,
ML cost/ETA prediction, and constraint filtering *before* the user sees a price. Most
products show one price from one rail and discover the constraint failure later.

## 2. Compliance decision flow

```mermaid
flowchart TD
    A[Transfer request] --> B{Sanctions screen<br/>OFAC/UN/EU/UK-HMT}
    B -->|hit| Z[BLOCK + file report]
    B -->|clear| C{Amount >= Travel Rule<br/>threshold?}
    C -->|yes| D[Attach originator +<br/>beneficiary data]
    C -->|no| E[AML risk model]
    D --> E
    E --> F{score}
    F -->|< 0.40| G[ALLOW<br/>reason code + citation]
    F -->|0.40 - 0.70| H[Enhanced checks<br/>RAG-grounded agent]
    F -->|> 0.70| I[HUMAN GATE<br/>officer decides]
    H --> J{resolved?}
    J -->|yes| G
    J -->|no| I
    I --> K[Decision recorded with<br/>officer identity + rationale]
    G --> L[Audit event]
    K --> L
    Z --> L
```

Every terminal state writes an audit event carrying: the model version, the retrieved
citations, the reason code, and — where a human decided — who decided and why. This is
what makes the `/audit` report generatable rather than reconstructed.

## 3. Knowledge (RAG) ingestion flow

```mermaid
flowchart LR
    A1[Bangladesh Bank circulars] --> P[n8n 07<br/>circular watcher]
    A2[FATF guidance] --> P
    A3[Sanctions lists] --> Q[n8n 02<br/>list sync]
    A4[ISO 20022 specs] --> P
    A5[Partner corridor rules] --> P

    P --> CH[Chunker<br/>structure-aware]
    CH --> EM[Embedding<br/>multilingual e5]
    EM --> VDB[(Qdrant)]
    CH --> NER[Entity extraction]
    NER --> GDB[(Neo4j)]
    Q --> SDB[(Sanctions store)]

    VDB --> R[Hybrid retrieval<br/>dense + BM25]
    GDB --> R
    R --> RR[Reranker]
    RR --> GU[Citation guardrail]
    GU --> OUT[Grounded answer<br/>or explicit 'not found']
```

**The guardrail is non-negotiable in a regulated domain.** If no retrieved passage
clears the citation threshold, the service returns *not found* and the request escalates
to a human. It never generates an ungrounded compliance opinion. A confident wrong
answer about an AML rule is worse than no answer.

## 4. Data classification and residency

| Class | Examples | Residency | Encryption | Retention |
|---|---|---|---|---|
| **C1 Identity** | NID number, passport, biometric template | Bangladesh only, never leaves | Field-level AES-256, separate key | Per BFIU requirement |
| **C2 Financial** | Amounts, beneficiary account, ledger entries | Bangladesh only | At-rest AES-256 | 5+ years, regulatory |
| **C3 Behavioural** | Device, session, in-app events | In-country preferred | At-rest | 24 months |
| **C4 Derived** | Risk scores, model features | In-country | At-rest | Model lifetime |
| **C5 Public** | FX rates, corridor fee benchmarks, circulars | Unrestricted | — | Indefinite |

**Rule:** classes C1–C4 never enter a third-party LLM prompt. Where an LLM is needed on
a record, the record is tokenised first and only C5 plus tokens leave the boundary. See
`docs/security/data-sovereignty.md` for the enforcement mechanism.

## 5. Event catalogue (Kafka topics)

| Topic | Emitted by | Consumed by | Key |
|---|---|---|---|
| `transfer.requested` | gateway | fraud, compliance, audit | `transfer_id` |
| `transfer.quoted` | routing-engine | analytics, audit | `quote_id` |
| `compliance.decided` | compliance | orchestrator, audit, reporting | `transfer_id` |
| `ledger.entry.posted` | ledger | reporting, reconciliation | `entry_id` |
| `payout.initiated` | orchestrator | notification, audit | `transfer_id` |
| `payout.settled` | orchestrator | ledger, reconciliation, notification | `transfer_id` |
| `payout.failed` | orchestrator | routing-engine, notification, audit | `transfer_id` |
| `model.prediction.made` | model serving | drift monitor, audit | `prediction_id` |
| `model.drift.detected` | n8n 09 | on-call, model registry | `model_name` |

All events are versioned, schema-registered in `data/schemas/`, and carry a
`correlation_id` that ties a user tap to every downstream consequence.
