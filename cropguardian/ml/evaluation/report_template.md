# Evaluation report — <model> <semver>

| | |
|---|---|
| Date | |
| Commit | |
| Data split | split_v1 (sha256 of split file: ) |
| Config | ml/vision/configs/… |
| Seeds | |

## 1. Headline (test set, evaluated once)
| Metric | Value | 95 % CI |
|---|---|---|
| Macro-F1 | | |
| Balanced accuracy | | |
| Top-3 accuracy | | |
| ECE (before → after T) | | |
| τ / coverage @ τ / selective accuracy @ τ | | |
| OOD AUROC | | |

## 2. Per-class
| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|

## 3. Confusion matrix (normalised) — image
## 4. Reliability diagram & risk–coverage curve — images
## 5. Model comparison (validation, 5-fold mean ± std) + McNemar p-value top-2
## 6. Slices (source, region, brightness, blur)
## 7. Robustness (blur, brightness, rotation, JPEG, crop) — agreement %
## 8. Confound probe (source-prediction accuracy)
## 9. int8 parity & latency (median / p95)
## 10. Known limitations & decisions
