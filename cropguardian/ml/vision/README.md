# ml/vision — classifier training specification

Owner: **Taeen** (training), **Apon** (export & serving). Method: [`docs/ai/vision-model.md`](../../docs/ai/vision-model.md).
Notebook outline: [`train.md`](train.md) · export: [`export_onnx.md`](export_onnx.md).
Files to create while working: `configs/labels.yaml`, `configs/train_base.yaml`, `configs/split_v1.csv`
(file names + split + group id only — never images).

## 1. Label taxonomy (output order = model output index = `disease_catalog` id − 1)
| # | Code | D1 RiceLeafBD | D2 RiceLeafDisease-BD5 | Notifiable |
|---|---|---|---|---|
| 0 | healthy | Healthy | Normal Leaf | — |
| 1 | bacterial_leaf_blight | Bacterial Leaf Blight | — | yes |
| 2 | brown_spot | Brown Spot | — | — |
| 3 | narrow_brown_spot | — | Narrow Brown Spot | — |
| 4 | blast | — | Blast | yes |
| 5 | sheath_blight | — | Sheath Blight | — |
| 6 | tungro | Tungro | Tungro | yes |

## 2. Training configuration (values to put in `train_base.yaml`)
| Group | Setting |
|---|---|
| Seeds | 13, 42, 2026 |
| Data | split file `split_v1.csv`; image 224; resize short side 256; ImageNet mean/std; class-balanced sampler |
| Augment | random resized crop 0.6–1.0 · h-flip 0.5 · v-flip 0.2 · rotation ±25° · colour jitter (brightness 0.3, contrast 0.3, saturation 0.2, hue 0.02) · Gaussian blur p 0.2 σ 0.1–2 · random shadow p 0.2 · JPEG quality 40–95 |
| Stage 1 | backbone frozen, 5 epochs, lr 1e-3 |
| Stage 2 | last blocks unfrozen, up to 40 epochs, lr 1e-4 cosine, 2 warm-up epochs |
| Optimiser | AdamW, weight decay 0.05, label smoothing 0.1, class weights 1/√freq, batch 32, mixed precision |
| Stopping | early stopping on validation macro-F1, patience 7; 5-fold CV for model selection |
| Candidates | classical colour+texture SVM baseline · mobilenetv3_large_100 · tf_efficientnetv2_b0 · convnext_tiny · deit_small_patch16_224 |
| Selection rule (fixed before test) | int8 ONNX ≤ 30 MB · median CPU latency ≤ 1,000 ms · rank by mean validation macro-F1 · tie-break ECE, then size |

## 3. Output of this folder
An evaluation report (template: [`../evaluation/report_template.md`](../evaluation/report_template.md)),
an int8 ONNX file uploaded to the private Supabase `models` bucket, and a `model_versions` row.
Model improvement uses **public datasets only** (no user-photo labelling in this version).
