# System overview

Diagram: [`../diagrams/system-architecture.mmd`](../diagrams/system-architecture.mmd).
Build specs: [`services/api/SPEC.md`](../../services/api/SPEC.md) · [`apps/web/SPEC.md`](../../apps/web/SPEC.md) ·
[`db/SCHEMA-SPEC.md`](../../db/SCHEMA-SPEC.md).

```
┌──────────────────────────── Browser (phone-first PWA) ─────────────────────────────┐
│ React + Vite + TS · i18n bn/en · service worker · IndexedDB outbox · image compress │
│ routes: /app /app/scan /app/result/:id /app/history /app/alerts                      │
│         /demo-user /demo-admin /admin /data /security /architecture                  │
│         /presentation /pitchdeck /audit                                              │
└──────────────┬───────────────────────────────────────────────┬──────────────────────┘
               │ REST/JSON + Bearer JWT                        │ supabase-js: auth
               ▼                                               │ (+ CAPTCHA), signed PUT
┌──────────── Crop Guardian API (FastAPI, Docker, Render free, 1 instance) ──────────┐
│ routers:  health · demo · scans · alerts · admin · audit · hooks                    │
│ services: scan_service · inference (ONNX Runtime) · decision (abstain) ·            │
│           advisory (agent) · rag (retriever, validator) · outbreak · audit_chain     │
│ security: JWKS auth · role guard · rate limit · CAPTCHA · upload sanitiser ·         │
│           webhook signatures · security headers                                     │
└──────┬──────────────────────────┬───────────────────────┬────────────────┬──────────┘
       ▼                          ▼                       ▼                ▼
 Supabase Postgres          Supabase Storage         LLM provider       Open-Meteo
 relational + pgvector      scans/ (private)         (Claude, swap-     weather API
 + RLS + audit_log          models/ (private)         pable via config)
       ▲
       │ signed webhooks
┌──────┴──────── n8n ─────────┐
│ alert notice · daily digest │──▶ team Telegram channel
│ drift · keep-warm · heartbeat│
│ synthetic monitor · retention│
└──────────────────────────────┘
```

## Module responsibilities
| Module | Owns tables | Talks to | Owner |
|---|---|---|---|
| auth | profiles, consents | Supabase Auth | Apon |
| scans | scans | Storage | Apon |
| inference | diagnoses, model_versions | ONNX file | Apon (integration) / Taeen (model) |
| advisory | advisories, citations | rag, LLM | Raisa |
| rag | kb_documents, kb_chunks | pgvector | Salwa |
| alerts / outbreak | alerts, alert_preferences | Open-Meteo, n8n | Apon / Taeen |
| admin | app_settings | all (read) | Apon |
| audit | audit_log | all (append) | Apon |

**Rule:** a module writes only its own tables; cross-module reads go through the owning module.

## Trust boundaries
1. Browser ↔ API: untrusted input. Token verified against Supabase JWKS on every request; role
   always read from `profiles` on the server.
2. Browser ↔ Supabase: publishable key only; RLS enforces ownership; CAPTCHA on auth forms.
3. API ↔ Supabase: secret key — server only.
4. API ↔ LLM: only disease, crop, stage and retrieved public KB text — **no names, emails or precise
   location**.
5. n8n ↔ API: HMAC-signed webhooks, 5-minute replay window.
