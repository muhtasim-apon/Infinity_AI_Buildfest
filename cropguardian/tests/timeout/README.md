# Timeout tests

Owner: Apon. Tools: pytest + respx (slow HTTP), a fake ONNX session that sleeps, Toxiproxy (slow DB),
k6. Semi-manual cold-start test: [`cold_start_e2e.md`](cold_start_e2e.md).

| ID | Scenario | Expected |
|---|---|---|
| TO1 | inference sleeps 5 s (budget 4 s) | 503 problem+json with `Retry-After`; scan stays `uploaded` |
| TO2 | LLM delayed 25 s (budget 20 s) | 200 with diagnosis; advisory `fallback`; no 5xx |
| TO3 | LLM returns 429 / 500 / 503 | same fallback; error logged without PII |
| TO4 | Postgres +3 s latency | `/healthz` < 200 ms; `/readyz` degraded |
| TO5 | signed upload URL used after 5 min | Storage 403 → client requests a new URL (E2E) |
| TO6 | Open-Meteo times out (3 s) | analysis succeeds; outbreak risk not raised |
| TO7 | Turnstile verification endpoint slow | demo session fails closed with a clear message, no hang |
| TO8 | Render cold start (~1 min after 15 min idle) | UI waking state; outbox flushes after `/healthz` 200 |
