# Runbook (spec 22.3) — skeleton

Entries below are **procedures not yet rehearsed**. Each is rehearsed and dated in Phase 11/12; until then do not
tell judges they have been tested.

| Situation | First actions | Status |
|---|---|---|
| API asleep / cold start | open `/health`, wait up to 90 s (the UI shows "waking"); keep-warm workflow runs every 10 min in demo windows | not rehearsed |
| Supabase paused | dashboard → Restore project; then `/health/ready` | not rehearsed |
| Redis lost | auth rate limits fail **closed**; queue/pub-sub degrade; restart Key Value | not rehearsed |
| LLM outage | set `ADVICE_MODE=static` (cached/fallback cards only) | not rehearsed (Phase 6) |
| Budget exhausted | `LLM_DAILY_BUDGET_USD` cap reached → static advice | not rehearsed (Phase 6) |
| Model integrity alert | roll back to the previous active model version (admin, step-up) | not rehearsed (Phase 9) |
| Bad advice reported | disable advice for that disease (admin toggle), fix KB/prompt, re-eval, re-enable | not rehearsed (Phase 6) |
| Audit chain broken | freeze admin actions; `SELECT audit_verify_chain()` returns the first bad row id; investigate | verified in test DB (see tests/integration) |
| Key leak | rotate in this order: Anthropic, DB, S3, `SECRET_KEY` (forces re-login) | not rehearsed |
| Restore drill | `make restore-drill` | stub (Phase 12) |
