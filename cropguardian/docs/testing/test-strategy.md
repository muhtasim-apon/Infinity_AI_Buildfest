# Test strategy

Owners: Apon (API, DB, security, load) · Taeen (ML) · Salwa (RAG, red-team) · Raisa (agent,
usability) · Sara (frontend, E2E, accessibility). Tests live in [`../../tests/`](../../tests/).
**Status: designed, not yet executed.**

## 1. Test pyramid & where each type lives

| Type | What it proves | Folder | Tools | When |
|---|---|---|---|---|
| Unit | functions behave in isolation | `tests/unit/` | pytest, Vitest | every PR |
| **Whitebox** | every branch of safety-critical code is exercised (abstain logic, validator, upload sanitiser, outbreak rules, HMAC) | `tests/whitebox/` | pytest + pytest-cov `--cov-branch`, Hypothesis | every PR (≥ 80 % branch, 100 % on `decision.py`, `validator.py`) |
| **Blackbox** | API behaves per contract without knowing internals — equivalence classes, boundaries | `tests/blackbox/` | Schemathesis (OpenAPI fuzz), Postman/Newman, pytest + httpx | every PR / nightly |
| Integration | API + real Postgres/pgvector + Storage emulator | `tests/integration/` | pytest, Docker Postgres, testcontainers | nightly |
| Contract | frontend ↔ API types match | `tests/blackbox/contract/` | openapi-typescript diff | every PR |
| **Timeout** | budgets enforced; cold start handled; LLM slow/failing | `tests/timeout/` | pytest + respx (mock delays), toxiproxy, k6 | nightly |
| **Concurrency** | no duplicate scans, no race in audit chain, semaphore works, idempotency | `tests/concurrency/` | pytest-asyncio + asyncio.gather, k6, Locust | nightly |
| Load / performance | p95 latency at target users on free instance | `tests/concurrency/k6/` | k6 | before freeze |
| Security | OWASP Top 10, LLM Top 10, RLS, IDOR, uploads | `tests/security/` | pytest, OWASP ZAP baseline, Bandit, pip-audit, npm audit, gitleaks | every PR + pre-release |
| ML | accuracy gates, robustness, slices, int8 parity | `tests/ml/` | pytest, NumPy | per model release |
| E2E | user journeys in a real browser, both locales, phone viewport | `tests/e2e/` | Playwright | nightly + pre-release |
| Accessibility | contrast, labels, keyboard | `tests/e2e/a11y.spec.ts` | @axe-core/playwright, Lighthouse | pre-release |
| **Manual** | exploratory, usability with farmers, device matrix | `tests/manual/` | test-case sheets | each milestone |
| **n8n** | synthetic monitors in deployed env; workflow tests | `tests/n8n/` + `automation/n8n/` | n8n schedules + webhook assertions | continuous after deploy |

## 2. Whitebox design (coverage-driven)
Targets and the branches that must each have a test:

| Module | Branches |
|---|---|
| `ml/decision.py` (abstain) | prob ≥ τ · prob < τ · OOD reject · exactly τ (boundary) · NaN/inf logits |
| `rag/validator.py` | valid · no citations · unknown citation id · dose not in chunk · banned ingredient · chemical without safety · invalid JSON |
| `security/upload.py` | JPEG · PNG · WebP · wrong magic bytes · > 5 MB · > pixel cap · truncated file · EXIF present |
| `services/outbreak.py` | below min reports · at min · weather favourable/unfavourable · abstained excluded · radius edge |
| `security/hmac.py` | valid · bad signature · stale timestamp · replayed nonce |
| `audit` chain | first row (no prev) · normal · tampered row detected |

Hypothesis property tests: softmax output sums to 1; temperature > 0 never increases max-prob
above the T=1 value when T > 1; coarse location rounding always within 0.005°.

## 3. Blackbox design (equivalence partitioning + boundary values)

| Input | Valid classes | Invalid classes | Boundaries |
|---|---|---|---|
| Image size | 1 KB – 5 MB | 0 B, > 5 MB | 5 MB, 5 MB + 1 B |
| Image type | JPEG, PNG, WebP | GIF, SVG, PDF, HTML renamed `.jpg` | — |
| Dimensions | 224–4096 px side | < 64 px, > pixel cap | 64, 4096 |
| Crop | `rice` | unknown, empty | — |
| Coarse lat/lon | inside Bangladesh box | outside, null for required | 20.00, 27.00 |
| Pagination `limit` | 1–50 | 0, 51, negative, string | 1, 50 |
| Auth | valid JWT | missing, expired, wrong audience, other user's id | expiry ± 1 s |
| Role | farmer on farmer routes | farmer on `/v1/admin/*` | — |

Schemathesis runs `--checks all` against `/openapi.json` (status codes, schema conformance, 5xx = fail).

## 4. Timeout tests
| Scenario | Expected |
|---|---|
| Inference > 4 s (mocked slow session) | 503 problem+json, `Retry-After`, scan stays `uploaded` |
| LLM > 20 s (respx delay) | diagnosis returned with cached/static advice, `advisories.status='fallback'` |
| LLM 429 / 500 | same fallback, no 5xx to client |
| Supabase slow (toxiproxy 3 s latency) | `/readyz` reports degraded; `/healthz` still fast |
| Cold start | client waits ≤ 90 s with "waking" UI, then outbox flushes (E2E with API started late) |
| Signed URL expired (> 5 min) | 403 from Storage → client requests new URL automatically |

## 5. Concurrency tests
| Scenario | Expected |
|---|---|
| Same image submitted twice simultaneously (same `sha256`) | exactly one scan row; second gets the same id |
| Same `Idempotency-Key` replayed 10× in parallel | one side effect |
| 50 concurrent `analyze` calls | semaphore caps parallel inferences at 2; others queue; no OOM; 429 beyond queue limit |
| 20 parallel `audit_append` | chain linear (advisory lock); verification passes |
| Two agronomists review the same scan | both reviews stored; label conflict → `unclear` |
| Alert approve race | one approval wins; n8n receives exactly one event |

k6 load profile (`tests/concurrency/k6/scan_flow.js`): ramp 0→20 VUs over 2 min, hold 5 min;
thresholds `http_req_failed < 1%`, `p(95) < 5000` ms for cached advice path.

## 6. Security tests
RLS (anon key cannot read other users' rows), IDOR on every `{id}` route, JWT tampering, upload
polyglots, XSS payloads in farmer questions and in a poisoned test KB chunk, prompt-injection
red-team set, HMAC replay, rate-limit enforcement, ZAP baseline on staging, dependency audit,
secret scan.

## 7. ML tests
Accuracy gates from `docs/ai/eval-plan.md`; robustness (blur, brightness, rotation, JPEG,
crop) agreement ≥ 90 %; slice floors; int8 parity; ONNX hash; deterministic preprocessing
(same bytes → same tensor).

## 8. Manual testing
Sheets in `tests/manual/`: functional walkthrough per route, device/browser matrix (low-end
Android Chrome, Samsung Internet, iOS Safari, desktop), network throttling (Slow 3G, offline),
Bangla copy review, usability sessions protocol.

## 9. n8n-driven testing
`automation/n8n/workflows/05-synthetic-monitor.md`: every 10 min in demo windows → `/healthz`,
`/readyz`, demo session, analyze fixture image, assert citation present, record latency → alert
team Telegram on failure. Workflow tests: each workflow has a "test" trigger with fixture payloads.

## 10. Entry / exit criteria for the 31 Oct submission
Exit: all hard gates green (citation coverage, banned leakage, red-team, RLS, IDOR, upload);
E2E happy paths pass in bn and en; no P1 bugs open; known issues listed in the README.

## 11. Test data
Synthetic only (`tests/fixtures/`): generated profiles, a handful of CC BY images from D1/D2 with
attribution file, non-leaf images for OOD, malicious upload samples (generated, harmless).
