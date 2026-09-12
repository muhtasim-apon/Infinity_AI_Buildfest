# Threat Model (STRIDE)

**Scope:** the whole RemitOS system — Flutter clients, USSD/IVR path, 14 services, the
AI/RAG layer, n8n automation, and the data stores.

**Assumed adversaries:** opportunistic fraudsters · organised laundering networks
(the hundi ecosystem has scale, money and existing agent relationships) · malicious
insiders · nation-state-capable actors targeting a national-scale financial system ·
compromised partners.

---

## 1. Trust boundaries

| # | Boundary | Crossing |
|---|---|---|
| TB1 | User device ↔ gateway | Untrusted client; assume it is fully compromised |
| TB2 | Gateway ↔ internal services | Authenticated, mTLS |
| TB3 | Services ↔ partner rails | Third-party, assume unreliable and potentially hostile |
| TB4 | Services ↔ external LLM APIs | **Data-residency boundary (ADR 0011)** |
| TB5 | n8n ↔ application APIs | Automation plane, high-value credentials |
| TB6 | Ingested documents ↔ RAG | **Untrusted content entering a reasoning system** |
| TB7 | Officer console ↔ services | Privileged human access |

TB6 is the boundary most systems forget exists.

---

## 2. STRIDE analysis

### Spoofing

| Threat | Mitigation |
|---|---|
| Credential stuffing | Rate limiting, breach-password checks, device binding, step-up auth |
| SIM-swap → OTP takeover | Device binding as primary; SMS OTP is **not** sufficient alone for high-value; cooling-off on device change |
| Agent impersonating a user | Agent-assisted mode requires the user's own biometric or PIN; agent identity logged on every action |
| Forged identity documents | Liveness + issuer verification; OCR is extraction only, never authentication (see doc-intelligence card) |
| **Voice cloning against IVR** | **Voice is never a credential** (bangla-nlu card) |
| Partner API spoofing | mTLS, pinned certificates, signed webhooks |

### Tampering

| Threat | Mitigation |
|---|---|
| Client-side amount manipulation | Server is authoritative; quote is server-signed and bound to a quote id |
| Replay of a transfer request | Idempotency keys, nonce, short-lived signed quotes |
| Ledger tampering | Append-only, hash-chained journal; corrections are compensating entries (ADR 0009) |
| Audit-log tampering | Append-only with periodic external anchoring of chain digests |
| **Poisoning the RAG corpus** | Source allow-list, signature/checksum verification on ingest, human review of new sources, per-document provenance |
| Model poisoning via feedback | Feedback is a candidate label, never a training label without adjudication |

### Repudiation

| Threat | Mitigation |
|---|---|
| User disputes a transfer they authorised | Signed request + device attestation + full audit chain |
| Officer disputes a decision | Audit records **who, when, what they saw, and why** (ADR 0010) |
| Partner disputes settlement | Independent double-entry ledger + daily reconciliation (n8n 06) |

### Information disclosure

| Threat | Mitigation |
|---|---|
| **PII in an LLM prompt** | Tokenisation proxy + **egress filter that fails the request**, plus a CI check on prompt templates (ADR 0011) |
| Cross-tenant data leak via agent | Per-request authorisation on every tool call; agents cannot widen their own scope |
| Notification preview leaking on a shared device | No amounts or names in lock-screen previews |
| Support agent over-disclosure | Support agent reports recorded reasons only; never speculates on compliance decisions |
| Backup exfiltration | Encrypted backups, separate key custody, restore drills |
| Graph database as a relationship map | Highest-sensitivity store: network-isolated, access-logged, read-only for agents |

### Denial of service

| Threat | Mitigation |
|---|---|
| Quote-endpoint flood | Per-user and per-IP rate limits, cost-aware throttling (quotes invoke ML) |
| **LLM cost exhaustion** | Per-tenant token budgets; agent runs bounded by steps, tokens and wall-clock |
| Partner outage cascade | Circuit breakers, bulkheads, automatic re-route |
| Intelligence-layer outage | Graceful degradation ladder — the system keeps settling money |

### Elevation of privilege

| Threat | Mitigation |
|---|---|
| **Prompt injection escalating agent authority** | Authority enforced **at the tool boundary**, not by prompt. L3 tools are absent from the agent registry entirely |
| Injection via an ingested document | Retrieved content is delimited and declared non-instructional; suspected injection halts the run and quarantines the document |
| Insider limit override | L3 human gate + dual control on limit changes + audit |
| Service-account sprawl | Least privilege per service; short-lived credentials; no shared accounts |

---

## 3. AI-specific threats

| Threat | Why it matters here | Mitigation |
|---|---|---|
| **Prompt injection via RAG** | A circular PDF is attacker-influenceable if sourcing is sloppy | Source allow-list; content as data; injection detection; quarantine |
| Jailbreak to obtain another user's data | Agents hold real data access | Authorisation per tool call, not per session |
| Model inversion / membership inference | Training data is financial PII | Differential-privacy-aware training for high-risk models; no user-identifiable model outputs |
| Adversarial evasion of fraud scoring | Direct financial motive | Ensembles, graph signals, continuous retraining, human review band |
| Over-reliance on model output | The quiet failure: an officer rubber-stamps the model | Evidence bundles present **contradictions explicitly**; periodic blind re-adjudication measures whether officers are actually deciding |
| Degraded model presented as authoritative | Silent quality loss | Degradation ladder surfaces its own state to users and officers |

The "over-reliance" row is the one most likely to be underrated. A human gate that
approves 99 % of what the model proposes is not a control — it is a rubber stamp with a
name attached, and blind re-adjudication is how that gets detected.

---

## 4. Residual risks (accepted, with owner)

| Risk | Why accepted | Owner |
|---|---|---|
| A compromised partner can mis-settle | We cannot control partner security; limited by reconciliation and exposure caps | Backend Lead |
| Social engineering of the end user | Cannot be eliminated technically; mitigated by warnings and second-channel confirmation | Product |
| Novel laundering typologies | Unknowable in advance; mitigated by anomaly detection and officer expertise | Compliance |
| Nation-state adversary | Out of proportion to project resources; documented honestly rather than pretended away | Team Leader |

Stating residual risk with an owner is itself a control. A threat model with no residual
risks has not been finished.
