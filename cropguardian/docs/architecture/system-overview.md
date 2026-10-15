# System overview

Diagram: [`../diagrams/system-architecture.mmd`](../diagrams/system-architecture.mmd).

```
┌──────────────────────────── Browser (phone-first PWA) ─────────────────────────────┐
│ React + Vite + TS · i18n bn/en · service worker · IndexedDB outbox · image compress │
│ routes: /app /app/scan /app/result/:id /app/history /app/alerts /app/review          │
│         /demo-user /demo-admin /admin /data /security /architecture                  │
│         /presentation /pitchdeck /audit                                              │
└──────────────┬───────────────────────────────────────────────┬──────────────────────┘
               │ REST/JSON + Bearer JWT                        │ supabase-js: auth,
               ▼                                               │ signed-URL PUT
┌──────────── Crop Guardian API (FastAPI, Docker, Render free, 1 instance) ──────────┐
│ routers:  auth · scans · diagnoses · advisory · review · alerts · admin · audit ·   │
│           hooks · health                                                            │
│ services: scan_service · inference (ONNX Runtime) · explain · advisory (agent) ·    │
│           rag (retriever, validator) · outbreak (cluster + weather) · audit_chain    │
│ security: jwt verify · role guard · rate limit · upload sanitiser · HMAC verify      │
└──────┬──────────────────────────┬───────────────────────┬────────────────┬──────────┘
       ▼                          ▼                       ▼                ▼
 Supabase Postgres          Supabase Storage         LLM provider       Open-Meteo
 relational + pgvector      scans/ (private)         (Claude, swap-     weather API
 + RLS + audit_log          models/ (ONNX)            pable via config)
       ▲
       │ HMAC webhooks / REST
┌──────┴──────── n8n ────────┐
│ alert fan-out · daily digest│──▶ SMS gateway / email / Telegram
│ drift monitor · keep-warm  │
│ synthetic uptime checks    │
└────────────────────────────┘
```

## Module responsibilities
| Module | Owns tables | Talks to | Owner |
|---|---|---|---|
| auth | profiles, consents | Supabase Auth | Apon |
| scans | scans | Storage | Apon |
| inference | diagnoses, model_versions | ONNX file | Apon (integration) / Taeen (model) |
| advisory | advisories, citations | rag, LLM | Raisa |
| rag | kb_documents, kb_chunks | pgvector | Salwa |
| review | expert_reviews, feedback_labels | scans, diagnoses | Apon |
| alerts / outbreak | alerts, alert_subscriptions | Open-Meteo, n8n | Apon / Taeen |
| admin | settings | all (read) | Apon |
| audit | audit_log | all (append) | Apon |

**Rule:** a module writes only its own tables. Cross-module reads go through the owning
module's service function, never ad-hoc SQL.

## Trust boundaries
1. Browser ↔ API: untrusted input. JWT verified on every request; role from token claims
   cross-checked with `profiles.role`.
2. Browser ↔ Supabase: anon key only; RLS enforces ownership.
3. API ↔ Supabase: service-role key — server only.
4. API ↔ LLM: outbound; only disease name, crop, stage, and retrieved public KB text — **no
   phone numbers, names or precise location** ever leave.
5. n8n ↔ API: HMAC-signed webhooks, replay window 5 min.
