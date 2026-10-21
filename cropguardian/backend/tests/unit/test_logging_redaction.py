import pytest

from app.core.logging import REDACTED, redact


@pytest.mark.security
@pytest.mark.parametrize(
    "key",
    [
        "password",
        "token",
        "otp",
        "session_id",
        "phone",
        "lat",
        "lon",
        "api_key",
        "csrf",
        "Authorization",
        "totp_secret",
        "image",
    ],
)
def test_sensitive_keys_masked(key):
    assert redact({key: "value-123"})[key] == REDACTED


@pytest.mark.security
def test_nested_and_list_values_masked():
    out = redact({"user": {"password": "p", "name": "ok"}, "items": [{"token": "t"}]})
    assert out["user"]["password"] == REDACTED
    assert out["user"]["name"] == "ok"
    assert out["items"][0]["token"] == REDACTED


@pytest.mark.security
def test_secret_looking_values_masked_under_innocent_keys():
    out = redact({"msg": "got Bearer abc.def.ghi and phone 01712345678 and +8801712345678"})
    assert "abc.def.ghi" not in out["msg"]
    assert "01712345678" not in out["msg"]
    assert "+8801712345678" not in out["msg"]


@pytest.mark.security
def test_jwt_value_masked():
    # built at runtime so secret scanners do not flag a JWT-shaped literal in the repo
    jwt = ".".join(["eyJ" + "a" * 20, "b" * 20, "c" * 12])
    assert jwt not in redact({"note": jwt})["note"]


def test_non_sensitive_data_untouched():
    assert redact({"route": "/scans", "count": 3}) == {"route": "/scans", "count": 3}


def test_deep_nesting_is_cut_off_not_crashing():
    deep: dict = {}
    cur = deep
    for _ in range(20):
        cur["a"] = {}
        cur = cur["a"]
    redact(deep)  # must not recurse forever
