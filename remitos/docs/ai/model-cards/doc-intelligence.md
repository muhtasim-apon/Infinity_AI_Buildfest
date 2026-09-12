# Model Card — Document Intelligence (NID / Passport OCR)

**Status:** Specification (not trained) · **Risk tier:** High
**Pack:** core (shared across packs) · **Code:** `ml/models/doc_intelligence/`

---

## Intended use

Extract structured fields from identity documents during KYC — National ID (both Bangla
and English faces), passport MRZ, and utility bills for address verification — so that a
user does not have to type them, and so an officer reviews rather than transcribes.

Extraction **proposes**; verification confirms. A low-confidence field is surfaced for
human correction, never silently accepted.

## Out-of-scope use

- **Not authentication.** Extraction does not establish that the document is genuine or
  that the bearer is its subject — that is liveness plus verification against the issuing
  authority.
- Not used for demographic inference of any kind.
- Face data is used for liveness matching only, is never used for identification against
  a database, and never leaves the residency boundary (ADR 0011).

## Training data

Annotated identity documents across capture conditions that reflect reality rather than a
lab: low-end phone cameras, poor light, glare, creases, partial occlusion, and physically
worn cards. **A model trained on clean scans fails precisely for the users who most need
it to work** — a laminated NID carried in a wallet for eleven years is the normal case,
not the edge case.

All training data is consented and lawfully sourced (Congress §20.6). No scraped identity
documents, under any circumstances.

## Evaluation

| Metric | Target |
|---|---|
| Field-level exact match (clean capture) | ≥ 0.99 |
| Field-level exact match (degraded capture) | ≥ 0.97 |
| NID number character error rate | ≤ 0.002 |
| Confidence calibration | ECE ≤ 0.05 |

Stratified by capture quality, document age, **Bangla vs English document face**, and
device tier. The Bangla-face stratum is reported separately and gated separately — a
model that reads the English face well and the Bangla face poorly has failed the local
document, which is the document most users hold.

| Fairness gate | Threshold |
|---|---|
| Accuracy ratio, lowest device tier vs highest | ≥ 0.95 |
| Accuracy ratio, Bangla face vs English face | ≥ 0.97 |

## Known limitations

1. Bengali conjunct characters and older printing are genuinely hard; error rates on
   names are higher than on numerals.
2. Name transliteration between Bangla and English is **not deterministic** — the same
   name legitimately romanises several ways. Downstream matching must use fuzzy and
   phonetic comparison, never exact string equality. This is a frequent source of unfair
   screening failures.
3. Damaged or heavily worn documents may be unreadable; the path must degrade to
   assisted or in-person capture, not to rejection.
4. Not forgery detection.

## Ethical considerations

An extraction failure means a person cannot onboard — exclusion by OCR. Mitigations:

- Human-assisted correction is always available and is one tap away
- An **agent-assisted mode** lets a trained agent complete capture for a user who cannot
- Failure messaging in Bangla explains what to try (better light, flatten the card),
  never "invalid document"
- Repeated failure routes to a human, never to a dead end

## Maintenance

Retrain on new document formats; monitor per-stratum accuracy in production; any stratum
falling below gate triggers rollback.
