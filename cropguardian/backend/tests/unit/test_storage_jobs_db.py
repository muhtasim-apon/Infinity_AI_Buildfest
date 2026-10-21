from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from app.core.clock import ensure_utc, utcnow
from app.core.storage import StorageError, bucket_is_private, presign_upload
from app.db.session import DbContext, normalise_async_url, session_scope
from app.jobs.worker import acquire_cron_lock, ping


def test_presign_rejects_bad_type_key_and_size():
    c = MagicMock()
    with pytest.raises(StorageError):
        presign_upload(c, "scans", "a.jpg", "text/html", 1000)
    with pytest.raises(StorageError):
        presign_upload(c, "scans", "../etc/passwd", "image/jpeg", 1000)
    with pytest.raises(StorageError):
        presign_upload(c, "scans", "/abs.jpg", "image/jpeg", 1000)
    with pytest.raises(StorageError):
        presign_upload(c, "scans", "a.jpg", "image/jpeg", 0)
    with pytest.raises(StorageError):
        presign_upload(c, "scans", "a.jpg", "image/jpeg", 10**9)


def test_presign_sets_length_and_type_conditions():
    c = MagicMock()
    presign_upload(c, "scans", "u/1.jpg", "image/png", 5000)
    kwargs = c.generate_presigned_post.call_args.kwargs
    assert ["content-length-range", 1, 5000] in kwargs["Conditions"]
    assert {"Content-Type": "image/png"} in kwargs["Conditions"]


@pytest.mark.security
def test_bucket_private_check_fails_closed():
    c = MagicMock()
    c.get_bucket_acl.return_value = {"Grants": []}
    assert bucket_is_private(c, "scans")
    c.get_bucket_acl.return_value = {
        "Grants": [{"Grantee": {"URI": "http://acs.amazonaws.com/groups/global/AllUsers"}}]
    }
    assert not bucket_is_private(c, "scans")
    c.get_bucket_acl.side_effect = ClientError({"Error": {"Code": "403"}}, "GetBucketAcl")
    assert not bucket_is_private(c, "scans")  # any doubt => not private


def test_clock_rejects_naive_and_normalises():
    from datetime import datetime

    with pytest.raises(ValueError):
        ensure_utc(datetime(2026, 1, 1))
    assert ensure_utc(utcnow()).tzinfo is not None


def test_normalise_async_url():
    assert normalise_async_url("postgres://u:p@h/db").startswith("postgresql+asyncpg://")
    assert normalise_async_url("postgresql://u:p@h/db").startswith("postgresql+asyncpg://")


@pytest.mark.security
async def test_session_scope_rejects_bad_role_and_context():
    with pytest.raises(ValueError):
        async with session_scope(MagicMock(), DbContext(), role="postgres; DROP TABLE x"):
            pass
    with pytest.raises(ValueError):
        async with session_scope(MagicMock(), DbContext(tenant="evil")):
            pass
    with pytest.raises(ValueError):
        async with session_scope(MagicMock(), DbContext(region_csv="a'; --")):
            pass


async def test_ping_job():
    assert await ping({}) == "pong"


async def test_cron_lock_semantics():
    redis = MagicMock()

    async def set_(key, val, nx, ex):
        return True

    redis.set = set_
    assert await acquire_cron_lock(redis, "digest", 60) is True
    with pytest.raises(ValueError):
        await acquire_cron_lock(redis, "digest", 0)
