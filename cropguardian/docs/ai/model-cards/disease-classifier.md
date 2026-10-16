# Model card — Crop disease classifier (rice)

**Status:** Specification (not trained) · **Risk tier:** High · **Code:** `ml/vision/`, served by `services/api/app/ml/inference.py`

## Intended use
Classify a phone photo of a single rice leaf into one of 7 classes (healthy, bacterial leaf
blight, brown spot, narrow brown spot, blast, sheath blight, tungro) **as decision support**,
abstaining when uncertain. Users: farmers and extension officers in Bangladesh.

## Out of scope
Other crops; whole-field or drone images; insect pests; severity estimation; nutrient deficiency;
any use as the sole basis for chemical application without reading the cited advice.

## Training data
D1 RiceLeafBD (1,555) + D2 RiceLeafDisease-BD5 (2,545), CC BY 4.0, field images from Sylhet,
Dhaka and Savar. Optional pre-training on PlantVillage (licence pending). Unified taxonomy and
splits: `docs/data/datasets.md`.

## Method
Architecture chosen by the rule in `docs/ai/vision-model.md` §3 from MobileNetV3-L,
EfficientNetV2-B0, ConvNeXt-T, DeiT-S (+ classical baseline). Temperature scaling; threshold τ
from risk–coverage; int8 ONNX.

## Evaluation
| Metric | Target | Measured |
|---|---|---|
| Macro-F1 (test, 95 % CI) | ≥ 0.85 | — |
| Notifiable-disease recall | ≥ 0.85 each | — |
| ECE | ≤ 0.05 | — |
| Selective accuracy / coverage @ τ | ≥ 0.95 / report | — |
| OOD AUROC | ≥ 0.90 | — |

Reference (not ours): the D1 authors report 91.5 % accuracy with EfficientNet-V2 on their own
split [P1]; different split, classes and metric — not comparable to our numbers.

## Per-group results
To fill: by source dataset, region, brightness, blur, phone model.

## Known limitations
- Classes from a single source may be confounded with photo style (`statistics.md` §3).
- Two collection regions + one season for D2; unknown generalisation elsewhere.
- Multiple simultaneous diseases → single label only.
- Brown spot vs narrow brown spot visually similar → expected confusion.

## Ethical considerations
Wrong output can cause economic loss or pesticide misuse → "not sure" answers, citations, local office card,
"decision support" disclaimer.

## Versioning
`model_versions` row per release: semver, architecture, ONNX sha256, τ, T, eval summary (with split
id and commit). One active version; rollback = flip `is_active`.
