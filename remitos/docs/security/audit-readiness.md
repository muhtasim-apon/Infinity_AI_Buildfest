# Audit Readiness

Idea to Unicorn judges assess governance and responsible AI directly (§11.1). More
substantially: a payments institution must be able to answer a supervisor's question
about any single transaction, years later, with evidence rather than recollection.

## 1. The standard

For **any** transaction, at **any** past date, the system must reconstruct:

| Question | Source |
|---|---|
| What happened, in order? | Event stream, by `correlation_id` |
| Who or what decided, at each step? | Audit log: actor, human or service |
| **What information did the decider have?** | Evidence-bundle snapshot, stored with the decision |
| Which rule applied? | RAG citations with effective dates |
| Which model version ran, and what did it output? | Prediction record with version and SHAP attribution |
| What did the money do? | Double-entry ledger journal |
| Who reviewed it, and why did they decide that? | Human-gate record with rationale |

The bolded row is the one most systems cannot answer, and it is the one that determines
whether a decision was *reasonable*. A decision can only be judged against the evidence
actually in front of the decider at the time — which is why the bundle is **snapshotted**,
not re-derived later from data that has since changed.

## 2. Audit log properties

- **Append-only.** No update, no delete, enforced at the storage layer.
- **Hash-chained.** Each entry carries its predecessor's digest; chain digests are
  periodically anchored externally, so tampering becomes detectable rather than merely
  discouraged.
- **Complete.** Every state transition, decision, disclosure, and every access to class
  C1 or C2 data.
- **Queryable.** Indexed by correlation id, user, transfer, actor, time.
- **Retained** per regulatory requirement, in-country.

## 3. What is logged

| Category | Includes |
|---|---|
| Transaction lifecycle | Request, quote, route decision with reason codes, compliance verdict, ledger postings, payout attempts **including failures**, settlement |
| Decisions | Model predictions with version and attribution; RAG citations; human decisions with rationale and evidence snapshot |
| Access | Every read of C1/C2 data, with actor and stated purpose |
| Administration | Limit changes, fee changes, model promotions, permission changes — all under dual control |
| Security | Auth events, egress-filter blocks, suspected prompt injection, rate-limit trips |
| AI operations | Agent runs with tool calls, budget consumption, escalations, refusals |

Failures are logged as fully as successes. An audit trail that records only what worked
is useless at precisely the moment it is needed.

## 4. The generated audit report

`services/audit` assembles a report covering:

| Section | Content |
|---|---|
| Security | Posture, open findings, incident summary |
| Privacy & residency | Attestations, egress-filter statistics, disclosure log |
| Compliance | Screening coverage, alert volumes, STR counts, SLA adherence |
| Governance | Human-gate volumes, override counts, **blind re-adjudication agreement rates** |
| Responsible AI | Model versions in force, fairness metrics **per group**, drift status, refusal rates |
| Operational readiness | SLO attainment, DR test results |
| Open risks | The register, with owners — never empty |

**Fairness metrics appear per group, never aggregated.** An aggregate conceals exactly the
disparity the report exists to surface. A report that always looks clean is not an audit,
it is a brochure — and the open-risk section is what distinguishes the two.
