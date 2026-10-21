"""S3 storage (MinIO in compose, Supabase S3 endpoint hosted). Private buckets only (16.11).

Presigned POST carries a content-length-range and exact content-type conditions so the storage
service, not our API, rejects oversize or mistyped uploads.
"""

from __future__ import annotations

from typing import Any

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import Settings

ALLOWED_IMAGE_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
PRESIGN_TTL_SECONDS = 300


class StorageError(Exception):
    pass


def make_s3_client(settings: Settings) -> Any:
    if not settings.s3_endpoint_url:
        raise StorageError("S3 endpoint not configured")
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(
            signature_version="s3v4",
            connect_timeout=3,
            read_timeout=10,
            retries={"max_attempts": 2},
            s3={"addressing_style": "path"},
        ),
    )


def presign_upload(
    client: Any, bucket: str, key: str, content_type: str, max_bytes: int
) -> dict[str, Any]:
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise StorageError("content type not allowed")
    if not (0 < max_bytes <= 20 * 1024 * 1024):
        raise StorageError("invalid size limit")
    if ".." in key or key.startswith("/"):
        raise StorageError("invalid key")
    post: dict[str, Any] = client.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=[
            {"Content-Type": content_type},
            ["content-length-range", 1, max_bytes],
        ],
        ExpiresIn=PRESIGN_TTL_SECONDS,
    )
    return post


def presign_get(client: Any, bucket: str, key: str, ttl: int = PRESIGN_TTL_SECONDS) -> str:
    return str(
        client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=min(ttl, 900)
        )
    )


def bucket_is_private(client: Any, bucket: str) -> bool:
    """True only if the bucket exists and has no public ACL grant. Any doubt returns False."""
    try:
        acl = client.get_bucket_acl(Bucket=bucket)
    except ClientError:
        return False
    public_uris = ("AllUsers", "AuthenticatedUsers")
    return not any(
        any(u in grant.get("Grantee", {}).get("URI", "") for u in public_uris)
        for grant in acl.get("Grants", [])
    )
