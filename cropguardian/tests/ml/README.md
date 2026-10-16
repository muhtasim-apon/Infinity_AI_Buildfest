# ML tests

Owner: Taeen. Run per model release against the held-out split; values come from the evaluation
report, never recomputed on training data. Targets: [`docs/ai/eval-plan.md`](../../docs/ai/eval-plan.md).

## Release gates
| ID | Gate | Threshold |
|---|---|---|
| ML1 | test macro-F1 (report with 95 % CI) | ≥ 0.85 |
| ML2 | recall of each notifiable disease (blast, bacterial leaf blight, tungro) | ≥ 0.85 |
| ML3 | ECE after temperature scaling | ≤ 0.05 |
| ML4 | int8 vs FP32 top-1 agreement (validation) | ≥ 0.99 |
| ML5 | CPU latency p95, 1 thread | ≤ 1,000 ms |
| ML6 | slice recall floor (source, region, brightness, blur) | ≥ overall − 0.10, else listed in model card |
| ML7 | OOD AUROC | ≥ 0.90 |

## Robustness (agreement with clean prediction ≥ 0.90)
Gaussian blur σ = 2 · brightness −30 % / +30 % · rotation 30° · JPEG quality 40 · centre crop 80 %.

## Preprocessing parity
Same bytes twice → identical tensors · shape (1,3,224,224) float32 · max abs diff vs training eval
transform < 1e-5 on 20 fixtures · EXIF-rotated fixture equals the physically rotated image.
