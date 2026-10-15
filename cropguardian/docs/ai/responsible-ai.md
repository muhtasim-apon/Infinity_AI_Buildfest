# Responsible AI

Mapped to Congress §15 commitments.

| Commitment (S1 §15) | How Crop Guardian meets it | Evidence |
|---|---|---|
| Lawful, legally sourced data | CC BY 4.0 datasets with attribution; PlantVillage used only after licence check; KB docs with permission notes | `docs/data/datasets.md`, `kb_documents.licence_note` |
| Transparency in AI decisions | top-3 + calibrated confidence, heat-map, model version on every result; citations on every advice | result screen, `/architecture`, model cards |
| Active bias detection & mitigation | per-slice evaluation (source, region, light, blur, phone); confound probe | `docs/ai/statistics.md` §3, §7 |
| No misleading or fabricated demos | synthetic banner; no unmeasured metric shown; demo labelled | prototype, `CLAUDE.md` |
| Privacy-preserving design | EXIF strip, coarse location, no PII to LLM, consent per purpose, deletion | `docs/security/privacy.md` |
| Data-sovereignty awareness | farmer ownership, no data sale, portable to in-country hosting | `docs/data/data-sovereignty.md` |

## Harms we specifically design against
| Harm | Mitigation |
|---|---|
| Wrong diagnosis → wrong chemical, crop loss, money loss | abstain below τ; agronomist review; IPM-first advice |
| Pesticide misuse / poisoning | dose verbatim from source; safety line mandatory; banned list block; PPE reminder |
| Over-trust of the app | "This is decision support; confirm with your agronomist" on every result |
| False outbreak alarm → panic spraying | alerts require agronomist approval; risk level wording reviewed |
| Exclusion of low-literacy / low-end phone users | icons, voice, Bangla, light pages, offline capture |
| Unequal accuracy across regions | slice reporting + targeted data collection in under-represented districts |
| Surveillance concerns | coarse location only; aggregate alerts; no data sale |

## Human oversight
Agronomist in the loop for uncertain diagnoses and every alert. Admin can lower coverage
(raise τ) instantly from `/admin` if a problem appears; every change is audit-logged.

## Incident response
Wrong-advice report → advisory disabled for that disease (admin toggle) → root-cause → KB or
model fix → re-eval → re-enable. Logged in `docs/security/audit-readiness.md` incident register.
