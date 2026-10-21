# Phase 3 — ML data pipeline, baselines, first ONNX (Taeen)

Skills loaded: cropguardian-safety.

## 17 Oct section (executed 2026-10-21)
Scope: `ml/` skeleton, `cg_ml data download|verify|prepare`, EDA, datasheets, D4 licence check.

Built: manifest with host-published SHA-256 + local lock; resumable allow-listed downloader; zip-slip/symlink/bomb-safe
extraction (zip, rar via 7-Zip); integrity (Pillow verify + decode, ≥ 128 px), EXIF transpose, RGB, metadata strip;
taxonomy mapping that reports unknown folders instead of guessing; per-image brightness/blur/size; five EDA figures.
Run results (D1, D2): all 4,710 images pass integrity; hashes of both archives match the host. See `docs/datasheets/`.
Findings: D2 archive has 3,150 images vs 2,545 stated; D1 has 98 exact-duplicate groups (22 with conflicting labels);
D2 is uniformly 300×300 while D1 is up to ~2000 px (source confound is strong). D4 PlantVillage licence unconfirmed → blocked.
Tests: 49 pass, 94% branch coverage; mypy strict + ruff clean.
Exit check: manifest checksums committed; `ml/reports/eda/` figures exist → **met**.
Next (18 Oct): pHash groups, taxonomy mapping into `split_v1.csv`, stratified-group split, leakage tests.
