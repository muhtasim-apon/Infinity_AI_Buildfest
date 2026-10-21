# Datasheet D2 — RiceLeafDisease-BD5

Status: **measured on 2026-10-21** by `python -m cg_ml data verify|prepare|eda` (outputs under `ml/reports/`).
Data is never committed. Third-party claims are labelled as the source's own.

| Field | Value |
|---|---|
| Name | RiceLeafDisease-BD5: A Field-Collected Five-Class Image Dataset from Bangladesh |
| Host / page | Mendeley Data — https://data.mendeley.com/datasets/sjkptpgv79/2 (DOI 10.17632/sjkptpgv79.2) |
| Version / published | **v2**, 2026-07-28 (host metadata, accessed 2026-10-21). The README inside the archive cites DOI `...sjkptpgv79.1` and the title "RiceLeafBD: A Field-Collected Rice Leaf Disease Dataset from Bangladesh" (naming inconsistency inside the source) |
| Licence | **CC BY 4.0** (host `data_licence`; the archive also ships `License .pdf` stating CC BY 4.0). Attribution required |
| Archive | `RiceLeafDisease-BD5.rar`, 21,642,468 bytes; SHA-256 `ea5da4b300af32998d4d2c396f5033b3d82843f5e9629a15bfc1131f744c9d2b` (published by host **and** recomputed by us: match; locked) |
| Role in Crop Guardian | train / validation / test (never external test) |

## Collection (the dataset page / README claims — not verified by us)
Paddy fields in Savar Upazila, Akran, Birulia and Savar Municipal Area (Dhaka District), Oct–Nov 2024,
consumer smartphones; "manually verified by agricultural experts and extension officers"; ambiguous, blurred or
multi-infection samples excluded. The README states **2,545 images, resized to 224 × 224**.

## What we measured — and where it differs from the source's own statement
| Class folder in archive | Unified class | Page claim | Files found | Difference |
|---|---|---|---|---|
| Normal_Leaf | healthy | 923 | 834 | −89 |
| Blast | blast | 339 | 720 | +381 |
| Narrow_Brown_Spot | narrow_brown_spot | 329 | 476 | +147 |
| Sheath_Blight | sheath_blight | 454 | 626 | +172 |
| Tungro | tungro | 500 | 494 | −6 |
| **Total** | | 2,545 | **3,150** | +605 |

- The archive also contains 3 PDFs (README, licence, dataset description) that are not images.
- **The archive holds 605 more images than its page and README state, with a very different class mix.** We
  do not know why (a later version v2 may have added images while the text still describes v1, or some files are
  re-exports). This is unresolved: **do not quote 2,545 as our training count**; use the recomputed numbers.
  Action (Taeen, 18 Oct): after pHash grouping, report how many of the extra images are near-duplicates of others.
- Integrity: **3,150 / 3,150 pass**; every image is exactly **300 × 300 px** (README says 224 × 224).
- Exact byte-duplicate groups: 2 (5 files). 6 files have names like `... - Copy.jpg` / `Copy (N)`, i.e. copies made by
  hand. No exact duplicates span classes.
- File names look like camera timestamps (`IMG_20241103_120527.jpg`); consecutive timestamps imply
  **near-identical frames of the same plant/leaf**, which pHash grouping must keep in one split.

## Known issues and limits
1. **Pre-resized square crops** (300 × 300) versus D1's high-resolution originals (up to ~2000 px): the two sources
   differ in resolution, so resolution alone can identify the source (see `EDA-findings.md`). Any resize-to-224
   preprocessing equalises the pixel grid but not the sharpness/compression history.
2. **Source confound:** Blast, narrow brown spot and sheath blight occur only here.
3. Count discrepancy with the page (above) and the inconsistent DOI/title inside the archive.
4. One region, one season (Oct–Nov 2024); no claim about other regions.

## Attribution (CC BY 4.0)
Dataset authors as listed on the Mendeley page. Cite as the page instructs (Mendeley Data, doi:10.17632/sjkptpgv79.2).
Changes made by us: EXIF orientation applied, converted to RGB, metadata stripped, re-saved as JPEG (quality 95).
