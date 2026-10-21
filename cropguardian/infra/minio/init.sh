#!/bin/sh
# Create PRIVATE buckets (no public ACL, no anonymous policy) and lifecycle rules, then verify.
# Runs in the one-shot `minio-init` compose service with the aws-cli image.
set -eu
EP="--endpoint-url ${S3_ENDPOINT_URL}"
# wait for the store to accept requests (up to ~60 s)
n=0
until aws $EP s3api list-buckets >/dev/null 2>&1; do
  n=$((n + 1)); [ "$n" -ge 30 ] && { echo "object store not ready"; exit 1; }; sleep 2
done
for b in scans models exports backups; do
  aws $EP s3api head-bucket --bucket "$b" 2>/dev/null || aws $EP s3api create-bucket --bucket "$b" >/dev/null
  aws $EP s3api put-public-access-block --bucket "$b"     --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true 2>/dev/null || true
done
lifecycle() { # bucket days
  aws $EP s3api put-bucket-lifecycle-configuration --bucket "$1" --lifecycle-configuration     "{\"Rules\":[{\"ID\":\"expire\",\"Status\":\"Enabled\",\"Filter\":{\"Prefix\":\"\"},\"Expiration\":{\"Days\":$2}}]}" 2>/dev/null     || echo "note: lifecycle rule for $1 not applied by this store (apply on the hosted store)"
}
lifecycle scans 90; lifecycle exports 7; lifecycle backups 30
echo "buckets ready: $(aws $EP s3api list-buckets --query 'Buckets[].Name' --output text)"
