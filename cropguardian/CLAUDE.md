# CLAUDE.md — Crop Guardian working rules (spec: ../CROP_GUARDIAN_BUILD_SPEC.md)

The Build Spec is the baseline and supersedes older `docs/` text where they differ
(DECISIONS.md D-001). Read §0 and §1 first; then only the phase section + sections it references.

## Workflow (every phase)
1. `/clear`, Shift+Tab to Plan Mode. Write a plan to `docs/plans/phase-NN.md`, show ≤15 lines, WAIT.
2. Implement exactly the approved plan. Deviations → `DECISIONS.md`.
3. Run `/security-review` on the diff → `docs/security-reviews/phase-NN.md`.
4. `make gate PHASE=N` must print `PHASE N GATE: PASS`. Then update `PROGRESS.md`, commit, stop.

## Hard rules (spec §0.2)
- Fail closed. Deny by default. Security is part of every phase; never weaken a default for a test/demo.
- Honesty: no metric without a committed script + split; synthetic data labelled SIMULATED / DEMO DATA
  (`"synthetic": true`); advice says "not yet reviewed by an agronomist"; never claim field loss reduction.
- Every third-party statistic is in `docs/research/sources.md` with URL + access date.
- Alerts need human approval (reviewer + step-up 2FA). Nothing automated reaches farmers.
- Bangla is the source locale: strings go in `frontend/src/i18n/bn.json` first.
- Never log secrets/PII (passwords, tokens, OTPs, sessions, phones, exact coordinates, image bytes).
- LLM never receives personal data or images. Images never leave our systems.
- Pure logic stays pure: `backend/app/domain/` has no DB, network, framework or wall clock.
- Times stored UTC (`timestamptz`), shown in Asia/Dhaka.
- No tests that only cover the happy path; every unit tests invalid input + failure modes.
- Out of scope: native apps, payments, IoT/satellite, crops other than rice, real SMS in demo.

## Layout (spec §4, rooted at this directory)
`backend/` FastAPI · `frontend/` React+Vite · `infra/` nginx, postgres init, render.yaml · `ml/` · `kb/` ·
`e2e/` Playwright · `docs/` · `runs/` gate reports. Legacy `services/api` + `apps/web` keep the hosted
skeleton alive until cut-over (DECISIONS.md D-002).

## Commands
`make env certs up` · `make test` · `make security` · `make gate PHASE=N` · `make migrate` · `make down`
Python 3.12 in Docker; local venv may be newer. Dependencies pinned; add only if the spec names them.

## Branches / ownership
`track/platform` Apon · `track/ml` Taeen · `track/rag` Salwa · `track/agent` Raisa · `track/web` Sara.
Small PRs to `main` at least daily. CODEOWNERS in `.github/CODEOWNERS`.

## Skills
`.claude/skills/`: cropguardian-safety (every phase), cropguardian-ui + frontend-design (every frontend
task; cropguardian-ui wins). List the skills loaded at the top of each plan.
