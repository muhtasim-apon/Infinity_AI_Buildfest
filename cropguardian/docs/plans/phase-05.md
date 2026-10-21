# Phase 5 — Knowledge base & retrieval (Salwa)

Skills loaded: cropguardian-safety; Claude-provided pdf skill (the repo copy is proprietary and not committed).

## 17 Oct section (executed 2026-10-21)
Scope: `kb/sources.yaml` + licences; start downloading PDFs into `kb/raw` (gitignored).

Built: `kb/sources.yaml` (15 downloaded documents with real SHA-256, sizes, page counts, extraction status; 2 candidates; 4 declared
gaps); `backend/app/rag/sources.py` validator + exact-host SSRF allow-list; 41 tests.
Findings: BRRI Knowledge Bank has nine disease factsheets and a 30-page five-disease guide; **none has usable text** (nine have no
text layer, Kholpora has a legacy-font layer) → OCR is the critical path for Phase 5. DAE publishes an extension manual (English) and a
pest-list report. IRRI's rice-diseases site is reachable; the IRRI Knowledge Bank host did not respond. **No official
banned-pesticide list found** (1985 Rules contain none; secondary sources disagree) → lead: `ppw.krishi.gov.bd` cancelled list export.
All licences recorded as "not stated / redistribution not obtained". Nothing is expert-reviewed.
Exit check: every document has publisher/edition/licence note → **met** (some fields marked UNVERIFIED).
Next (18 Oct): OCR path (Tesseract `ben`), extraction + chunking CLI, legacy-font detection tests.
