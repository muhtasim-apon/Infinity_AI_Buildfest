# Submission checklist — preliminary (deadline 31 Oct 2026, 12:00 BST)

Owner: Apon (A) · Raisa (R). Target submit: **Fri 30 Oct**.

## Package (S1 §9.1)
- [ ] Problem definition — SDD §1
- [ ] AI architecture — `/architecture` + SDD §6, §10
- [ ] Data & sovereignty strategy — datasets.md, data-sovereignty.md
- [ ] Demo (live URL + recorded video)
- [ ] Scalability roadmap — rubric-map §4, ADR 0010
- [ ] Ethical safeguards — responsible-ai.md

## Video (S1 §9.2) — exactly ≤ 180 s
- [ ] 0:00–0:30 Problem · 0:30–1:00 Solution · 1:00–2:00 Demo · 2:00–2:30 AI approach · 2:30–3:00 Impact & next step
- [ ] Bangla shown on screen; subtitles in English
- [ ] No unmeasured numbers; synthetic data labelled

## Public URLs (verify from a phone on mobile data, logged out)
- [ ] `/app` · [ ] `/demo-user` · [ ] `/demo-admin` · [ ] `/admin` · [ ] `/data` · [ ] `/security`
- [ ] `/architecture` · [ ] `/presentation` · [ ] `/pitchdeck` · [ ] `/audit`
- [ ] Repository public (or access granted) with README status statement

## Team declaration (S1 §13.2)
- [ ] Roles per member as in CONTRIBUTING.md (confirm Presentation lead)
- [ ] NRB advisor listed or stated as not yet recruited
- [ ] AI tool usage documented — `ai-usage-log.md`

## Integrity (S1 §20)
- [ ] Every statistic traces to `docs/research/sources.md`
- [ ] Dataset licences and attributions in the app (`/data`) and README
- [ ] Code of conduct agreement ticked by every member

## Operational (morning of submission)
- [ ] Supabase project active (not paused) · [ ] API warm · [ ] LLM budget OK
- [ ] Smoke test passes (n8n synthetic monitor green)
