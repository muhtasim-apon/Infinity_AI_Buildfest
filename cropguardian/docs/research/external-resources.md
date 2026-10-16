# External resources — free datasets, knowledge, data services, models, tools

Owner: **Taeen** (datasets) · **Salwa** (knowledge sources) · **Apon** (data services, platforms).
Everything here is free to access. Facts were read on the source page on **2026-10-16**; IDs point to
[`sources.md`](sources.md). **"Verify" means: do not use in the product until the licence or terms are
confirmed and recorded.** Commercial use matters because the PRD has a business model
([`prd.md`](../product/prd.md) §7) — prefer resources that allow it.

---

## 1. Rice / plant-disease image datasets

### 1.1 Primary — field photos from Bangladesh (train + validate + test)
| ID | Dataset | Link | Images | Classes | Where / when | Licence | Our use |
|---|---|---|---|---|---|---|---|
| D1 | RiceLeafBD | https://data.mendeley.com/datasets/kx9rx8p2mz | 1,555 | Healthy 252 · Bacterial Leaf Blight 417 · Brown Spot 356 · Tungro 530 | Sylhet & Dhaka; v1, 7 Nov 2025 | **CC BY 4.0** | core training data |
| D2 | RiceLeafDisease-BD5 | https://data.mendeley.com/datasets/sjkptpgv79 | 2,545 | Blast 339 · Narrow Brown Spot 329 · Sheath Blight 454 · Tungro 500 · Normal 923 | Savar (Dhaka), Oct–Nov 2024; v2, 28 Jul 2026 | **CC BY 4.0** | core training data |
| D5 | Dhan-Shomadhan | https://data.mendeley.com/datasets/znsxdctwtt | 1,106 | Brown Spot · Leaf Scald · Rice Blast · Rice Tungro · Sheath Blight | Bangladeshi local rice; Daffodil International University; v1, 6 Apr 2021; field **and** white-background photos | **CC BY 4.0** | adds Leaf Scald + more Blast/Sheath Blight; white-background subset useful for robustness tests, not for field accuracy |

### 1.2 Secondary — other regions (more data, robustness, out-of-distribution tests)
| ID | Dataset | Link | Images | Classes | Origin | Licence | Our use |
|---|---|---|---|---|---|---|---|
| D7 | Rice Leaf Disease Image Samples (Sethy) | https://data.mendeley.com/datasets/fwcj7stb8r | 5,932 | Bacterial Blight · Blast · Brown Spot · Tungro | Sambalpur University (India); v2, 18 Jul 2024 | **CC BY 4.0** | extra training data for 4 shared classes; test region shift |
| D8 | RiceSeg-5932 (masks for D7) | https://data.mendeley.com/datasets/92jc6w6mcy | 5,932 masks | pixel masks for D7 images | derived from D7 | **verify** | future lesion-area work only |
| D9 | Rice Leaf Disease Dataset (Chaudhari) | https://data.mendeley.com/datasets/z4hx2v3ywc | 242 | "Rice Blast" (other classes not listed) | mobile-camera field photos; v2, 18 Jan 2024 | **CC BY 4.0** | small extra blast sample; check labels first |
| D6 | Paddy Doctor | https://ieee-dataport.org/node/10108 · https://paddydoc.github.io · DOI 10.21227/hz4v-af08 | 16,225 | 13 classes (12 diseases + healthy) | India; smartphone field photos | **verify** — not stated on IEEE DataPort or the project page; the Kaggle subset (10,407 images) follows competition terms | **benchmark only** until the licence is confirmed |
| D3 | PlantDoc | https://github.com/pratikkayal/PlantDoc-Dataset | 2,598 | 13 species, up to 17 classes | in-the-wild web images | **CC BY 4.0** | out-of-distribution ("not rice") tests |
| D4 | PlantVillage | https://github.com/spMohanty/PlantVillage-Dataset | 54,306 | 14 crops, 26 diseases (lab backgrounds) | lab photos | **verify** (not stated on the repo page) | optional pre-training / domain-shift experiment |

### 1.3 How the datasets combine
| Unified class (labels in [`ml/vision/README.md`](../../ml/vision/README.md)) | D1 | D2 | D5 | D7 |
|---|---|---|---|---|
| healthy | Healthy | Normal Leaf | — | — |
| bacterial_leaf_blight | ✓ | — | — | ✓ |
| brown_spot | ✓ | — | ✓ | ✓ |
| narrow_brown_spot | — | ✓ | — | — |
| blast | — | ✓ | ✓ | ✓ |
| sheath_blight | — | ✓ | ✓ | — |
| tungro | ✓ | ✓ | ✓ | ✓ |
| *leaf_scald (new class, optional)* | — | — | ✓ | — |

Rules: deduplicate across all sets with perceptual hashing before splitting; keep the **test split
Bangladeshi field photos only** (D1/D2/D5 field subset); adding D5 + D7 reduces the "class exists in one
source only" confound ([`statistics.md`](../ai/statistics.md) §3); record per-source counts in the
evaluation report. Adding `leaf_scald` changes the model output — decide before 20 Oct.

### 1.4 Not yet available (gaps)
Insect pests (stem borer, brown planthopper, hispa) image sets for Bangladesh; severity labels;
bounding boxes; other crops (jute, wheat, potato). Search Mendeley Data, Kaggle, Zenodo, IEEE DataPort,
Harvard Dataverse with "Bangladesh" + crop + disease, and record new finds here.

## 2. Knowledge sources for advice (RAG)
| Source | Link | Content | Language | Status |
|---|---|---|---|---|
| Bangladesh Rice Research Institute (BRRI) | https://brri.gov.bd | rice disease & pest management guides, variety information | bn / en | **permission to confirm**; record edition dates |
| Department of Agricultural Extension (DAE) | https://dae.gov.bd | extension leaflets, crop-protection guidance, plant clinics | bn | **permission to confirm** |
| Bangladesh Agricultural Research Institute (BARI) | https://bari.gov.bd | non-rice crops (future packs) | bn / en | later |
| IRRI Rice Knowledge Bank | http://www.knowledgebank.irri.org | rice diseases, pests, management practices | en | **verify terms** (site was unreachable on 2026-10-16) |
| FAO — Integrated Pest Management | https://www.fao.org/pest-and-pesticide-management | IPM principles | en | **verify terms** |
| Banned / restricted pesticides — Bangladesh | official government list | needed for validator rule V5 | bn / en | **to source** — until found, all chemical advice stays blocked |

Rule: each document gets a `kb_documents` row with URL, publisher, edition date and licence note
**before** ingestion ([`rag-design.md`](../ai/rag-design.md)).

## 3. Weather & climate (outbreak risk)
| Service | Link | What | Terms (read 2026-10-16) | Use |
|---|---|---|---|---|
| Open-Meteo forecast API | https://open-meteo.com | humidity, rain, temperature forecasts, no key | free API is **non-commercial only**; limits < 10,000 calls/day, 5,000/hour, 600/minute; data CC BY 4.0 | prototype & preliminary; cache 1 h. **Before any commercial use: paid plan or another provider** |
| NASA POWER | https://power.larc.nasa.gov | free meteorological data (300+ parameters) from satellite and models | **verify** API and usage terms | historical weather for outbreak model v2 |

## 4. Geography & maps
| Resource | Link | What | Licence | Use |
|---|---|---|---|---|
| geoBoundaries | https://www.geoboundaries.org | administrative boundaries (country files) | **CC BY 4.0**, most commercial use allowed; requires a visible "geoBoundaries" credit link | district / upazila boundaries — **confirm which admin levels exist for Bangladesh** |
| GADM | https://gadm.org | administrative boundaries | free for academic / non-commercial use only; redistribution and commercial use need permission | **avoid** in the product (use geoBoundaries) |
| OpenStreetMap tiles | https://www.openstreetmap.org | base map for the alerts map | data ODbL; tile servers have a usage policy — **verify** before production traffic | alerts map (Leaflet) with attribution |

## 5. Statistics & context
| Source | Link | Use |
|---|---|---|
| FAOSTAT | https://www.fao.org/faostat | production / yield context |
| Bangladesh Bureau of Statistics | https://bbs.gov.bd | agriculture statistics, Labour Force Survey ([S5]) |
| BRRI annual reports | https://brri.gov.bd | national rice disease/pest observations |
Any number taken from these goes into [`sources.md`](sources.md) first.

## 6. Pre-trained models & libraries (all free / open source)
| Resource | Link | Use | Licence |
|---|---|---|---|
| timm (PyTorch image models) + ImageNet weights | https://github.com/huggingface/pytorch-image-models | backbones: MobileNetV3, EfficientNetV2, ConvNeXt, DeiT | Apache-2.0 library; **check each weight's licence** |
| multilingual-e5-small | https://huggingface.co/intfloat/multilingual-e5-small | Bangla-capable text embeddings for RAG | check model card |
| ONNX Runtime | https://onnxruntime.ai | CPU inference | MIT |
| pytorch-grad-cam | https://github.com/jacobgil/pytorch-grad-cam | heat-maps | MIT (verify) |
| Tesseract OCR (`ben`) | https://github.com/tesseract-ocr/tesseract | Bangla OCR for scanned guides | Apache-2.0 |
| Noto Sans Bengali / Hind Siliguri | https://fonts.google.com | Bangla UI fonts | SIL Open Font Licence |
| Leaflet | https://leafletjs.com | alerts map | BSD-2 |

## 7. Compute & platforms (free tiers)
Google Colab · Kaggle Notebooks (training GPUs) · Render (hosting) · Supabase (DB, storage, auth) ·
Cloudflare Turnstile (CAPTCHA) · n8n · UptimeRobot · GitHub. Setup and limits:
[`docs/deployment/README.md`](../deployment/README.md) and [`04-free-tier-challenges.md`](../deployment/04-free-tier-challenges.md).

## 8. Evidence base for impact (papers and reports)
| ID | Reference | Link | What it gives us |
|---|---|---|---|
| S6 | Savary et al. (2019), *Nature Ecology & Evolution* 3, 430–439 | https://doi.org/10.1038/s41559-018-0793-y | global rice yield loss to pests & pathogens 30.0 % (24.6–40.9 %), expert survey |
| S7 | FAO (2021), scientific review on climate change and plant pests (news release) | https://sfcs.fao.org/newsroom/detail/Climate-change-fans-spread-of-pests-and-threatens-plants-and-crops-new-FAO-study/en | up to 40 % of global crop production lost to pests each year |
| S8 | Fabregas, Kremer & Schilbach (2019), *Science* 366, eaay3038 | https://doi.org/10.1126/science.aay3038 | digital agricultural information: +4 % yields, +22 % odds of adopting recommended inputs |
| S9 | Beach et al. (2025), *Global Food Security* 45, 100866 | https://doi.org/10.1016/j.gfs.2025.100866 | 20 studies: yield +6 % (95 % CI +2 to +9 %), income +6 % |
| S10 | Rajendran & Islam (2017), CABI Case Study 19 — plant clinics in Bangladesh | https://www.gov.uk/dfid-research-outputs/plant-clinics-in-bangladesh-are-farmers-losing-less-and-feeding-more | observational: regular clinic users reported higher yields/profits (not causal) |
| S11 | Mrisho et al. (2020) — PlantVillage Nuru diagnosis accuracy vs extension agents and farmers (peer-reviewed; **add full reference and DOI before citing in slides**) | search "Mrisho 2020 Nuru cassava accuracy" | diagnosis accuracy 74–88 % with six leaves per plant |
| S2–S5 | Bangladesh context | [`sources.md`](sources.md) | outbreak losses, missing national figure, employment share |
How we use them: [`docs/evaluation/field-loss-reduction.md`](../evaluation/field-loss-reduction.md).

## 9. Licence check & attribution
1. Open the dataset/resource page; record licence, version, DOI, date in [`sources.md`](sources.md) and
   in [`datasets.md`](../data/datasets.md).
2. CC BY 4.0 → allowed (including commercial) **with attribution**. Non-commercial / competition-only /
   unstated → research benchmarking only, never in the shipped model or app.
3. Attribution text shown on `/data` and in the README, e.g.:
   *"Training data includes RiceLeafBD (CC BY 4.0), RiceLeafDisease-BD5 (CC BY 4.0), Dhan-Shomadhan
   (CC BY 4.0) and Rice Leaf Disease Image Samples by Sethy et al. (CC BY 4.0). Boundaries ©
   geoBoundaries (CC BY 4.0). Map data © OpenStreetMap contributors."*
4. Re-check licences before each model release (they can change between dataset versions).
