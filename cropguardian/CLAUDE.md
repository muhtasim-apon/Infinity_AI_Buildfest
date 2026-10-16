# CLAUDE.md — conventions for AI-assisted work in this repository

## What this repository is
The Crop Guardian **template** for the International AI Builders Congress 2026 (AgriSphere AI → Crop
Guardian). It contains **specifications and documentation only** — no application code yet — plus a
static clickable `prototype/`. The team implements the code piece by piece from the specs:
`services/api/SPEC.md`, `apps/web/SPEC.md`, `db/SCHEMA-SPEC.md`, test-case tables in `tests/`.
Nothing has been trained, deployed or run. Do not claim otherwise in any document, commit, slide or demo.

## Hard rules
1. **No fabricated results.** Congress §20.4 prohibits fabricated demos and simulated results presented
   as real. Synthetic data appears only in the prototype, demo seed and test fixtures, always labelled.
2. **No uncited statistics.** A number may appear in `docs/` only if it is in
   `docs/research/sources.md` with a URL and access date. Model metrics only from an evaluation report.
3. **Bangla is the default, not a translation.** Every user-facing string exists in
   `apps/web/i18n/bn.json` first.
4. **The model may say "I don't know".** Below the calibrated threshold the app shows "not sure" with
   retake tips and the local agriculture office card — never a guessed disease (ADR 0005).
5. **Advice must cite.** No advice without a retrieved source chunk (ADR 0006); dose verbatim, safety line.
6. **No human-review features** in this version (no expert queue, no alert approval). Alerts are
   automatic, rule-based, labelled "unverified", in-app only; the admin can dismiss them.
7. **Web only.** No native mobile code.
8. **Free-tier aware.** Nothing may rely on a persistent local disk, more than one API instance or an
   always-warm server (see `docs/deployment/04-free-tier-challenges.md`).
9. **Security checklist.** Every change keeps the 19 controls in `docs/security/security-checklist.md`
   true; run `/security-review` before opening a PR.

## Code conventions (for when the code is written)
- **Frontend** — React + TypeScript strict, feature folders under `apps/web/src/features/`, API calls only
  through `src/lib/api.ts`, LLM/KB text rendered as plain text.
- **Backend** — Python 3.12, FastAPI, Pydantic v2. Thin routers; logic in `app/services/`. Every endpoint
  has a timeout budget and an error contract; every admin action is audited.
- **Database** — RLS on every table; additive migrations; coarse location only.
- **ML** — every model has a card in `docs/ai/model-cards/` before it is referenced.
- **Naming** — snake_case Python/SQL, camelCase TS, PascalCase React components, kebab-case directories.

## Documentation conventions
- ADRs in `docs/architecture/adr/`, numbered, superseded rather than edited.
- Diagrams as Mermaid `.mmd` in `docs/diagrams/`.
- The PDF in `docs/report/` is generated from the Markdown docs (builder kept outside the repo).

## Extending to another AgriSphere challenge
Precision Farm, YieldMax and Climate Smart Farming are future **domain packs** (ADR 0010): config,
schemas, prompts and models only.
