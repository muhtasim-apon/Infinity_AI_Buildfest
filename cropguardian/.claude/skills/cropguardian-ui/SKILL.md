---
name: cropguardian-ui
description: Crop Guardian design system - tokens, Bangla typography, motion catalogue, components, layouts, low-literacy rules, quality bar and microcopy. Load for EVERY frontend task in this repository together with frontend-design; where they disagree, this skill wins.
---

# Crop Guardian UI skill (spec 15; source of truth: `CROP_GUARDIAN_BUILD_SPEC.md` section 15)

Two products, one language. **Farmer app** (`/app`): mobile-first, icon-first, Bangla-first, calm and warm, works on a low-end Android over slow 3G. **Staff console + public pages** (`/review`, `/admin`, `/`, `/trust`, `/map`, `/pitch`, `/demo`): dense, polished, Linear/Stripe-like. Every screen has loading (skeleton matching the final layout), empty, error (with request id) and success states; every action responds within 100 ms; nothing looks like an unstyled framework default.

## 1. Tokens (never invent colours)
Source: `frontend/src/design/tokens.ts` (mirrored by `tokens.css`; `tokens.test.ts` fails on drift; `contrast.test.ts` checks every text/background pair in both themes: 7:1 farmer primary text, 4.5:1 body, 3:1 large/UI).
- Light is the default (sunlight). Dark follows the OS for staff; the farmer app offers it in settings. Use CSS variables / Tailwind names (`bg-surface`, `text-muted`, `text-primary`...), never hex outside `design/tokens.*` (ESLint + `check_forbidden.py`).
- Primary = paddy green `--primary`; accent = rice gold; sky = weather/info; success / warning / danger for status; **`--simulated` purple is reserved for SIMULATED / DEMO DATA labels**.
- Disease categorical palette is Okabe-Ito (`--disease-1..7`), colour-blind safe, **always paired with name or icon**. Risk chips use `--risk-low/medium/high` with text.
- Known deviation: `--text-subtle` is `#657569` (spec value failed AA by 0.004), never use it on `--surface-2` (DECISIONS D-007).
- Spacing 4 px grid (4, 8, 12, 16, 20, 24, 32, 40, 48, 64). Radius sm 6, md 10 (inputs/buttons), lg 14 (cards), xl 20 (sheets/hero). Elevation xs/sm/md/lg; dark theme uses borders, not shadows. Focus ring: 3 px primary + 2 px offset on `:focus-visible`. Touch targets >= 48x48 px farmer, >= 44 elsewhere.

## 2. Typography (Bangla is not a translation of Latin)
- Stack: Noto Sans Bengali first for `lang="bn"`, Inter for Latin, JetBrains Mono for code. Self-hosted (`@fontsource`), `font-display: swap`, no external font requests.
- Latin scale (px/line): 12/16, 14/20, 16/24, 18/28, 20/28, 24/32, 30/38, 36/44 (landing hero 56/64). **Bangla: +2 px size and x1.15 line-height at every step.** Farmer body text is **18 px Bangla minimum**.
- Numbers: `tabular-nums`; Bangla numerals in the bn locale (`Intl.NumberFormat('bn-BD')`); dates `১৬ অক্টোবর ২০২৬` / `16 Oct 2026`; relative times with exact time in a tooltip. Durations "৪ দিন". CIs as "0.87 (0.84-0.90)", percentages <= 1 decimal.
- One `h1` per page. Sentence case. Avoid all-caps labels, single-word accent in headlines and eyebrow labels above every heading (frontend-design anti-patterns).

## 3. Motion (only `frontend/src/design/motion.ts` defines durations and easings)
Durations fast/base/slow/page = 120/200/320/240 ms; ease standard `(0.2,0,0,1)`, emphasized `(0.3,0,0,1)`, exit `(0.4,0,1,1)`; spring soft (260/26); list stagger 35 ms, max 8 items. Use only the catalogue in spec 15.2 (buttons, farmer scan button breathing ring, cards, page transitions, camera viewfinder brackets, analyzing scan-line driven by **real events never fake timers**, result reveal, advice card, not-sure card slide-up with **no shake and no red**, outbox bump, outbreak map ripples, alert approval stamp, dialogs/sheets, toasts, tabs, skeletons, stat count-up, charts, form-error shake, success check).
- Reduced motion (OS or in-app): no transforms, scale, shimmer, sweeps, pulses, count-ups, drawing; <= 120 ms opacity fades; analyzing shows a static progress list. Data saver or battery < 20%: disable looping animations. Motion never delays content by more than 300 ms.

## 4. Components (shadcn/ui primitives restyled with tokens)
Button (primary/secondary/outline/ghost/destructive/link; sm/md/lg/xl-farmer; icon-only needs `aria-label`; loading keeps width) - inputs, selects, switches, sliders, date picker with Bangla months - form field (label, hint, error, required) - cards, stat card - **Badge (status = icon + text), Simulated badge, Confidence band chip, Risk chip** - tabs, breadcrumbs - data table (sticky header, 44 px rows, hover not zebra, numbers right-aligned, collapses to cards < 768 px) - dialog/alert dialog (typed confirmation for destructive) - sheet, popover, tooltip, command palette (staff) - toast (5 s, pause on hover) - skeleton, empty state, error state - stepper, timeline, progress/meter/ring - charts with "View as table".
Domain composites: `CameraCapture` (file-input fallback always), `PhotoQualityHints`, `ScanProgress`, `DiagnosisHero`, `AdviceCard`, `CitationChip` + `SourceViewer`, `NotSureCard`, `OutboxBadge`, `AlertCard`, `OutbreakMap` (d3-geo SVG, keyboard-focusable, table alternative), `ReviewCard`, `AlertDraftEditor`, `ModelVersionCard`, `SimulationConsole`, `PhoneFrame`, `TrustSection` (measured / "Not yet measured" markers). Details in spec 15.3.

## 5. Layout and navigation
- Farmer shell: top bar 56 px (logo ফসল রক্ষী, language toggle বাংলা/EN, outbox badge, notifications) + bottom tab bar 64 px with safe area: হোম · ছবি (raised centre) · ইতিহাস · সতর্কতা · আরও. On >= 768 px a centred 480 px column; never stretch wide.
- Staff shell: top bar 64 px, sidebar 248 px (rail 72 px < 1280, drawer < 1024), content max 1280 px, `DEMO`/`SIMULATED` badge when relevant. Public nav: logo, How it works, Trust, Map, Pitch, Try the demo, Sign in.
- Route guards (15.4): unauthenticated -> `/login?return_to=<validated>`; wrong role -> `/403` (admin -> `/404`); PENDING -> `/verify`; staff without TOTP -> `/setup-2fa`; demo sessions always show the purple **DEMO DATA** ribbon.
- Breakpoints sm 640, md 768, lg 1024, xl 1280. Check 360x740 (primary farmer target), 390, 412, 768, 1024, 1366x768, 1440, 1920.

## 6. Low-literacy and field rules (farmer app)
1. One primary action per screen, >= 56 px tall, icon + short Bangla verb. 2. Icons and pictures carry meaning; text supports them (reference disease illustrations are team-drawn SVG, no copyrighted photos). 3. Read-aloud button on every advice, alert and not-sure card. 4. <= 3 taps from opening the app to a result. 5. **No raw percentages for farmers**: bands (উচ্চ / মাঝারি) and plain sentences. 6. Light theme default, primary text >= 7:1. 7. Forgiving input: Bangla digits, spaces, `+880`/`0` prefixes, OTP paste. 8. **Never blame**: errors say what to do ("আলো বেশি এমন জায়গায় আবার ছবি তুলুন"). 9. Data-light: images compressed on device, no autoplay media, subset fonts.

## 7. Quality bar (reviewed at every readiness check)
Page header: breadcrumb -> h1 (24/32, 600) -> one-line muted description -> primary action right. Cards on `--bg`: radius 14, 1 px border, shadow xs, 24 px gutters (16 mobile). One primary button per view; destructive in danger style with confirmation. Charts: no 3D, no gradients behind data, light grid, 12 px muted labels, token series colours, exact-value tooltips. Icons: lucide 16/20 px, stroke 1.75, paired with text except close/more/search (need `aria-label`). **Simulated or demo data always carries the purple SIMULATED badge and is never mixed silently with real data.**

## 8. Engineering rules that affect UI code
No literal user-facing strings in JSX (`i18next/no-literal-string`; add keys to `bn.json` FIRST, then `en.json`; `check_i18n` fails on missing keys). No `dangerouslySetInnerHTML`/`innerHTML`/`eval`/inline handlers/external URLs; LLM and KB text is rendered as plain text. API calls only through `src/lib/api.ts`; data via TanStack Query hooks in `features/*/api.ts`. Bundle budgets: farmer initial JS <= 170 KB gzip, route chunk <= 120 KB, staff initial <= 250 KB, landing 3D chunk <= 220 KB (lazy), Bangla font subset <= 120 KB. WCAG 2.1 AA: keyboard access, visible focus, `aria-live="polite"` for progress/toasts/errors, status never by colour alone, 200% zoom without horizontal scroll, `prefers-reduced-motion` honoured.

## 9. Microcopy (voice)
Respectful "আপনি"; sentences <= 15 words; one idea per step; verbs first; Bangla numerals; terms simple ("প্রতি লিটার পানিতে"); never fear words in alerts; actions keep one name through the whole flow ("সংরক্ষণ করুন" then "সংরক্ষণ হয়েছে"). Errors explain what happened and how to fix it; they never apologise or blame. Full guide: `docs/BANGLA_STYLE.md`.

## 10. Process
Plan tokens/layout first (frontend-design), then build; verify at 360/390/1366 in light and dark, bn and en, reduced motion; run `npm run lint && npm test && npm run build`; screenshot with webapp-testing before claiming done.
