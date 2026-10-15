# CLAUDE.md — conventions for AI-assisted work in this repository

## What this repository is
The Crop Guardian **web-app template and clickable prototype** for the International AI
Builders Congress 2026 (AgriSphere AI → Crop Guardian). Source files are typed, documented
stubs. Nothing has been installed, trained, deployed or run. Do not claim otherwise in any
document, commit message, slide or demo.

## Hard rules
1. **No fabricated results.** Congress §20.4 prohibits fabricated demos and simulated results
   presented as real. Synthetic data lives only in `db/seed_synthetic.sql`,
   `prototype/assets/synthetic-data.js` and `tests/fixtures/`; every surface that renders it
   shows the "SYNTHETIC DEMO DATA" banner.
2. **No uncited statistics.** A number may appear in `docs/` only if it is listed in
   `docs/research/sources.md` with a URL and access date. Model metrics appear only after
   they are measured, with the dataset split and commit that produced them.
3. **Bangla is the default, not a translation.** Every user-facing string exists in
   `bn.json` first. A feature shipped English-only is incomplete.
4. **The model may say "I don't know".** Below the calibrated confidence threshold the app
   shows "not sure — sent to an agronomist", never a guessed disease (ADR 0005).
5. **Advice must cite.** A treatment recommendation without a retrieved source chunk is not
   shown (ADR 0006). Pesticide advice always includes the safety line and dose from the source.
6. **Web only.** No native mobile code. The PWA is the mobile experience.
7. **Free-tier aware.** Anything that assumes a persistent local disk, more than one API
   instance, or an always-warm server is a bug on Render free (see
   `docs/deployment/challenges-and-recovery.md`).

## Code conventions
- **Frontend** — React + TypeScript strict, feature folders under `apps/web/src/features/`,
  no business logic in components, API calls only through `src/lib/api.ts`.
- **Backend** — Python 3.12, FastAPI, Pydantic v2. Routers are thin; logic in `app/services/`.
  Every endpoint declares a timeout budget and an error contract.
- **Database** — every table has `created_at`, RLS enabled, and an owner column or an
  explicit "public read" comment. Migrations are additive.
- **ML** — every model needs a card in `docs/ai/model-cards/` before it is referenced in code.
- **Naming** — snake_case Python/SQL, camelCase TS, PascalCase React components,
  kebab-case directories.

## Documentation conventions
- ADRs live in `docs/architecture/adr/`, are numbered, and are superseded, never edited.
- Diagrams are Mermaid `.mmd` in `docs/diagrams/`, referenced from Markdown.
- The report is assembled from `docs/report/parts/` by `scripts/build_report.py`.

## Extending to another AgriSphere challenge
Precision Farm, YieldMax and Climate Smart Farming are future **domain packs**
(`docs/architecture/adr/0010-domain-packs.md`): config, schemas, prompts and models only.
Do not modify the core to accommodate a pack.
