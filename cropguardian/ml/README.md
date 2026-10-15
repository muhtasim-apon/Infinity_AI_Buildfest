# ml/ — training, evaluation and knowledge pipelines

Training happens **offline** (free Colab / Kaggle GPUs); only exported ONNX files reach the API.
Nothing here has been run.

| Folder | Owner | What |
|---|---|---|
| `vision/` | Taeen | classifier training configs, notebook outline, ONNX export |
| `outbreak/` | Taeen / Apon | rules v1 parameters, LightGBM v2 plan |
| `rag/` | Salwa | KB ingestion pipeline, golden Q&A set |
| `evaluation/` | Taeen | report template, metrics scripts outline |
| `registry/` | Apon | how model files are versioned, stored and promoted |

Design docs: [`../docs/ai/`](../docs/ai/). Datasets: [`../docs/data/datasets.md`](../docs/data/datasets.md).
Datasets and weights are never committed (`.gitignore`).
