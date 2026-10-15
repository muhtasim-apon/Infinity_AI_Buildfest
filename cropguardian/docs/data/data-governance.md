# Data governance & lineage

## Roles
| Role | Who | Responsibility |
|---|---|---|
| Data owner | Farmer (their photos and records) | consent, deletion |
| Data steward | Taeen | dataset licences, label taxonomy, datasheets |
| Data custodian | Apon | storage, access control, backups, retention jobs |
| KB steward | Salwa | KB document permissions, edition dates, removal of outdated advice |

## Lineage (what the `/data` page shows)
```
external dataset (D1..D4, licence) ─┐
pilot photo (consent id) ───────────┼─▶ processed split vN ─▶ training run (commit, config)
agronomist label (review id) ───────┘        ─▶ model_versions row (onnx sha256, τ, T, eval)
                                              ─▶ diagnoses.model_version_id
KB document (url, licence, edition) ─▶ kb_chunks ─▶ citations ─▶ advisories
```
Every diagnosis can be traced to the exact model file and every advice line to a page of a document.

## Quality rules
- Label disagreement between two agronomists → `unclear`, excluded from training.
- KB document older than its successor edition → retired (chunks deleted, citations keep doc id).
- Datasets re-verified (count + checksum) at each training run.

## Access matrix
| Data | Farmer | Agronomist | Admin | Service (API) |
|---|---|---|---|---|
| Own scans/diagnoses | R | R (region) | R | RW |
| Others' scans | — | R (region, review) | R | RW |
| Phone numbers | own | — | R (masked) | R (notify only) |
| KB | R | R | RW | R |
| Model registry | R (summary) | R | RW | R |
| Audit log | — | — | R | append |

## Deletion
"Delete my data" (settings) → soft-delete flag → n8n job hard-deletes rows and Storage
objects within 7 days; audit row keeps only the action and a hashed user id.
