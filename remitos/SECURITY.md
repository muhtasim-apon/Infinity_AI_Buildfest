# Security Policy

## Scope
RemitOS handles personally identifiable information, national identity documents and
financial instructions. Every component is in-scope for security review.

## Reporting a vulnerability
Report privately to the security owner listed in `CODEOWNERS`. Do not open a public
issue. Expect acknowledgement within 48 hours and a remediation plan within 7 days.

Do not test against any environment you do not own. Congress section 20.11 prohibits
introducing malware, exploiting vulnerabilities, or interfering with event
infrastructure.

## Security posture summary

| Control | Where it is specified |
|---|---|
| Threat model (STRIDE) | `docs/security/threat-model.md` |
| Data residency and sovereignty | `docs/security/data-sovereignty.md` |
| AML / KYC / Travel Rule | `docs/security/aml-kyc-policy.md` |
| Audit readiness | `docs/security/audit-readiness.md` |
| Secrets | never committed; `.env.example` only; sealed-secrets in `infra/security/` |
| Transport | TLS 1.3 everywhere; mTLS between services |
| At rest | AES-256; field-level encryption for PII and NID numbers |
| Key management | envelope encryption, KMS-backed, 90-day rotation |
| Audit log | append-only, hash-chained, in `services/audit/` |

## Responsible AI security
Prompt injection is treated as an untrusted-input problem. Retrieved documents and user
messages are data, never instructions. Agents operate against an allow-listed tool
surface with per-tool authorisation, and no agent may move funds without a human gate.
