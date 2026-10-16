# prototype/ — clickable static UI

Owner: **Sara**. Open `index.html` in any browser — **no build, no server, no install.**
Works from `file://`. Bangla by default; "English" button in the top bar; ◐ toggles dark mode.

| Page | Congress route | Shows |
|---|---|---|
| `index.html` | — | landing + links to every route |
| `app.html` | `/app` | home → scan → "waking server" → result (diagnosed / **not sure**) → cited advice + voice → history → alerts map |
| `demo-user.html` / `demo-admin.html` | `/demo-user` / `/demo-admin` | one-click entry (auto-redirect) |
| `admin.html` | `/admin` | overview, alerts (dismiss with reason), settings (reason required → audit), models, KB, users |
| `data.html` | `/data` | datasets with licences, lineage, "not yet measured" results |
| `security.html` | `/security` | controls, responsible-AI harms & mitigations |
| `architecture.html` | `/architecture` | system diagram (inline SVG), AI layer, free-tier engineering |
| `presentation.html` | `/presentation` | problem → users → solution → market → impact |
| `pitchdeck.html` | `/pitchdeck` | 11-slide deck, ← → keys |
| `audit.html` | `/audit` | one-click audit report |

## Honesty rules built in
- Every page shows the **SYNTHETIC** banner (`assets/app.js`).
- No model runs here. The scan screen lets you pick a *scenario* (blast / tungro / unclear); a photo you
  choose is only previewed locally — it is never uploaded.
- Advice text is marked as sample copy; citations are marked as placeholders until the KB is ingested.
- Metrics show "not yet measured".

## Files
`assets/style.css` (tokens, light/dark, phone-first) · `assets/app.js` (banner, top bar, language/theme,
tabs) · `assets/synthetic-data.js` (all demo data in one place). Bilingual text uses
`<span class="bn">…</span><span class="en">…</span>` pairs; the production app uses `apps/web/i18n/*.json` (moved to `src/i18n/` when scaffolded).

## Turning it into the real app
Each screen maps to a React feature in `apps/web/src/features/` (see `apps/web/README.md`).
