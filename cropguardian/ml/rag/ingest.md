# KB ingestion pipeline

1. **Register** the document first: `kb_documents` row with title, publisher, URL, edition date, language,
   and `licence_note` (permission or licence basis). No row → do not ingest.
2. **Extract** — digital PDF: pdfplumber; scanned: Tesseract with `-l ben+eng`. Keep page numbers.
3. **Normalise** — Unicode NFC; fix common Bangla OCR confusions (reviewed list); strip headers/footers.
4. **Chunk** — split on headings; 300–500 tokens; 50 overlap; never split a dosage table row.
5. **Tag** — `meta = {crop, disease (unified code), stage, topic: symptom|prevention|cultural|chemical}`;
   tagging assisted by keyword rules, checked by a human.
6. **Embed** — `intfloat/multilingual-e5-small`, text prefixed `"passage: "`, L2-normalised, 384-d.
   Export the encoder to ONNX once (optimum) so the API embeds queries without PyTorch.
7. **Load** — insert `kb_chunks`; HNSW index exists in schema.
8. **Evaluate** — run the golden set (Recall@8, MRR); record results with the KB version.
9. **Retire** — new edition → set `retired_at` on the old document; chunks excluded by RLS/filters.
