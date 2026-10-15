# services/api — Crop Guardian API (FastAPI)

Owners: **Apon** (lead), **Taeen**. AI modules: Salwa (`app/rag/`), Raisa (`app/services/advisory.py`).
Status: **typed stubs — not runnable yet.** Functions raise `NotImplementedError` with their
contract in the docstring.

```
app/
├── main.py              app factory, middleware, router registration, startup (model load)
├── config.py            typed settings from environment (.env.example)
├── db.py                async connection pool (asyncpg / SQLAlchemy async)
├── routers/             thin HTTP layer — validation, auth, status codes
│   ├── health.py        /healthz /readyz
│   ├── demo.py          /v1/demo/session
│   ├── scans.py         /v1/scans …
│   ├── review.py        /v1/review …
│   ├── alerts.py        /v1/alerts …
│   ├── admin.py         /v1/admin …
│   ├── audit.py         /v1/audit/report
│   └── hooks.py         /v1/hooks/n8n/{event}
├── schemas/             Pydantic v2 request/response models
├── services/            business logic: scan_service, advisory, outbreak, audit_chain
├── ml/                  inference (ONNX), decision (abstain), preprocessing
├── rag/                 retriever, validator, prompt builder
└── security/            auth (JWT), roles, upload sanitiser, HMAC, rate limit
```

API contract: [`openapi-outline.md`](openapi-outline.md). Design: [`../../docs/system-design/SDD.md`](../../docs/system-design/SDD.md) §9.

## Run (once implemented)
```bash
cp ../../.env.example .env
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```
