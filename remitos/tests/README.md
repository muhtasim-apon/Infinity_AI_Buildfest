# Tests

| Path | Scope |
|---|---|
| `e2e/` | Full user journeys J1 to J4 against a composed stack |
| `load/` | k6 scenarios; the binding target is quote p95 under 400 ms (FR-01) |
| `contract/` | Pact consumer/provider verification against `packages/api-contracts/` |
| `security/` | Automated checks incl. the PII egress detector and prompt-template scan |

**No test in this repository has been executed.**

## Test cases that must exist before launch

| Case | Why |
|---|---|
| J3 split proposal at exactly Tk 30,000 and Tk 30,001 | The boundary of the constraint that defines the product |
| Outbox double-submit after a crash mid-flight | Idempotency key must prevent a double-send. This is the highest-consequence bug in the client |
| Quote served from cache while offline | Must render as stale and must never be presented as binding |
| Bangla rendering at every font scale, incl. elder mode | Conjunct rendering and overflow |
| Egress filter blocks a prompt containing an NID pattern | ADR 0011 enforcement, not aspiration |
| Agent attempts an L3 tool | Must be impossible - the tool is absent from the registry |
| RAG returns NOT_FOUND below citation threshold | Cite-or-refuse, verified rather than assumed |
| Superseded circular is not retrieved for a past-dated query | Stale-rule leakage gate |
| Ledger conservation under concurrent posting | Sum of entries invariantly zero |
| Fairness suite per group on every risk model | Release gate, not a report |
