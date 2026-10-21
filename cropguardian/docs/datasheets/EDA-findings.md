# EDA findings (17 Oct task, run 2026-10-21)

Everything here is recomputed by `python -m cg_ml data prepare && python -m cg_ml data eda` from the verified
archives. Raw outputs: `ml/reports/eda/` (`files_D*.csv`, `summary_D*.json`, `exact_duplicates_summary.json`,
and five PNG figures). Nothing below is a model result; no model has been trained.

## Unified class counts (usable images; 1,560 from D1 + 3,150 from D2 = 4,710)
| Class | D1 | D2 | Total | Sources |
|---|---|---|---|---|
| healthy | 252 | 834 | 1,086 | both |
| bacterial_leaf_blight | 422 | – | 422 | D1 only |
| brown_spot | 356 | – | 356 | D1 only |
| tungro | 530 | 494 | 1,024 | both |
| blast | – | 720 | 720 | D2 only |
| narrow_brown_spot | – | 476 | 476 | D2 only |
| sheath_blight | – | 626 | 626 | D2 only |

Figure: `ml/reports/eda/class_counts_by_source.png`.

## Finding 1 — the structural confound is real and larger than the spec's note
Five of seven classes come from exactly one source (spec 9.3 anticipated this). In addition:
- **D2 is uniformly 300 × 300 px** (3,150 of 3,150). **D1 spans 167–2000 × 245–2048 px.** (`image_sizes.png`.)
  A classifier, or even a one-line rule, can recover the source from the original image size.
- Consequences to carry forward: (a) resize to a common grid *before* statistics comparisons; (b) include source
  probing and per-source recall for `healthy` and `tungro` in every evaluation (spec 9.6); (c) the model card and
  Trust Centre must state that disease and source are entangled; (d) LOSO on the two shared classes is the only
  cross-source check available.

## Finding 2 — duplicates and label noise
- D1: 98 exact-duplicate groups (207 files, 109 redundant copies); **22 groups carry different labels for the same
  bytes**. D2: 2 groups (5 files); 6 hand-made "Copy" files.
- Spec 9.4.4: cross-class duplicate groups are excluded as label noise; near-duplicates (pHash, Hamming ≤ 6) are
  grouped within and across datasets — scheduled for 18 Oct. Exact duplicates are a lower bound on the problem.

## Finding 3 — count discrepancy in D2
The archive contains 3,150 images while the dataset page and README state 2,545 (differences per class in
`D2-RiceLeafDisease-BD5.md`). Unexplained; we use recomputed counts and will measure how many extras are
near-duplicates (18 Oct).

## Finding 4 — brightness and blur differ by source
See `brightness_by_source.png`, `blur_by_source.png`, `brightness_per_class_source.png`. These are descriptive
only; the per-file values are in `files_D*.csv`. We make no claim yet about how much they influence a model.

## What is NOT done yet (next days)
pHash grouping + `split_v1.csv` (18 Oct), baselines (19 Oct), first ONNX (20 Oct). D3/N1 downloads (≈23 Oct).
