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
public dataset (D1..D3, licence) ─▶ processed split vN ─▶ training run (commit, config)
                                     ─▶ model_versions row (onnx sha256, τ, T, eval report)
                                     ─▶ diagnoses.model_version_id
KB document (url, licence, edition) ─▶ kb_chunks ─▶ citations ─▶ advisories
```
Every diagnosis can be traced to the exact model file and every advice line to a page of a document.
User uploads are never used for training.

## Quality rules
- Near-duplicate and corrupt images removed before every split (pHash, decode check).
- KB document older than its successor edition → retired (chunks deleted, citations keep doc id).
- Datasets re-verified (count + checksum) at each training run.

## Access matrix
| Data | Farmer | Admin | Service (API) |
|---|---|---|---|
| Own scans / diagnoses | R | R | RW |
| Others' scans | — | R | RW |
| Email addresses | own | R (masked in UI) | — (Supabase Auth) |
| KB | R | RW (via API, audited) | R |
| Model registry | R (summary) | RW (via API, audited) | R |
| Alerts | R (published) | R + dismiss (audited) | RW |
| Audit log | — | R | append |

## Deletion
"Delete my data" (settings) → soft-delete flag → n8n job hard-deletes rows and Storage
objects within 7 days; audit row keeps only the action and a hashed user id.
