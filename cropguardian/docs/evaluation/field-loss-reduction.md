# Evaluation — how much field-level loss can Crop Guardian reduce?

Owner: **Taeen** (analysis) · **Raisa** (pitch wording) · reviewed by the whole team.
Status: **pre-registration-style evaluation — nothing here is a measured result.** Evidence IDs point to
[`docs/research/sources.md`](../research/sources.md); resources: [`external-resources.md`](../research/external-resources.md).
The challenge's winning signal is *"loss reduction at the field level"* (S1 §6.4).

---

## 1. Bottom line (honest)

1. **No published randomized study shows that a photo-based crop-disease app reduces yield loss.** For the
   best-known apps we found accuracy and adoption studies, not yield-impact trials (§2).
2. The **closest causal evidence** is for digital agricultural *advice* in general: on average about
   **+4 % yield** (meta-analysis, S8) and **+6 % yield, 95 % CI +2 to +9 %** (20 studies, S9).
3. Rice loses a lot to pests and pathogens (global estimate **30 %, range 24.6–40.9 %**, S6), and local
   outbreaks in Bangladesh can be severe (blast **up to 80 %** in affected places, S3). So the *room* for
   improvement is large; the open question is how much of it an app actually captures.
4. Our transparent model (§4) says: averaged over all farmers the effect is likely **small (well under a
   few percentage points of yield)**. For a farmer who uses the app in time **during an outbreak**, the
   avoided loss could be **substantial**. These are **illustrative scenarios built on stated assumptions,
   not predictions.**
5. We will **not claim any loss reduction until the pilot measures it** (§6).

## 2. What the evidence says — and does not say

| ID | Evidence | Finding | What it tells us | What it does **not** tell us |
|---|---|---|---|---|
| S6 | Savary et al. 2019 (expert survey, 219 experts, 67 countries) | global rice yield loss to pests & pathogens 30.0 % (24.6–40.9 %); major causes include sheath blight, blast, brown spot, bacterial blight | the size of the problem for rice; our target diseases are among the main ones | Bangladesh-specific loss; how much is avoidable |
| S7 | FAO 2021 | up to 40 % of global crop production lost to pests each year | upper-bound framing | a precise figure ("up to") |
| S2 | Bangladesh state institutes via Mongabay 2024 | up to 62 % loss *if* major outbreaks are frequent; BRRI average national insect loss 1.0 % | outbreaks matter far more than averages | how the 62 % was computed |
| S3 | BRRI via TBS | blast cut yield by up to 80 % in some places in one boro season | outbreak fields are where avoided loss is largest | national average |
| S4 | BRRI-linked review | no precise, updated national rice-disease loss figure | we must measure our own baseline | — |
| S8 | Fabregas, Kremer & Schilbach 2019 (*Science*) | digital ag information: +4 % yields, +22 % odds of adopting recommended inputs | phone-delivered advice changes behaviour and yields a little, cheaply | effect of *photo diagnosis*; Bangladesh |
| S9 | Beach et al. 2025 (*Global Food Security*, 20 studies) | yield +6 % (95 % CI +2 to +9 %), income +6 % | a realistic average range for digital advice | effect on disease losses specifically |
| S10 | CABI Case Study 19 — 30 plant clinics, 10 districts, Bangladesh | regular clinic users reported higher yields/profits | a Bangladeshi diagnosis-and-advice service is used and valued | causation (users self-selected) |
| S11 | Nuru diagnosis study (Mrisho et al. 2020) | 74–88 % accuracy with six leaves per plant, better than extension agents | phone AI can diagnose as well as people in the field | yield impact |
| — | Literature search, 2026-10-16 | no randomized evaluation of image-based disease apps on yield found | the gap our pilot can fill | — |

## 3. Impact pathway — where the effect can break

```
disease appears ─▶ farmer notices and opens the app in time (u)
   ─▶ model answers and is correct (d)  ── or says "not sure" (no harm, no gain unless the retake succeeds)
   ─▶ advice understood and followed (a)
   ─▶ recommended action actually stops the damage (e)
   ─▶ loss avoided on THIS field
   +  rule-based alert warns neighbours earlier ─▶ same chain on their fields (spill-over)
```
Every arrow is a place the effect shrinks. The biggest risks: farmers notice too late, the disease is
not one of our 7 classes, photo quality forces "not sure", advice is not followed, or the disease (e.g.
tungro, a virus) has no curative treatment — only roguing and vector control.

## 4. Transparent impact model (illustrative)

**Avoided loss (percentage points of yield) = L × d × a × e**, for a field where the app was used in
time. Averaged over all farmers in an area, multiply by **u**.

| Symbol | Meaning | Conservative | Moderate | Optimistic | Grounding |
|---|---|---|---|---|---|
| L (average field) | % of yield lost to the diseases we cover, in an ordinary season | 5 | 10 | 15 | subset of the 24.6–40.9 % total for pests & pathogens (S6) |
| L (outbreak field) | same, in a field hit by an outbreak | 30 | 50 | 80 | outbreak reports up to 62–80 % (S2, S3) |
| d | share of scans answered **and** correct | 0.50 | 0.65 | 0.80 | depends on coverage at τ — **measure** ([eval-plan](../ai/eval-plan.md)) |
| a | share of farmers who follow the advice | 0.40 | 0.60 | 0.80 | digital advice raises adoption odds by 22 % (S8) — adherence itself **unknown**, measure |
| e | share of the remaining loss the recommended action prevents when applied in time | 0.30 | 0.50 | 0.70 | depends on disease and timing — **assumption**, to be replaced by guide/trial data |
| u | share of affected fields where the app is used in time | 0.10 | 0.25 | 0.50 | smartphone access and adoption (Nuru adoption 45 % in one study) — **measure** |

**Scenario results** (arithmetic computed by script; inputs are assumptions, not data):

| Scenario | Field that used the app — ordinary season | Field that used the app — outbreak | All farmers (× u) — ordinary | All farmers (× u) — outbreak |
|---|---|---|---|---|
| Conservative | 0.30 pp | 1.80 pp | 0.03 pp | 0.18 pp |
| Moderate | 1.95 pp | 9.75 pp | 0.49 pp | 2.44 pp |
| Optimistic | 6.72 pp | 35.84 pp | 3.36 pp | 17.92 pp |

*pp = percentage points of the field's potential yield.* Example (moderate, outbreak field):
50 × 0.65 × 0.60 × 0.50 = 9.75 pp.

**How to read this:**

- For one farmer in an outbreak who uses the app in time, the moderate case avoids roughly a tenth of
  the potential yield — that is where Crop Guardian is most valuable.
- Averaged across a whole area in an ordinary season, the moderate case is under 1 pp, the same order as
  the +4 % to +6 % average yield effects of digital advice (S8, S9) — a plausible, modest range.
- The optimistic column needs high accuracy, high adherence and wide adoption all at once; treat it as a
  ceiling, not a target.
- The **early-warning alerts are not in this model** (they add spill-over to neighbours); they are measured
  separately as alert lead time.

## 5. What raises or limits the effect — and what we do about it
| Factor | Effect | Lever in our design |
|---|---|---|
| Disease not in our 7 classes | d = 0 for that case | honest "not sure"; add classes (e.g. leaf scald from D5); pest classes later |
| Photo quality / abstention | lowers d | quality hints, retake flow, robustness training |
| Late detection | lowers e | outbreak alerts prompt neighbours to check fields early |
| Advice not followed | lowers a | simple Bangla, voice, IPM-first steps, cited source builds trust |
| No curative treatment (tungro) | lowers e | advice focuses on roguing and vector control; honest wording |
| Smartphone access / reach | lowers u | light PWA, offline capture, works on low-end phones |
| Wrong alerts | could cause unnecessary spraying | conservative rules, "unverified" label, in-app only, admin dismiss |

## 6. How we will measure it
**Before 31 Oct (preliminary) — leading indicators we *can* measure:**
diagnostic macro-F1 with 95 % CI on Bangladeshi field photos · coverage and selective accuracy at τ ·
not-sure rate · time-to-advice · citation coverage · advice comprehension in usability sessions
([eval-plan](../ai/eval-plan.md), [usability protocol](../../tests/manual/usability-protocol.md)).

**After the preliminary — the field pilot** ([pilot protocol](../product/pilot-protocol.md)):
- **Design:** villages randomly assigned to app vs usual practice (cluster randomisation), or a matched
  comparison if randomisation is not possible. Same variety and season.
- **Primary outcome:** yield per decimal at harvest. **Secondary:** days from first symptom to
  correct treatment; disease-affected area at a fixed stage; number of pesticide applications; alert
  lead time vs official reports.
- **Sample size (illustrative, assumptions stated):** yield coefficient of variation 25 %, two-sided
  α = 0.05, power 80 %, 10 fields per village, intra-village correlation 0.05 (design effect 1.45):

| Smallest effect to detect | Fields per arm (individual) | Fields per arm (clustered) | Villages per arm |
|---|---|---|---|
| 10 % yield difference | 99 | 143 | 15 |
| 5 % yield difference | 393 | 570 | 57 |
| 5 % with CV 30 % | 566 | 820 | 82 |

  Formula: n per arm = 2 (z₁₋α/₂ + z₁₋β)² · CV² / Δ², multiplied by 1 + (m − 1)·ICC for clustering.
  Because realistic average effects are in the single digits (S8, S9), a convincing trial needs
  **hundreds of fields per arm** — or it should target **outbreak-prone areas**, where the expected
  effect is larger and a smaller sample suffices.
- **Analysis & reporting:** pre-register outcomes; difference in means with 95 % CI; regression adjusting
  for variety, sowing date and area; report null results; publish the not-sure and dismiss rates.

## 7. What we may and may not say (pitch, video, judges)
| ✅ We may say | ❌ We may not say |
|---|---|
| "Rice loses an estimated 30 % of yield to pests and pathogens worldwide (Savary et al. 2019)." | "Crop Guardian reduces losses by X %." |
| "Phone-based farm advice has raised yields by about 4–6 % on average in other countries (meta-analyses)." | "Farmers using our app gained X % yield." |
| "Our biggest value is early, correct action in outbreak fields; we will measure loss reduction in a pilot." | Any accuracy number before the evaluation report exists. |
| "When the model is unsure, it says so instead of guessing." | "Our AI is as good as an expert." (not measured) |
