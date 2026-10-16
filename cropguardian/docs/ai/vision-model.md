# Vision model — design, algorithm choice, training, export

Owners: **Taeen** (training, evaluation) · **Apon** (export, serving, integration).
Card: [`model-cards/disease-classifier.md`](model-cards/disease-classifier.md). Statistics: [`statistics.md`](statistics.md).

## 1. Task
Single-label image classification of a rice leaf photo into the 7-class unified taxonomy
([`../data/datasets.md`](../data/datasets.md) §4), plus **abstention** when uncertain.

Why classification first (not detection/segmentation): our datasets have image-level labels
only. Detection (YOLO) needs bounding boxes and segmentation needs masks — neither exists in our
datasets, so both are out of scope for this version.

## 2. Algorithm landscape — what each family offers
| Family | Examples | Strength | Weakness for us |
|---|---|---|---|
| Classical ML on handcrafted features | colour histograms + GLCM texture + SVM / Random Forest | tiny, explainable features | brittle on field backgrounds; low ceiling — **kept as a baseline** |
| CNN, mobile-optimised | MobileNetV3, EfficientNet-Lite | fast on CPU, small | slightly lower accuracy |
| CNN, compound-scaled | EfficientNet / EfficientNetV2 | strong accuracy per FLOP | heavier than MobileNet |
| Modern CNN | ConvNeXt-Tiny | strong texture modelling | ~28 M params → latency risk on free CPU |
| Vision Transformer | ViT-S/16, DeiT-S, Swin-T | global context; best with large pre-training | data-hungry; we have ~4 k images |
| Self-supervised backbones | DINOv2 (ViT-S/14) frozen + linear head | excellent features with few labels | size; licence check |

## 3. Shortlist and selection rule
Train: **(a)** handcrafted+SVM baseline, **(b)** MobileNetV3-Large, **(c)** EfficientNetV2-B0,
**(d)** ConvNeXt-Tiny, **(e)** DeiT-Small. Optional **(f)** DINOv2-S frozen + logistic head.

Selection rule — fixed **before** seeing test data:
1. Filter: int8 ONNX ≤ 30 MB and median CPU latency ≤ 1 s/image on a 1-vCPU benchmark.
2. Rank by **validation macro-F1** (mean over 5 folds).
3. If the top two are within each other's 95 % CI → choose lower ECE, then smaller model.
4. Evaluate the winner **once** on the test split. Report everything, including losers.

## 4. Training recipe
| Item | Setting | Reason |
|---|---|---|
| Init | ImageNet pre-trained (timm) | small dataset |
| Input | 224 × 224, ImageNet normalisation | standard |
| Stage 1 | freeze backbone, train head 5 epochs, lr 1e-3 | stabilise head |
| Stage 2 | unfreeze last blocks, lr 1e-4 → cosine, 25–40 epochs, early stopping on val macro-F1 (patience 7) | fine-tune |
| Optimiser | AdamW, weight decay 0.05 | |
| Loss | cross-entropy, label smoothing 0.1, class weights ∝ 1/√freq | imbalance |
| Augment | RandomResizedCrop(0.6–1), flips, rotation ±25°, ColorJitter, GaussianBlur, RandomShadow, JPEG-quality 40–95 | match phone/field conditions |
| Regularise | Mixup/CutMix (α 0.2) for (d)/(e) | |
| Precision | AMP fp16 | free GPU memory |
| Seeds | 3 seeds for the final candidate | variance estimate |
| Tracking | CSV + config YAML committed; weights in Supabase `models/` bucket, not git | reproducibility |

Compute: free Google Colab / Kaggle notebooks (GPU). Notebook outline: [`../../ml/vision/train.md`](../../ml/vision/train.md).

## 5. Calibration & abstention
Temperature scaling (single scalar T fit on validation NLL) → risk–coverage curve → choose τ.
Plus an **out-of-distribution guard**: images from PlantDoc non-rice classes and random non-leaf
photos form an OOD validation set; reject when max-prob < τ *or* energy score above a threshold.
See ADR 0005.

## 6. Explainability
- **Grad-CAM** heat-maps (pytorch-grad-cam) for the validation/test report and the demo
  gallery; the team checks a sample against the public disease descriptions: does the heat-map sit
  on the lesion or on the background?
  (a "right for the wrong reason" check — catches the dataset-source confound).
- Runtime: top-3 with calibrated probabilities always shown; a heat-map only where computed.

## 7. Export & serving
PyTorch → `torch.onnx.export(opset 17, dynamic batch)` → `onnxruntime.quantization.quantize_dynamic`
(int8) → **parity gate**: top-1 agreement with FP32 ≥ 99 % on validation and macro-F1 drop ≤ 1 pt;
otherwise ship FP32 ONNX. SHA-256 recorded in `model_versions`. Details:
[`../../ml/vision/export_onnx.md`](../../ml/vision/export_onnx.md).

Serving (`services/api/app/ml/inference.py`): session created once at startup;
`intra_op_num_threads=1`; called through a thread pool with a semaphore of 2; 4 s timeout.

## 8. Roadmap
v0 classifier (Oct) → v1 retrained with more public field datasets (Nov)
→ more crops (jute, wheat, potato, vegetables) as data permits → on-device (onnxruntime-web) for
offline diagnosis.
