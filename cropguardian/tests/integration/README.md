# Integration tests

Owner: Apon, Taeen. Environment: API + disposable Postgres with pgvector (testcontainers or a second
free Supabase project) + Storage emulator, fake LLM, tiny test ONNX model. Nightly.

| ID | Case | Expected |
|---|---|---|
| IT1 | create → upload → analyze (fixture leaf) | rows in scans, diagnoses, advisories, citations, audit_log; status diagnosed |
| IT2 | non-leaf fixture | status `not_sure`; no advisory; not-sure help returned |
| IT3 | **stateless restart**: recreate the app between upload and analyze | analyze still succeeds (Render may restart any time) |
| IT4 | 3 blast diagnoses within 5 km / 7 days | one published alert |
| IT5 | admin dismisses alert | status dismissed; audit row with reason |
| IT6 | admin changes τ | `app_settings` updated; audit row; next analysis uses new τ |
| IT7 | migration applied twice on a fresh DB | idempotent / fails cleanly — never half-applied |
| IT8 | model file missing at boot | downloaded from private bucket; sha256 verified; `/readyz` 200 |
| IT9 | model hash mismatch | `/readyz` 503; analyze 503 |
