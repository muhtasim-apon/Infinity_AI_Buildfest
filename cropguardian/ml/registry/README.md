# Model registry

Source of truth: the `model_versions` table (db/SCHEMA-SPEC.md). Files: Supabase Storage bucket `models/`
(private), path `models/<name>/<semver>/classifier.int8.onnx`.

## Lifecycle
`trained` → report written → card updated → uploaded + row inserted (`is_active=false`) → admin activates
from `/admin` (audited) → API downloads and loads it on next boot (restart from the Render dashboard) → previous version kept
for one-click rollback.

## Rules
- A version without an evaluation report cannot be activated.
- `onnx_sha256` is verified at load; mismatch → API not ready.
- Never delete a version that produced diagnoses (lineage).
