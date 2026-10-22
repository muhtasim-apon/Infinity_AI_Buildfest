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

## 21 Oct - approved plan for the rest of Phase 2 (solo; no commit, no push)
Skills loaded: cropguardian-safety, cropguardian-ui, frontend-design, webapp-testing (threejs-* only in Block 3).
Full plan (state audit, blocks, tests, gate definition, solo prompts, Vercel verification): `C:\Users\Hp\.claude\plans\playful-prancing-rossum.md`; decisions D-020..D-024 in `DECISIONS.md`.

State at start (audited): DONE skill + tokens + contrast + motion + i18n base + guards/auth pages/403-404/DEMO ribbon (Phase 1).
MISSING: ESLint duration/colour rules, primitives + chips + states + toast, formatters, `check_i18n.py`, farmer/staff/public shells, offline page, `/app` routes, landing + 3D hero + stills, `/demo` styling, `/dev/ui-kit`, P2 gate steps (E2E widths, axe, visual, Lighthouse, budgets, stills manifest), Makefile `a11y/visual/lighthouse/gallery`.

Blocks: **1** primitives + i18n tooling + lint + gate scaffolding (21 Oct) - **2** shells, guards, offline, ui-kit, `/app` rename (22 Oct) - **3** landing copy + landing + 3D hero + stills + baselines (23 Oct am) - **4** verify: security-review, gate PASS, regression gates 0/1, Vercel preview checklist (23 Oct pm).
Migrations/endpoints: none (frontend + gate scripts only). Security row: spec 16.21 row 2. Corner case: CC-40. Gate: `make gate PHASE=2`.

### Block 1 - DONE 2026-10-21 (primitives, i18n tooling, lint, gate scaffolding)
Built (all verified locally):
- Dependencies pinned (D-021, amended by D-025/D-026): framer-motion, lucide-react, cva/clsx/tailwind-merge, cmdk, three 0.186.1, fiber 8.18.0 + drei 9.122.0 (React 18), Radix (slot, popover, dropdown-menu, tooltip, tabs, toast, checkbox, radio-group, switch, slider, progress, label), lighthouse, @axe-core/playwright.
- Lint: ESLint rules forbidding hex colours and numeric durations outside `src/design` (`tests/eslint-rules.test.ts`, 7 tests).
- Tokens: `duration` press/fast/shake/base/slow/page/reveal/draw + toast/tooltip constants in `motion.ts`, mirrored to `tokens.css` and Tailwind (drift test), in-app reduced-motion and text-scale switches, `motion-ok:` variant.
- `src/lib`: `format.ts` (Bangla digits, Dhaka dates `১৬ অক্টোবর ২০২৬`, relative time, days, compact, percent; 16 tests), `uiPrefs.ts` (validated storage, 11 tests), `cn.ts`, `zodConfig.ts` (D-027).
- `src/design`: `variants.ts` (catalogue + `reducedVariants`), `useMotion.ts` (OS + in-app + data-saver + low-battery policy).
- `src/components/ui`: Button/IconButton, Input/Textarea/FormField/CharacterCounter, Badge/SimulatedBadge, ConfidenceBandChip/RiskChip, Card/StatCard, Skeleton/EmptyState/ErrorState, Toaster (Radix toast), Modal/Sheet/ConfirmDialog (native `<dialog>`, D-025), Tabs/SegmentedControl, SwitchField/CheckboxField/RadioCards/SliderField/NativeSelect, Progress/Meter/Ring/Stepper, Tooltip/Popover/DropdownMenu, Reveal. 72 component tests incl. axe, keyboard, failure paths.
- Tooling: `backend/scripts/check_i18n.py` (+20 tests, wired into gate step 6 from P2), `frontend/scripts/check-budgets.mjs` + `lib/budgets.mjs` (+12 tests, part of `npm run build`), Playwright projects w360/w768/w1366/slow3g + `fixtures.ts` (CSP-violation capture) + `screens.ts` + `a11y.spec.ts`, Makefile `budgets/a11y/visual/visual-update/lighthouse/gallery`, P2 steps in `phase_gate.py` (fail when unbuilt; +10 tests).
Defects found by the new gates and fixed: Bangla fonts 192.7 KB over the 120 KB budget (D-026); Zod probing eval under the strict CSP (D-027); Phase 1 register page rendered consent checkboxes with no accessible name while loading (D-028).
Result: frontend 262 tests, i18n/format/prefs/gate backend unit tests green, lint + tsc + build + budgets + CSP check pass, **axe E2E 84/84** (7 screens x light/dark x bn/en x 360/768/1366, zero CSP violations).
Gate `make gate PHASE=2` (keep-going) now fails ONLY on: security review file (Block 4), layout/shells E2E spec (Block 2), visual spec, Lighthouse script, stills manifest (Block 3). No other step fails.
Not done in Block 1 (moved): `/security-review` on the diff runs once at Block 4 over the whole P2 diff.
