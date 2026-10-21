# Datasheet D1 — RiceLeafBD

Status: **measured on 2026-10-21** by `python -m cg_ml data verify|prepare|eda` (outputs under `ml/reports/`).
Data is never committed (`ml/data/` is gitignored). Third-party claims are labelled as the source's own.

| Field | Value |
|---|---|
| Name | RiceLeafBD: A Real-Field Image Dataset for Rice Leaf Disease Detection and Classification in Bangladesh |
| Host / page | Mendeley Data — https://data.mendeley.com/datasets/kx9rx8p2mz/1 (DOI 10.17632/kx9rx8p2mz.1) |
| Version / published | v1, 2025-11-07 (host metadata, accessed 2026-10-21) |
| Licence | **CC BY 4.0** (host `data_licence`, accessed 2026-10-21). Attribution required; changes must be indicated |
| Archive | `Original Images.zip`, 497,906,237 bytes; SHA-256 `3280cc176c2ee9f6ee4386e5728623fc7e8f9204b31c50f4ebb303edc52d9c83` (published by host **and** recomputed by us: match; locked in `ml/configs/data_lock.json`) |
| Role in Crop Guardian | train / validation / test (never external test) |

## Collection (the dataset page's own claims — not verified by us)
Smartphone images (Samsung Galaxy S21 Ultra, Redmi Note 9) of the adaxial leaf surface, Sylhet and Dhaka,
Amon season (Aug–Dec), varied weather; labels validated with experts of the Jamalpur Krishi Gobeshona
Institution. Page states 1,555 images in 4 classes plus a CSV of labels/metadata.

## What we measured
| Class folder in archive | Unified class (spec 9.3) | Page claim | Files found | Difference |
|---|---|---|---|---|
| Healthy Leaf | healthy | 252 | 252 | 0 |
| Bacterial Leaf Blight | bacterial_leaf_blight | 417 | 422 | +5 |
| Brown Spot | brown_spot | 356 | 356 | 0 |
| Tungro Virus | tungro | 530 | 530 | 0 |
| **Total** | | 1,555 | **1,560** | +5 |

- Integrity (Pillow verify + full decode, min side 128 px): **1,560 / 1,560 pass**; none corrupt or too small.
- Image sizes (after EXIF transpose): widths 167–2000 px (median 1080), heights 245–2048 px (median 1600);
  most common 1200×1600 (377 files), 1170×1560 (147), 1600×1200 (116).
- **Exact byte-duplicate groups: 98** (207 files; 109 extra copies). **22 groups contain the same bytes under
  different class folders** — label noise by construction. Per spec 9.4.4 these are excluded and listed once
  pHash grouping runs (18 Oct). (`ml/reports/eda/exact_duplicates_summary.json`)
- Per-image brightness and blur statistics: `ml/reports/eda/files_D1.csv`; figures in `ml/reports/eda/*.png`.

## Known issues and limits
1. **Cross-class duplicates** (above) mean naive splitting would leak and mislabel; group-aware splitting is mandatory.
2. **Source confound:** D1 holds Healthy, Bacterial Leaf Blight, Brown Spot and Tungro; only `healthy` and
   `tungro` also exist in D2. Blast, narrow brown spot and sheath blight come only from D2, so a model can learn
   *which dataset* instead of *which disease* (spec 9.3). See `docs/datasheets/EDA-findings.md` for the resolution
   difference between D1 and D2, which makes this worse.
3. Two geographies and one season per source; no claim about other regions or varieties.
4. Labels are the authors' (expert-validated per the page); we did not re-label.

## Attribution (CC BY 4.0)
Dataset authors as listed on the Mendeley page. Cite: *RiceLeafBD*, Mendeley Data, V1, doi:10.17632/kx9rx8p2mz.1.
Changes made by us: EXIF orientation applied, converted to RGB, metadata stripped, re-saved as JPEG (quality 95)
for the processed copy used in training; originals untouched in `ml/data/raw/`.
