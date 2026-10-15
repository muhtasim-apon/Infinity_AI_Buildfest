# tests/

Strategy and rationale: [`../docs/testing/test-strategy.md`](../docs/testing/test-strategy.md) · tool links:
[`../docs/testing/test-links.md`](../docs/testing/test-links.md).

**Status:** test cases are designed; bodies are stubs marked `pytest.mark.skip("stub")` (or `test.fixme`
in Playwright) so the suite never reports a false pass. Remove the skip when implementing.

| Folder | Type | Owner | Runs |
|---|---|---|---|
| `unit/` | unit | everyone (own code) | every PR |
| `whitebox/` | branch-coverage tests of safety-critical modules | Apon, Salwa | every PR |
| `blackbox/` | API contract, equivalence & boundary, Schemathesis, Newman | Apon | every PR / nightly |
| `integration/` | API + Postgres/pgvector + Storage | Apon, Taeen | nightly |
| `timeout/` | budgets, cold start, slow dependencies | Apon | nightly |
| `concurrency/` | races, idempotency, semaphore, k6 load | Apon | nightly / pre-release |
| `security/` | RLS, IDOR, auth, uploads, HMAC, LLM red-team | Apon, Salwa | every PR + pre-release |
| `ml/` | accuracy gates, robustness, parity, preprocessing | Taeen | per model release |
| `e2e/` | Playwright journeys, both locales, phone viewport, a11y | Sara | nightly |
| `manual/` | test-case sheets, device matrix, usability protocol | Sara, Raisa | each milestone |
| `n8n/` | workflow fixtures and expected outcomes | Apon, Taeen | on workflow change |
| `fixtures/` | synthetic data, attributed sample images, malicious samples | all | — |

Run (once implemented): `pytest tests/unit tests/whitebox --cov=services/api/app --cov-branch`.
