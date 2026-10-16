# Concurrency & load tests

Owner: Apon. Tools: pytest-asyncio (`asyncio.gather` against the app), k6, Locust. **Staging only** —
never load-test the production demo, and keep runs short: Render may suspend a free service for
unusually high outbound traffic (see [`04-free-tier-challenges.md`](../../docs/deployment/04-free-tier-challenges.md)).

| ID | Scenario | Expected |
|---|---|---|
| CC1 | 20 parallel `POST /v1/scans` with the same sha256 | one row; all responses carry the same scan_id |
| CC2 | 10 parallel analyze calls with the same `Idempotency-Key` | one diagnosis row, one audit row |
| CC3 | 50 parallel analyze calls | max 2 concurrent inferences; overflow → 429; no out-of-memory |
| CC4 | 20 parallel `audit_append` | chain verifies; ids contiguous; each prev_hash = previous row_hash |
| CC5 | outbreak check fired by 5 simultaneous diagnoses in one area | exactly one published alert |
| CC6 | two admins change the same setting simultaneously | last write wins; both changes in audit log |

## k6 load profile (`tests/concurrency/k6/scan_flow.js` to create)
Setup: `GET /healthz` with 120 s timeout (measure steady state, not the cold start).
Stages: ramp 0 → 20 virtual users in 2 min, hold 5 min, ramp down 1 min.
Thresholds: `http_req_failed < 1 %`; p95 < 5 s on the cached-advice analyze path.
Flow per user: demo session → create scan → upload fixture → analyze → history.
Run: `k6 run -e BASE=<staging API URL> tests/concurrency/k6/scan_flow.js`.
