# MinIO / bucket policy (spec 16.11)

All buckets are **private**: `scans`, `models`, `exports`, `backups`. No anonymous policy is ever set.
Access is by presigned URLs (`backend/app/core/storage.py`) only; presigned POST limits size and type.
`infra/minio/init.sh` creates the buckets, removes any anonymous policy, and applies lifecycle rules.
`scripts/check_buckets.py` (from Phase 4) asserts anonymous access is denied.

Lifecycle: `scans/` originals expire after `retention.original_days` (default 90) once a thumbnail
exists; `exports/` expire after 7 days; `backups/` after 30 days.
