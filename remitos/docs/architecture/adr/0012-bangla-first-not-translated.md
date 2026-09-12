# ADR 0012 — Bangla-first, not English-translated

**Status:** Accepted · **Date:** 2026-09-12

## Context

Congress §13.4 lists "No Bangla / localization (English-only)" as mistake #6, and §14
requires "Bangla + localization capability". Most teams will satisfy this with a
translation file and a language toggle.

That is not localisation, and the difference is visible to anyone who has watched a
rural user attempt an English-designed financial flow. The failures are structural:

- Layouts are designed for English string lengths; Bangla equivalents overflow or
  truncate. Bengali is frequently 20–40 % longer for the same meaning.
- Bengali conjunct rendering (যুক্তাক্ষর) breaks in fonts chosen for Latin text.
- Amounts are shown as `1,20,000` in Bangladesh — the South Asian lakh/crore grouping —
  not `120,000`. Getting this wrong on a *money* screen destroys trust instantly.
- Bengali numerals (১২৩) are what many older users read fluently; Arabic numerals are not
  automatically legible to them.
- Financial vocabulary translated literally produces English-in-Bengali-script that
  native speakers do not actually use.
- Voice interfaces trained on formal Bangla fail against regional dialect.

## Decision

Bangla is the **source language of design**. English is the alternate.

1. **Design in Bangla first.** Every screen is laid out with Bangla strings; English must
   fit the Bangla layout, not the reverse.
2. **Typography** — a Bengali-complete typeface with verified conjunct coverage, chosen
   before the Latin face. Line-height and letter-spacing are tuned for Bengali, which
   needs more vertical room than Latin.
3. **Numerals** — user-selectable Bengali/Arabic digits; **lakh/crore grouping by default**
   for BDT amounts.
4. **Vocabulary** — a reviewed financial glossary in `data/dictionaries/`, using the words
   people actually use for money, not dictionary translations. Reviewed by native
   speakers, not by a model.
5. **Voice** — Bangla ASR/TTS with regional-dialect evaluation sets in
   `ml/models/bangla_nlu/`. A voice interface that only understands Dhaka-standard
   Bangla has failed the users it was built for.
6. **Every AI output is Bangla-capable** — routing rationales, compliance explanations
   and support replies are generated in Bangla, not generated in English and translated.
   Translation of a generated explanation reliably loses the explanation.
7. **Enforcement** — CI fails on any user-facing string missing from `app_bn.arb`, so
   English-only strings cannot reach `main`.

## Consequences

**Positive** — the product is genuinely usable by the people it claims to serve; it
directly satisfies §14 in a way a language toggle does not; it is demonstrable on stage
in five seconds by switching a screen and showing nothing breaks.

**Negative** — slower design iteration when the team thinks in English; a dependency on
native reviewers for vocabulary; Bangla evaluation sets for ASR must be built, since good
open ones are scarce. Larger font payload, which fights the under-50 KB low-bandwidth
target — resolved by subsetting the Bengali face to the glyphs actually used.

**Rejected** — English-first with a translation pass (mistake #6, exactly as written);
machine translation at runtime (wrong financial vocabulary, and it fails offline);
English-only with a "Bangla coming soon" note (the population that needs it most is
excluded, which is the opposite of the product's stated purpose).
