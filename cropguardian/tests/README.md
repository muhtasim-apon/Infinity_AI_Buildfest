# tests/ — test-case specifications

**Status: no test code yet.** Each folder's README lists the test cases (IDs, inputs, expected results)
that the team turns into test files while implementing. Strategy: [`../docs/testing/test-strategy.md`](../docs/testing/test-strategy.md) ·
security testing per platform: [`../docs/testing/security-testing-guide.md`](../docs/testing/security-testing-guide.md) ·
tool links: [`../docs/testing/test-links.md`](../docs/testing/test-links.md).

| Folder | Type | Owner | When it runs |
|---|---|---|---|
| [`unit/`](unit/README.md) | unit | each developer | every PR |
| [`whitebox/`](whitebox/README.md) | branch coverage of safety-critical modules | Apon, Salwa | every PR |
| [`blackbox/`](blackbox/README.md) | partitions, boundaries, Schemathesis, Newman | Apon | every PR / nightly |
| [`integration/`](integration/README.md) | API + DB + storage | Apon, Taeen | nightly |
| [`timeout/`](timeout/README.md) | budgets, cold start, slow dependencies | Apon | nightly |
| [`concurrency/`](concurrency/README.md) | races, idempotency, load (k6) | Apon | pre-release, staging only |
| [`security/`](security/README.md) | auth, RLS, IDOR, uploads, webhooks, LLM red-team | Apon, Salwa | every PR + pre-release |
| [`ml/`](ml/README.md) | accuracy gates, robustness, parity | Taeen | per model release |
| [`e2e/`](e2e/README.md) | Playwright journeys + accessibility | Sara | nightly + deployed URLs |
| [`manual/`](manual/functional-test-cases.md) | manual sheets, device matrix, usability | Sara, Raisa | each milestone |
| [`n8n/`](n8n/README.md) | workflow tests and synthetic monitor | Apon, Taeen | on workflow change |
| [`fixtures/`](fixtures/README.md) | synthetic data rules | all | — |

Rule: a case is "done" only when its test exists and passes; no result is reported before that.
