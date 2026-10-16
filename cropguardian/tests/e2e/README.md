# End-to-end & accessibility tests (Playwright)

Owner: Sara. Run against local dev, then against the deployed Render URLs. Every journey runs in
**Bangla and English** at **360 × 740**. Files to create: `journeys.spec.ts`, `a11y.spec.ts`.
Command: `npx playwright test tests/e2e` with `BASE_URL=<web URL>`.

| ID | Journey | Expected |
|---|---|---|
| E1 | `/demo-user` → CAPTCHA widget → enter | lands on `/app`; synthetic banner visible |
| E2 | scan fixture leaf | result with top-3, band, cited advice |
| E3 | non-leaf photo | "Not sure", retake tips, office card; **no disease named as answer** |
| E4 | offline → capture → online | queued badge, then auto-sent, result shown |
| E5 | API delayed 60 s (cold start) | waking message, then result |
| E6 | open `/audit` directly (deep link) | loads (SPA rewrite works) |
| E7 | farmer opens `/admin` | nothing rendered; API 403; admin chunk not loaded |
| E8 | `/demo-admin` → change τ without reason / with reason | blocked / saved and visible in audit |
| E9 | admin dismisses an alert | disappears from farmer alerts |
| E10 | language toggle on every page | no missing strings, no overflow |

Accessibility: axe-core (WCAG 2 A/AA) on `/app`, `/demo-user`, `/admin`, `/data`, `/security`,
`/architecture`, `/presentation`, `/pitchdeck`, `/audit` — zero serious or critical violations.
