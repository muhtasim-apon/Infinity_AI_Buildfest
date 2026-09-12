# Workflow 12 — onboarding_nurture_bangla

**Trigger:** Event: user.registered
**Human gate:** No

## Purpose

Staged Bangla onboarding including scam-awareness education

## Design note

Scam education is concrete and specific, not generic warnings. Persona P2 has already been targeted once. Messages are voice-capable for low-literacy users.

## Standing conventions

- **Idempotent.** Safe to re-run; schedules fire more often than expected.
- **Fails loud.** Dead-man's switch: absence of a success heartbeat pages on-call.
  A stopped workflow produces no error, so its silence must be the alarm.
- **No secrets in the repo.** Credentials are sealed-secrets only.
- **No PII leaves the boundary.** Subject to the same egress filter as application
  code (ADR 0011).

## Artefact

Exported JSON lives alongside this spec as `12_onboarding_nurture_bangla.json`. The JSON is the machine
representation; **this spec is what gets reviewed**, because workflow JSON diffs poorly.

Never imported or executed.
