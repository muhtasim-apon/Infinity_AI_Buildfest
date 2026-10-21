---
name: cropguardian-safety
description: Crop Guardian honesty rules, the PII boundary, security checklist coverage and forbidden patterns. Load for EVERY phase and every task in this repository before writing code, docs, UI copy or demo content.
---

# Crop Guardian safety skill

Source of truth: `CROP_GUARDIAN_BUILD_SPEC.md` 0.2, 16.22, 19.8. If this file and the spec disagree, the spec wins; record the fix in DECISIONS.md.

## 1. Honesty rules (Congress integrity rules; non-negotiable)
- A metric may only be shown, written or spoken if a committed script produced it on a recorded split (`ml/reports/...` with commit hash and split id). Otherwise render **"Not yet measured"**, never a number.
- Everything simulated or synthetic (outbreaks, demo farmers/reviews/alerts) carries a visible **SIMULATED / DEMO DATA** label in UI, exports and API (`"synthetic": true`).
- Advice reads "Based on published BRRI/DAE guidance - not yet reviewed by an agronomist" until a KB document has `expert_reviewed=true` set by a real reviewer.
- Never claim field loss reduction (it is a pre-registered pilot outcome). Never invent URLs, dataset counts, checksums, licences or citations: fetch or compute them, or mark `UNVERIFIED` / `GAP`.
- Every third-party statistic goes in `docs/research/sources.md` with URL + access date and is referenced `[S#]`, `[D#]` or `[R#]`.

## 2. The PII boundary
- The LLM receives only: disease, crop, growth stage, coarse weather summary, public KB text, and the farmer's question **after PII scrubbing**. Images never go to any third-party API.
- Never log: passwords, tokens, OTPs, session ids, TOTP secrets, API keys, full phone numbers, exact coordinates, image bytes. Coordinates are rounded on the device and stored coarse.

## 3. Fail closed, deny by default
Validation, authn/authz, integrity, model-integrity, citation or config failure -> reject, log, show a safe fallback. Never "continue anyway". Every endpoint is authenticated unless the spec lists it as public; every object access goes through `core/authz.py`. Never weaken a security default to make a test or demo pass - use fixtures or `CG_ENV=test`.

## 4. Security checklist coverage (spec 16.22 -> where it lives)
HTTPS/HSTS/CSP/headers (16.3) - authn, sessions, CSRF (16.4, 16.6) - authz/IDOR (16.5) - input validation, parameterised queries (16.7) - rate limits (16.8) - RLS + tenancy (16.10) - uploads (16.11) - CAPTCHA (16.12) - hidden admin (16.13) - debug off (16.14) - never trust the frontend (16.15) - LLM Top 10 (16.16) - privacy/deletion (16.17) - secrets/supply chain (16.18) - webhooks (16.19). A phase is not done without its 16.21 row.

## 5. Forbidden patterns (enforced by `backend/scripts/check_forbidden.py`)
Python: `eval(`, `exec(`, pickle/marshal/shelve, `torch.load` without `weights_only=True`, `yaml.load(`, `shell=True`, `os.system/popen`, `tempfile.mktemp`, `verify=False`, `allow_origins=["*"]`, `print(`/`assert` in `app/`, `==`/`!=` on secrets (use `hmac.compare_digest`), logging secret-named variables, `httpx` outside `core/http.py`, `anthropic` outside `advisory/llm_adapter.py`, TODO/FIXME in `core/`.
TypeScript: `dangerouslySetInnerHTML`, `innerHTML`, `document.write`, `eval`, `new Function`, string `setTimeout`, `localStorage/sessionStorage` (UI prefs allow-list only), external `http(s)://` literals, `target="_blank"` without `rel="noopener noreferrer"`, numeric animation durations outside `design/motion.ts`, hex colours outside `design/tokens.*`.
Repo: private keys, `.env` files, tokens, datasets/weights. Exceptions need `# forbidden-ok: <reason>` on the same line.

## 6. Working habits
Pure logic in `backend/app/domain/` and `ml/cg_ml` (no DB, network, clock). Times UTC, shown Asia/Dhaka. Tests always include invalid input, boundaries, permission failures. Comment the *why* of every security/ML/caching decision. Bangla is the source locale (`bn.json` first). Run `/security-review` on every phase diff before the gate.
