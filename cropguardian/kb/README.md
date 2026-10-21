# kb/ — knowledge-base sources (Salwa, Phase 5)

- `sources.yaml` — every document with publisher, edition, licence note, SHA-256 and extraction status; also lists
  known **gaps**. Validated by `backend/app/rag/sources.py` (tests in `backend/tests/unit/test_kb_sources.py`); the
  host list derived from it is the SSRF allow-list for admin ingestion.
- `raw/` — downloaded PDFs (**gitignored**). Re-download from the `url` and compare `sha256`.
- Licence stance: publicly available material, cited with attribution; redistribution permission **not** obtained; the
  app never republishes whole documents (≤ 50-word passage + link).

17 Oct sourcing result (2026-10-21): 15 documents downloaded (BRRI disease factsheets and IPM guide, DAE manual and
pest-list report, Pesticide Rules 1985 ×2), 2 candidates. **Nine of the BRRI PDFs have no text layer and one has a
legacy-font Bangla text layer, so OCR is required** (spec 10.2). No official banned-pesticide list has been found yet
(see `gaps`). Nothing has been expert-reviewed.
