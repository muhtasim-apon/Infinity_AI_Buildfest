# services/api — Crop Guardian API (FastAPI)

**Template folder — no code yet.** Everything to build is specified in **[`SPEC.md`](SPEC.md)**:
file tree, 17 endpoints, schemas, security modules, ML inference and abstain rules, RAG validator,
outbreak rules, audit chain, container and dependencies.

Owners: **Apon** (lead), **Taeen**; `app/rag/` **Salwa**; `app/services/advisory.py` **Raisa**.

## Build order (Gantt)
| Day | What |
|---|---|
| 18 Oct | `config.py`, `main.py`, `routers/health.py`, `security/auth.py` (JWKS), role guard |
| 19 Oct | `routers/scans.py` create + signed upload URL, `security/upload.py`, idempotency |
| 20 Oct | `ml/preprocess.py`, `ml/inference.py`, `ml/decision.py`, `Dockerfile` → first Render deploy |
| 22 Oct | `rag/*`, `services/advisory.py` integration; `services/audit_chain.py` |
| 23 Oct | `services/outbreak.py`, `routers/alerts.py`, n8n webhook |
| 24 Oct | `routers/admin.py`, `security/ratelimit.py`, `security/captcha.py`, `routers/demo.py` |
| 25 Oct | `security/headers.py`, `security/webhook_sig.py`, `routers/hooks.py`, `routers/audit.py` |

## Run locally (once the code exists)
See [`docs/deployment/00-zero-to-deploy.md`](../../docs/deployment/00-zero-to-deploy.md) Phase 4.
