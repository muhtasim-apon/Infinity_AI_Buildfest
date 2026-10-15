# Statistics & evaluation methodology

Owner: **Taeen**. Nothing here is a result. Results go in `ml/evaluation/reports/` with the
commit hash and split id, then into the model card.

## 1. Exploratory data analysis (EDA)
- Class counts per dataset and combined (bar chart); imbalance ratio max/min.
- Image size, aspect ratio, brightness, blur (variance of Laplacian) distributions per class
  **and per source** — if a class's photos are systematically brighter, the model can cheat.
- Near-duplicate clusters (pHash) — size and cross-class duplicates (label noise).
- Sample grid per class for agronomist sanity check.

## 2. Splitting
- 70/15/15 stratified by (class, source). Groups of near-duplicates stay in one split.
- **5-fold stratified-group CV** on train+val for model selection; test touched once.
- Seeds fixed and recorded.

## 3. Confound control (critical)
Some classes exist in only one dataset (e.g. Blast only in D2, Brown Spot only in D1).
A model may learn *which dataset* a photo came from. Tests:
1. **Source-prediction probe**: train a classifier to predict source dataset from the frozen
   embeddings. High accuracy → confound risk is real.
2. **Shared-class check**: on Tungro and Healthy (present in both), compare per-source recall;
   large gaps → model relies on source style.
3. Grad-CAM review on 50 random test images per class.
4. Mitigation: heavier colour/background augmentation, background-crop augmentation, and —
   most important — our own field photos across classes.

## 4. Metrics
| Metric | Why |
|---|---|
| **Macro-F1** (primary) | treats rare diseases equally |
| Per-class precision, recall, F1 | a missed blast case is worse than a missed healthy |
| Balanced accuracy | robust to imbalance |
| Confusion matrix (normalised) | which diseases are confused (e.g. brown spot vs narrow brown spot) |
| Top-3 accuracy | the UI shows top-3 |
| **ECE** (15 bins) + reliability diagram | is confidence trustworthy? before/after temperature scaling |
| Risk–coverage curve, AURC | quality of abstention |
| Selective accuracy @ τ and coverage @ τ | what the farmer actually experiences |
| OOD AUROC (in-dist vs OOD set) | can we reject non-rice / non-leaf images |
| Latency p50/p95 (CPU, int8) | deployability |

## 5. Uncertainty & significance
- **Bootstrap 95 % CI** (1,000 resamples of the test set) for macro-F1 and per-class recall.
- **McNemar's test** (paired, on test predictions) between the top two models; α = 0.05.
- Mean ± std over 3 seeds for the chosen architecture.
- Report CIs in every table; never a bare point estimate.

## 6. Domain-shift experiment (honest reporting)
Train on PlantVillage (lab background) only → test on D1/D2 field images. Expect a large drop.
Purpose: demonstrate *why* field data matters and justify our data-collection plan. Run only
if D4's licence is confirmed.

## 7. Per-group (fairness/robustness) slices
Source dataset · region (Sylhet / Dhaka / Savar, later our districts) · brightness tercile ·
blur tercile · phone model (our data). **Gate:** no slice's recall for a notifiable disease
below the overall value minus 10 points without being reported as a known limitation.

## 8. Robustness tests (also in `tests/ml/`)
Prediction stability under: Gaussian blur σ ≤ 2, brightness ±30 %, rotation ±30°, JPEG q=40,
centre crop 80 %. Metric: top-1 agreement with the clean prediction.

## 9. Outbreak model statistics (later stage)
Spatio-temporal clustering evaluated against agronomist-confirmed outbreaks: precision of
alerts, lead time distribution (median, IQR), false-alert rate per 1,000 km² per month.

## 10. Reporting template
`ml/evaluation/report_template.md`: data version, commit, config, per-class table with CIs,
confusion matrix, reliability diagram, risk–coverage, slices, robustness, latency, known limits.
