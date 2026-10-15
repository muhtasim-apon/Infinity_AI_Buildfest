# 05 — Synthetic monitor (end-to-end smoke test)

**Trigger:** Cron every 10 min inside demo windows, hourly otherwise.

| Step | Assertion |
|---|---|
| `GET /healthz` | 200 within 90 s |
| `GET /readyz` | `db=ok`, `model.sha256` = expected |
| `POST /v1/demo/session {role:user}` | token returned |
| create scan with fixture `blast_fixture.jpg` (CC BY, attributed) → upload → analyze | status 200; `diagnosis.top3` length 3; if diagnosed then `advisory.citations` length ≥ 1 |
| `GET /audit` page (static site) | 200 |
| record | latency per step → Google Sheet / n8n data table |

Failure → team Telegram with failing step + response excerpt (no tokens). This is the deployed-environment half of the test strategy (`docs/testing/test-strategy.md` §9).
