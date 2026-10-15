# ADR 0001 — React + Vite SPA delivered as a PWA; no native app

**Status:** Accepted · **Date:** 2026-10-16 · **Deciders:** Sara, Apon

## Context
The team scope is web only. Farmers use low-end Android phones on unreliable networks.
Judges need public URLs for every section (S1 §10.7–10.8 pattern). Render serves static sites
for free without spin-down [R1].

## Decision
React 18 + Vite + TypeScript (strict), React Router, TanStack Query, i18next, Workbox
service worker, IndexedDB (idb-keyval) for the offline outbox. Deployed as a Render static site
with an SPA rewrite rule.

## Alternatives rejected
- **Next.js (SSR)** — needs a Node server → a second sleeping free service and more hours.
- **Flutter Web** — large initial bundle on slow networks; team frontend skills are React.
- **Native Android** — out of scope (web only); store review delays.

## Consequences
+ Frontend is always up even when the API sleeps; it can show a "waking server" state.
+ Installable to the home screen, works offline for capture.
− SEO irrelevant here; no SSR needed. − iOS PWA background sync is limited → manual "send now".
