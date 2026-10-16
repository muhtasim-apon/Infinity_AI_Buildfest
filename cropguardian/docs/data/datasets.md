# Datasets — collection, licences, splits

Owner: **Taeen**. Every figure below is from the dataset page — see [`../research/sources.md`](../research/sources.md).
Datasets are **downloaded, never committed** (`.gitignore` → `data/raw/`).

## 1. Primary (field images, Bangladesh, rice)
| ID | Name & link | Images | Classes | Licence | Role |
|---|---|---|---|---|---|
| D1 | [RiceLeafBD](https://data.mendeley.com/datasets/kx9rx8p2mz) | 1,555 | Healthy · Bacterial Leaf Blight · Brown Spot · Tungro | CC BY 4.0 | train/val/test |
| D2 | [RiceLeafDisease-BD5](https://data.mendeley.com/datasets/sjkptpgv79) | 2,545 | Blast · Narrow Brown Spot · Sheath Blight · Tungro · Normal | CC BY 4.0 | train/val/test |

## 2. Secondary (pre-training / robustness)
| ID | Name & link | Images | Licence | Role |
|---|---|---|---|---|
| D3 | [PlantDoc](https://github.com/pratikkayal/PlantDoc-Dataset) | 2,598 in-the-wild | CC BY 4.0 | out-of-distribution tests ("not rice" / unseen classes); robustness |
| D4 | [PlantVillage](https://github.com/spMohanty/PlantVillage-Dataset) | 54,306 lab images | **unconfirmed — check before use** | optional pre-training; lab→field domain-shift experiment |
| D5 | [Dhan-Shomadhan](https://data.mendeley.com/datasets/znsxdctwtt) | 1,106 (Bangladesh; field + white background) | CC BY 4.0 | extra Bangladeshi training data; adds Leaf Scald |
| D7 | [Rice Leaf Disease Image Samples (Sethy)](https://data.mendeley.com/datasets/fwcj7stb8r) | 5,932 (India) | CC BY 4.0 | extra data for 4 shared classes; region-shift test |
| D6 | [Paddy Doctor](https://ieee-dataport.org/node/10108) | 16,225 (India, 13 classes) | **not stated** | benchmark only until the licence is confirmed |

Full catalogue of free datasets and other external resources (with licence status and merge plan):
[`../research/external-resources.md`](../research/external-resources.md).

## 3. Our own test photos
- A small **local held-out test set** photographed by the team in nearby rice fields (no people in
  frame, location coarsened), labelled by the team against public BRRI disease descriptions and used
  **only for testing**, never for training. User uploads are never used for training in this version.

## 4. Unified label taxonomy
D1 and D2 overlap (Tungro; Healthy = Normal). Mapping, stored in `ml/vision/configs/labels.yaml`:

| Unified code | D1 | D2 | Bangla name |
|---|---|---|---|
| `healthy` | Healthy | Normal Leaf | সুস্থ পাতা |
| `bacterial_leaf_blight` | Bacterial Leaf Blight | — | ব্যাকটেরিয়াজনিত পাতা পোড়া |
| `brown_spot` | Brown Spot | — | বাদামী দাগ |
| `narrow_brown_spot` | — | Narrow Brown Spot | সরু বাদামী দাগ |
| `blast` | — | Blast | ব্লাস্ট |
| `sheath_blight` | — | Sheath Blight | খোল পোড়া |
| `tungro` | Tungro | Tungro | টুংরো |

Bangla names to be checked against BRRI's published Bangla terminology before UI release.
Note: classes present in only one dataset carry a **source confound** (the model could learn
"photo style of D1" instead of the disease). Mitigation in [`../ai/statistics.md`](../ai/statistics.md) §3.

## 5. Preparation pipeline
1. Download → checksum → `data/raw/<id>/`.
2. Integrity: decode every file, drop corrupt; record counts per class (compare to page).
3. **Near-duplicate removal** with perceptual hashing (pHash, Hamming ≤ 6) — across datasets too.
4. Map labels to unified taxonomy.
5. Split **70 / 15 / 15** stratified by class *and* source dataset; duplicates/grouped shots kept
   in the same split. Seeded; split file committed (`ml/vision/configs/split_v1.csv` — names only).
6. Resize to 256 short side; store processed set outside git.
7. Datasheet ("datasheet for datasets") updated: provenance, licence, known biases, collection
   period (D2: Oct–Nov 2024, Savar — a single season/location).

## 6. Known biases & gaps
- Geography: D1 Sylhet & Dhaka; D2 Savar only → other regions untested.
- Season: D2 one season. Phone/camera models not documented.
- Class imbalance (e.g. D2 Normal 923 vs Narrow Brown Spot 329) → weighted loss + macro metrics.
- No pest (insect) classes yet; no severity labels; no bounding boxes.

## 7. Collection plan for our own data
- Partner: one upazila agriculture office / university agronomy department (to secure, Gantt 16–20 Oct).
- Protocol: 3 photos per leaf (close, medium, plant), daylight, plain hand behind leaf optional.
- Consent form in Bangla; no faces; location coarsened at capture.
