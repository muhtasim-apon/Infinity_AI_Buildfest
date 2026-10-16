# API specification — `services/api/` (FastAPI)

**Status: specification only — no code in this folder yet.** The team creates the files below one by one,
in the order of the [Gantt](../../docs/plan/gantt.md). Owners: **Apon** (lead), **Taeen** (support);
`app/rag/` **Salwa**; `app/services/advisory.py` **Raisa**.

Design context: [SDD §9](../../docs/system-design/SDD.md) · [ADR 0002](../../docs/architecture/adr/0002-fastapi-modular-monolith.md) ·
[security checklist](../../docs/security/security-checklist.md) · tests: [`tests/`](../../tests/README.md).

---

## 1. File tree to create

```
services/api/
├── Dockerfile                 container (see §9)
├── .dockerignore              keeps .env, caches, tests out of the image
├── requirements.txt           runtime deps (§10), pinned after first install
├── requirements-dev.txt       test/lint deps (§10)
└── app/
    ├── main.py                app factory, middleware, routers, lifespan
    ├── config.py              typed settings (all vars in ../../.env.example)
    ├── db.py                  async Postgres pool
    ├── routers/               thin HTTP layer
    │   ├── health.py  demo.py  scans.py  alerts.py  admin.py  audit.py  hooks.py
    ├── schemas/               Pydantic v2 models
    │   ├── scan.py  alert.py  admin.py
    ├── security/
    │   ├── auth.py  upload.py  webhook_sig.py  ratelimit.py  captcha.py  headers.py
    ├── ml/
    │   ├── preprocess.py  inference.py  decision.py
    ├── rag/
    │   ├── retriever.py  prompt.py  validator.py  banned.txt
    └── services/
        ├── scan_service.py  advisory.py  outbreak.py  audit_chain.py
```

Roles in the system: **`farmer`**, **`admin`**, **`demo`** (read-mostly synthetic sandbox).

## 2. `main.py` — application factory
| Concern | Rule |
|---|---|
| Lifespan (startup) | load settings → open DB pool → load model (download from private bucket if missing, verify SHA-256) → app becomes ready. Hash mismatch or download failure → app stays *not ready* (`/readyz` 503). |
| Interactive docs | `/docs` and `/openapi.json` **disabled when `ENVIRONMENT=production`** (debug off in prod). |
| CORS | allow exactly `APP_BASE_URL` (+ `http://localhost:5173` in development). Never `*`. Methods GET/POST/PUT; headers `Authorization`, `Content-Type`, `Idempotency-Key`, `CF-Turnstile-Response`. |
| Middleware | request-id, security headers (`security/headers.py`), rate limiter, problem+json error handler, structured JSON logging without PII. |
| Workers | one Uvicorn worker; CPU inference via thread pool + semaphore(2). |

## 3. `config.py` — settings
Every variable is listed with its meaning in [`../../.env.example`](../../.env.example). Secrets are
`SecretStr`. Settings are loaded once (cached). Pydantic setting `protected_namespaces=()` so fields
named `model_*` do not warn.

## 4. Endpoints (complete list)
Conventions: JSON, snake_case, `Authorization: Bearer <Supabase access token>`, writes accept
`Idempotency-Key`, errors are RFC 9457 `application/problem+json` `{type,title,status,detail,code}`.

| # | Method & path | Who | Budget | Behaviour |
|---|---|---|---|---|
| 1 | `GET /healthz` | public | 200 ms | `{"status":"ok"}` — no DB, no model. Render health check. |
| 2 | `GET /readyz` | public | 2 s | `{db, model:{name,version,sha256}}`; 503 if any part down. |
| 3 | `POST /v1/demo/session` | public + **CAPTCHA** | 2 s | body `{role:"user"|"admin"}`, header `CF-Turnstile-Response`; verifies Turnstile server-side; issues 30-min token for a synthetic demo account; 10/min/IP. |
| 4 | `POST /v1/scans` | farmer, demo | 2 s | create scan (`pending_upload`), return 5-min signed upload URL; idempotent on `(user_id, sha256)` → 200 with existing scan. |
| 5 | `POST /v1/scans/{id}/analyze` | owner | 25 s | validate image → infer → decide → advise (if not abstained) → persist → outbreak check. |
| 6 | `GET /v1/scans` | owner | 2 s | history, `limit` 1–50, cursor. |
| 7 | `GET /v1/scans/{id}` | owner, admin | 2 s | scan + diagnosis + advisory. Other users' ids → **404** (no id probing). |
| 8 | `GET /v1/alerts?lat=&lon=` | farmer, demo, admin | 2 s | published alerts covering a coarse point. |
| 9 | `PUT /v1/me/alert-preference` | farmer | 2 s | in-app alerts on/off, radius 1–50 km. |
| 10 | `POST /v1/alerts/{id}/dismiss` | admin | 2 s | operator kill-switch (wrong/abusive alert); reason required; audited. |
| 11 | `GET/PUT /v1/admin/settings` | admin | 3 s | τ, outbreak radius/min reports/window/cooldown; `reason` required on PUT; audited. |
| 12 | `GET /v1/admin/models`, `POST /v1/admin/models/{id}/activate` | admin | 3 s | registry; activation needs an evaluation report; audited. |
| 13 | `GET/POST /v1/admin/kb/documents`, `POST …/{id}/retire` | admin | 3 s | knowledge-base documents with licence note; audited. |
| 14 | `GET /v1/admin/users`, `PUT /v1/admin/users/{id}/role` | admin | 3 s | roles `farmer`/`admin` only; audited. |
| 15 | `GET /v1/admin/digest`, `GET /v1/admin/drift` | admin **or** signed webhook | 3 s | counts for n8n workflows 02 and 06. |
| 16 | `GET /v1/audit/report?format=json|html` | admin, demo (synthetic only) | 10 s | sections in `docs/security/audit-readiness.md`; unmeasured → "not yet measured". |
| 17 | `POST /v1/hooks/n8n/{event}` | **signed webhook** | 3 s | events `heartbeat`, `retention`, `reset_demo`, `verify_audit_chain`; long jobs return 202. |

Every route except 1–3 requires auth; every route checks role **on the server** (the UI hiding a
button is never the control).

## 5. Schemas (validation rules)
| Model | Fields and rules |
|---|---|
| `ScanCreateIn` | `crop` = `rice`; `field_id` uuid optional; `sha256` 64 hex; `lat_coarse` 20.00–27.00 and `lon_coarse` 88.00–93.00, **multiple of 0.01** (exact GPS rejected); `captured_at` optional; `client_quality_flag` `dark`/`blurry`/null |
| `ScanCreateOut` | `scan_id`, `upload_url`, `upload_expires_at` |
| `Prediction` | `code`, `name_bn`, `name_en`, `prob` 0–1 |
| `DiagnosisOut` | `model_version`, `top3[3]`, `abstained`, `confidence_band` high/medium/low |
| `AdvisoryOut` | `status` ok/fallback/blocked, `summary_bn`, `steps_bn[]`, `chemical` {active_ingredient, dose (verbatim from source), interval, phi_days} or null, `safety_bn`, `citations[]` {title, publisher, page, url} |
| `AnalyzeOut` | `scan_id`, `status` diagnosed/not_sure, `diagnosis`, `advisory` (null when not sure), `not_sure_help` (retake tips + local agriculture office card) |
| `AlertOut` | id, disease code/name_bn, centre (coarse), radius_km, report_count, risk, `rule_version`, `status` published/dismissed, `label` "possible outbreak — unverified, rule-based", created_at |
| `SettingsIn` | τ 0–1 exclusive; radius 0–50; min reports 2–50; window 1–30 days; cooldown hours 6–168; `reason` 5–500 chars |

## 6. `security/`
| File | Contract | Checklist item(s) |
|---|---|---|
| `auth.py` | verify Supabase access token via **JWKS** (`SUPABASE_JWKS_URL`, ES256/RS256, cache ≤ 10 min, refetch on unknown `kid`); check `exp`, `aud=authenticated`; reject `alg:none`/HS256; load role from `profiles` (DB is the source of truth); `require_role(*roles)` dependency, deny by default | Auth on every route · Never trust the frontend · Hide admin pages properly |
| `upload.py` | size ≤ `MAX_UPLOAD_MB` → else 413; magic bytes JPEG/PNG/WebP → else 415; decode with pixel cap 25 MP → else 422; min side 64 px; convert RGB; **re-encode JPEG** (drops EXIF/GPS, defeats polyglots) | Check file upload types · Sanitize input |
| `webhook_sig.py` | HMAC-SHA256 over `"{timestamp}.{raw_body}"`; header `X-CG-Signature: sha256=<hex>`, `X-CG-Timestamp`; reject if \|now−ts\| > 300 s, signature mismatch (constant-time compare), or replay within 5 min | Verify webhook signatures |
| `ratelimit.py` | token bucket per user and per IP; scans 30/h, advisory 60/h, demo 10/min/IP, auth-adjacent endpoints strict; daily LLM token budget; 429 + `Retry-After` | Rate limiting |
| `captcha.py` | verify Cloudflare Turnstile token server-side (secret in env) for the public demo-session endpoint | CAPTCHA on public forms |
| `headers.py` | API responses: `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Cache-Control: no-store` on authenticated responses | Security headers · HTTPS everywhere |

## 7. `ml/` — vision inference
| File | Contract |
|---|---|
| `preprocess.py` | bytes → float32 tensor (1,3,224,224): resize short side 256 → centre crop 224 → /255 → ImageNet mean/std. **Must equal training eval transform** (parity test). Deterministic. |
| `inference.py` | `load_session(path, expected_sha256)` downloads from the private `models` bucket when the file is missing (always after a Render restart), verifies hash, opens ONNX Runtime CPU session (`intra_op_num_threads=1`). `predict_logits(...)` runs in thread pool behind semaphore(2) with `INFERENCE_TIMEOUT_MS` → timeout → 503. |
| `decision.py` | `probs = softmax(logits / T)`; non-finite logits → not sure (`invalid_logits`); energy OOD score > threshold → not sure (`out_of_distribution`); max prob < τ → not sure (`low_confidence`); **max prob = τ → diagnosed** (inclusive). Band: high ≥ max(τ, 0.90), medium ≥ τ. 100 % branch coverage required. |

## 8. `rag/` and `services/`
| File | Contract |
|---|---|
| `rag/retriever.py` | hybrid: pgvector cosine top-20 ∪ full-text top-20 → reciprocal rank fusion (k = 60) → filter by crop + disease, exclude retired docs → top `RAG_TOP_K`; best score < `RAG_MIN_SCORE` → caller falls back. Query embedding: multilingual-e5-small ONNX, prefix `query: `. |
| `rag/prompt.py` | builds messages from **typed, non-personal fields only** (disease, crop, stage, confidence band, weather summary); sources wrapped as `<source id=…>` and farmer text as `<farmer_question>` — content inside tags is data, never instructions. |
| `rag/validator.py` | V1 valid JSON schema · V2 ≥ 1 citation · V3 cited ids ⊂ retrieved ids · V4 chemical dose appears verbatim (NFC + whitespace normalised) in a cited chunk · V5 no banned active ingredient (bn + en, case-insensitive) · V6 safety line present when chemical ≠ null. Any failure → `blocked`. Until `banned.txt` is sourced, **all chemical advice is blocked**. |
| `services/scan_service.py` | owner check → status must be `uploaded` (else 409) → download → sanitise → preprocess → infer → decide → advise if diagnosed → **one transaction**: diagnosis + advisory + citations + scan status + audit row → outbreak check after commit (its failure never fails the request). Idempotent. |
| `services/advisory.py` | cache by (disease, crop, stage, KB version) → retrieve → prompt → LLM (`LLM_TIMEOUT_MS`, max 1,500 tokens, temperature 0.2) → validate → retry once on V1 only. LLM timeout/429/5xx → `fallback` (cached or static card). Agent tools: `get_diagnosis`, `search_kb`, `get_weather`, `get_field_history` — **all read-only**, max 4 calls. |
| `services/outbreak.py` | rules v1: count non-abstained diagnoses of a notifiable disease within radius (haversine on coarse points) and window; ≥ min reports → **publish** one alert per (disease, area) unless one is inside the cooldown; risk: high if count ≥ 2×min and weather favourable, medium if favourable, else low; unknown weather never raises risk. Label "possible outbreak — unverified, rule-based". In-app only. |
| `services/audit_chain.py` | `append(actor, action, entity, id, detail)` through the DB function (advisory lock keeps the chain linear); `scrub(detail)` removes phone, email, name, lat/lon; `verify_chain()` recomputes hashes and returns first broken id. **Every admin action is logged.** |

## 9. Container specification (for the `Dockerfile` to write)
- Base `python:3.12-slim`; install `requirements.txt` with no cache; copy `app/`.
- Run as a non-root user; create `/tmp/models` owned by that user.
- **No build ARGs and no secrets in the Dockerfile** — Render passes every env var to `docker build`
  as a build arg, so anything read at build time can land in an image layer.
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers`.
- `.dockerignore`: `.env*`, `__pycache__`, `.venv`, caches, `*.onnx`, `tests/`.

## 10. Dependencies (to pin on first install)
Runtime: fastapi · uvicorn[standard] · pydantic ≥ 2 · pydantic-settings · httpx · asyncpg · pgvector ·
supabase · pyjwt[crypto] · onnxruntime · numpy · pillow · anthropic · tokenizers · slowapi · sentry-sdk.
Dev: pytest · pytest-asyncio · pytest-cov · hypothesis · respx · schemathesis · ruff · mypy · bandit ·
pip-audit · locust. **No PyTorch at runtime** (ADR 0004).

## 11. Definition of done per file
Contract above implemented · tests in the matching `tests/<type>/README.md` written and green ·
no secret or PII in logs · checklist row in `docs/security/security-checklist.md` ticked.
