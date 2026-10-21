# Phase 2 — Design system, shells, landing page (Sara; Raisa: copy)

Skills loaded: frontend-design, skill-creator, cropguardian-safety, cropguardian-ui (created today).

## 17 Oct section (executed 2026-10-21)
Scope: Sara — `cropguardian-ui` skill + tokens. Raisa — Bangla style guide, first `bn.json` strings, personas review.

Built
- `.claude/skills/cropguardian-ui/SKILL.md` from spec 15 (tokens, typography, motion, components, layout, low-literacy rules, quality bar, microcopy).
- `frontend/src/design/`: `tokens.css` + `tokens.ts` (light/dark), `contrast.ts`, `motion.ts`; Tailwind mapped to CSS variables; self-hosted fonts.
- `frontend/src/i18n/`: `bn.json` (source) and `en.json` — landing, scan, result, not-sure, not-rice, outbox, demo, errors, disease names; `index.ts`.
- `docs/BANGLA_STYLE.md`, `docs/product/personas.md` (added the reviewer persona; aligned with the human-approved alert flow).

Tests (63, all pass): WCAG contrast of every text/background pair in both themes (7:1 farmer primary text), tokens.css/tokens.ts
drift test, motion tokens, i18n completeness (key parity, Bengali script, danda, ≤ 15-word sentences, placeholders, no
percentages in farmer copy), App render, plus build-time CSP-compat check and a Chromium smoke test through Nginx.

Findings recorded in DECISIONS: D-007 (spec `--text-subtle` colour fails AA by 0.004; derived dark-theme status colours).
Exit check: contrast test green; skill committed → **met** (nothing committed to git by request).
Not done (later days): primitives, i18n lint wiring in CI, shells, landing page, 3D hero.
