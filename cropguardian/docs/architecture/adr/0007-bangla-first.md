# ADR 0007 — Bangla is the source locale

**Status:** Accepted · **Date:** 2026-10-16 · **Deciders:** Sara, Raisa

## Context
The guide lists "No Bangla / localization (English-only)" as a top-10 mistake (S1 §13.4 #6) and
asks for Bangla consideration in the preliminary stage (§9.2). Many farmers have limited literacy.

## Decision
`bn.json` is the source of truth; `en.json` must have the same keys (CI gate). Default locale
`bn`. Bangla web font (Noto Sans Bengali / Hind Siliguri) subset-loaded. Icons + colour + voice
playback (Web Speech API `bn-BD` where available, pre-recorded audio for the key messages as
fallback). Numbers shown in Bangla digits in `bn`. Advisory generated in Bangla directly from
Bangla KB text, not machine-translated from English where a Bangla source exists.

## Consequences
+ Usable by the actual users. − Two-language QA on every screen (Playwright runs both locales).
