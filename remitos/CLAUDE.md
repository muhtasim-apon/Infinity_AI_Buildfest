# CLAUDE.md — conventions for AI-assisted work in this repository

## What this repository is
A production-grade **architectural template**. Source files are typed, documented stubs.
Nothing here has been compiled, installed, deployed or run. Do not claim otherwise in
any document, commit message or demo.

## Hard rules
1. **No fabricated data.** Congress section 20.4 prohibits fabricated demos and simulated
   results presented as real. Synthetic data lives only in `data/synthetic/` and every
   surface that renders it must label it synthetic.
2. **No uncited statistics.** A number may appear in `docs/` only if it exists in
   `docs/research/data/*.md` with a source URL and access date.
3. **Bangla is not a translation layer.** It is the default. English is the alternate.
   Any feature shipped English-only is incomplete.
4. **Every AI decision that touches money must be explainable.** Model output affecting
   user funds carries a reason code and, for RAG paths, a citation.
5. **Regulatory limits are constraints, not validations.** Bangladesh Bank ceilings
   belong in the optimiser constraint set, not in an error message after the fact.

## Code conventions
- **Flutter** — Clean Architecture per feature: `data/` then `domain/` then
  `presentation/`. The domain layer imports nothing from data or presentation. BLoC for
  state. No business logic in widgets.
- **Services** — Python 3.12 + FastAPI + Pydantic v2. One service, one bounded context,
  one database. Services communicate by event or by explicit API contract in
  `packages/api-contracts/`, never by shared database.
- **ML** — every model needs a model card in `docs/ai/model-cards/` before it is
  referenced anywhere else.
- **Naming** — snake_case for Python and Dart files, PascalCase for Dart classes,
  kebab-case for directories and service names.

## Documentation conventions
- Architecture decisions are ADRs in `docs/architecture/adr/`, numbered, never edited
  after acceptance — superseded by a new ADR instead.
- Diagrams are authored as Mermaid `.mmd` in `docs/diagrams/` and referenced, not pasted.

## Extending to a new fintech vertical
Add a pack under `apps/mobile/lib/domain_packs/` and `ml/` supplying config, schemas,
prompts and models. Do not modify core services to accommodate a vertical — if you must,
the abstraction is wrong and needs an ADR.
