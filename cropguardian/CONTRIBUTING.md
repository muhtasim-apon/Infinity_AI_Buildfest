# Contributing

## Branching
`main` is protected. Work on `feat/<scope>`, `fix/<scope>`, `docs/<scope>`, `ml/<scope>`.
One reviewer from the owning role (see `.github/CODEOWNERS`) must approve.

## Commits
Conventional Commits, e.g. `feat(scan): add client-side image compression`.

## Definition of done
- [ ] Stub or code carries a docstring: contract, inputs, outputs, failure modes, timeout
- [ ] Tests added in the matching `tests/<type>/` folder (see `docs/testing/test-strategy.md`)
- [ ] Bangla string added to `apps/web/src/i18n/bn.json` before `en.json`
- [ ] Any new statistic is in `docs/research/sources.md` with URL + access date
- [ ] Any new model has a card in `docs/ai/model-cards/`
- [ ] Any architectural choice has an ADR
- [ ] `docs/congress/rubric-map.md` updated if a rubric line is affected
- [ ] Synthetic data is labelled synthetic wherever it renders

## Team roles (Congress §13.2 — mandatory, declared in the submission)

| Congress role | Owner | Also owns |
|---|---|---|
| Team Leader / Coordinator | **Apon** | Deployment (Render, Supabase), release freeze |
| Backend / Data Engineer | **Apon** (lead), **Taeen** | API, database, ML integration, n8n |
| Business Analyst / Data Scientist | **Taeen** | Datasets, training, statistics, KPIs |
| AI Integration — Knowledge & RAG | **Salwa** | KB ingestion, retrieval eval, LLM red-team |
| AI Integration — Agent & Bangla UX | **Raisa** | Advisory agent, prompts, Bangla voice copy |
| Presentation / Communication Lead | **Raisa** *(proposed — confirm at stand-up)* | Video pitch, deck, demo script |
| UI/UX / Frontend Developer | **Sara** | Prototype, web app, accessibility, PWA |
| Virtual NRB / Global Advisor (§8) | **Open — to recruit** | Architecture & go-to-market review |

Women participation (§13.3) is encouraged by the guide; record the final team composition in
the submission. NRB contributions, when an advisor joins, are recorded in
`docs/congress/nrb-log.md`; advisors may not influence judging (§20.8).

## Daily rhythm (16–29 Oct)
- 10:00 stand-up, 15 min — template in `docs/plan/daily-standup-template.md`
- 22:00 push + update your row in `docs/plan/gantt.md` (done / slipped / blocked)
