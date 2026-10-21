# ml/ — training, evaluation and knowledge pipelines

Training happens **offline** (free Colab / Kaggle GPUs); only exported ONNX files reach the API.
Datasets and weights are never committed (`.gitignore`; data lives in `ml/data/`).

| Folder | Owner | What |
|---|---|---|
| `cg_ml/` | Taeen | **library** (pure, typed, unit-tested): data pipeline today; training, calibration, evaluation, export to come |
| `configs/` | Taeen | `labels.yaml` (taxonomy), `data_manifest.yaml` (sources, licences, published checksums), `data_lock.json` (our verified hashes) |
| `reports/` | Taeen | generated EDA outputs (`reports/eda/`) and, later, evaluation reports — the only source of displayed numbers |
| `tests/` | Taeen | unit tests for every `cg_ml` module |
| `vision/` | Taeen | classifier training notes, ONNX export notes (design stubs) |
| `outbreak/` | Taeen / Apon | rules v1 parameters, LightGBM v2 plan |
| `rag/` | Salwa | KB ingestion pipeline, golden Q&A set |
| `evaluation/` | Taeen | report template, metrics scripts outline |
| `registry/` | Apon | how model files are versioned, stored and promoted |

Design docs: [`../docs/ai/`](../docs/ai/). Dataset notes: [`../docs/data/datasets.md`](../docs/data/datasets.md).
Measured datasheets and findings: [`../docs/datasheets/`](../docs/datasheets/).

## Quick start (Windows shown; use `bin/` on Linux/macOS)
```
python -m venv .venv && .venv/Scripts/pip install -r requirements-dev.txt
python -m cg_ml data download --dataset D1      # resumable; https + host allow-list
python -m cg_ml data verify                     # SHA-256 vs host-published hash and data_lock.json
python -m cg_ml data prepare                    # safe extract, integrity, EXIF, taxonomy, per-image stats
python -m cg_ml data eda                        # figures in ml/reports/eda/
python -m pytest --cov --cov-branch
```

## Status
17 Oct scope done: manifest + checksums, safe download/extract, integrity + normalisation, taxonomy mapping,
per-image statistics and EDA for D1 and D2 (see `docs/datasheets/EDA-findings.md`). Next: pHash groups and
`split_v1.csv` (18 Oct), baselines (19 Oct), first ONNX (20 Oct).
**No model has been trained and no metric exists yet.**
