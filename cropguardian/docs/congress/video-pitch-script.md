# 3-minute video pitch — script (S1 §9.2 structure)

Owner: Raisa (presentation lead) · Visuals: Sara · Narration in Bangla with English subtitles
(or English narration with Bangla UI on screen — decide after rehearsal).
**Rule:** say only what is true on recording day. Replace every "[measured: …]" with a measured
value or delete the line.

## 0:00 – 0:30 · Problem — clarity, relevance
> A rice farmer sees brown spots on a leaf. Is it blast? Brown spot? Is it spreading?
> Today she asks a neighbour or a shopkeeper who sells pesticide. By the time an expert sees it,
> it may be too late — local blast outbreaks have been reported to cut yields by up to 80 percent
> where they strike. And nobody connects one farmer's sick leaf to the next village's.

Visual: field footage / photo of diseased leaf; on-screen source tag for the 80 % figure [S3].

## 0:30 – 1:00 · Solution — simplicity, uniqueness
> Crop Guardian — ফসল রক্ষী. Take a photo. Get the likely disease, how sure the AI is, and what
> to do — in Bangla, with the source of every recommendation. When the AI isn't sure, it says so
> and asks for a better photo instead of guessing. And when several farmers nearby report the same
> disease, the area gets an early warning, clearly marked as unverified.

Visual: three-step animation photo → answer → alert.

## 1:00 – 2:00 · Demo — feasibility, logic
1. Open `/demo-user` (one click) — Bangla UI, synthetic banner visible.
2. Take/upload a leaf photo → waking-server message if cold → result with top-3 + confidence + heat-map.
3. Advice card: steps, dose, safety line, citation "BRRI … p. N". Tap 🔊 voice.
4. Upload a non-leaf photo → "not sure" with retake tips — no disease guessed.
5. Open 🔔 Alerts → a rule-based early warning labelled "unverified".
6. `/demo-admin` → change τ with a reason → flash `/audit` (logged) and `/architecture`.

## 2:00 – 2:30 · AI approach — depth, structure
> We compared five model families — from classical features to CNNs and vision transformers —
> on Bangladeshi field images, chose by a rule fixed in advance, calibrated the confidence so the
> model can abstain, and export it small enough to run on a free server. Advice comes from
> retrieval over DAE and BRRI guides; an answer without a citation is never shown.
> [measured: macro-F1 X (95 % CI a–b) on held-out field images]

## 2:30 – 3:00 · Impact & next step — vision, potential
> Agriculture is nearly half of Bangladesh's jobs [S5]. Our goal is earlier, correct action at
> field level — we will measure loss reduction in a pilot with an extension office, not assume it.
> (Allowed and forbidden impact wording: `docs/evaluation/field-loss-reduction.md` §7.)
> Next: pilot this season, more crops, and the same core for irrigation and yield advice.
> Crop Guardian — from one leaf to every field.

## Production notes
- Total ≤ 180 s; export 1080p; captions burned in.
- No real farmer faces/phones without consent; demo data synthetic.
