# OWASP mapping

## OWASP Top 10 (web) — https://owasp.org/Top10
| Category | Control in Crop Guardian | Verified by |
|---|---|---|
| A01 Broken Access Control | role guard on every router; ownership checks; RLS on every table; deny by default | S6–S9 |
| A02 Cryptographic Failures | HTTPS only + HSTS; Supabase encryption at rest; no secrets in repo; hashed audit chain | config review, gitleaks |
| A03 Injection | parameterised queries; Pydantic validation; output escaping; CSP | Bandit, Schemathesis, ZAP |
| A04 Insecure Design | threat model; abstain + HITL; gated agent tools | `threat-model.md` |
| A05 Security Misconfiguration | strict CORS allow-list; security headers on static site; debug off; `/docs` disabled in prod | ZAP baseline |
| A06 Vulnerable Components | Dependabot; `pip-audit`; `npm audit`; pinned versions | CI |
| A07 Identification & Auth Failures | Supabase Auth OTP; JWT TTL 1 h; refresh rotation; OTP rate limit | S1–S4 |
| A08 Software & Data Integrity | ONNX hash check; signed webhooks; lockfiles; protected `main` | S17 |
| A09 Logging & Monitoring Failures | structured logs with request id; audit log; Sentry; n8n uptime monitor | runbook |
| A10 SSRF | API never fetches user-supplied URLs; outbound allow-list (Supabase, LLM, Open-Meteo) | code review |

## OWASP Top 10 for LLM Applications — https://genai.owasp.org
| Risk | Control | Verified by |
|---|---|---|
| LLM01 Prompt Injection | user text and KB chunks wrapped as data; system rules restated after context; validator | red-team suite |
| LLM02 Sensitive Information Disclosure | no PII in prompts (typed builder); outputs never echo other users' data | S18 |
| LLM03 Supply Chain | pinned SDK; provider allow-list; model id in config | CI |
| LLM04 Data & Model Poisoning | KB admin-only with source allow-list; training uses public licensed datasets only (no user uploads) | governance |
| LLM05 Improper Output Handling | strict JSON schema; escape on render; never executed | WB-V1–V11 |
| LLM06 Excessive Agency | read-only tools only; no alert or messaging tool; 4-call cap | security case S19 |
| LLM07 System Prompt Leakage | no secrets in prompts; leakage harmless by design | red-team |
| LLM08 Vector & Embedding Weaknesses | metadata filters; retired docs excluded; no user-writable vectors | S20 |
| LLM09 Misinformation | citations mandatory; dose verbatim; banned list; abstain | RAG eval |
| LLM10 Unbounded Consumption | rate limits; token caps; daily budget; cache | S15, CC3 |
