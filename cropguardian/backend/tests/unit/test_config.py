import pytest
from pydantic import ValidationError

from app.core.config import ConfigError, Settings

GOOD = {
    "cg_env": "production",
    "secret_key": "x" * 40,
    "app_base_url": "https://app.example.org",
    "database_url": "postgresql://u:p@h:6543/db",
    "trusted_hosts": ["api.example.org"],
    "redis_url": "redis://:pw@redis.internal:6379/0",
    "sms_provider": "disabled",
    "email_provider": "disabled",
}


def make(**over):
    return Settings(_env_file=None, **{**GOOD, **over})


def test_defaults_are_development_and_safe():
    s = Settings(_env_file=None)
    assert s.cg_env == "development"
    assert s.cors_origins == []
    assert s.is_production is False


def test_valid_production_accepted():
    assert make().is_production


@pytest.mark.parametrize(
    "over",
    [
        {"secret_key": ""},
        {"secret_key": "change-me"},
        {"secret_key": "short"},
        {"app_base_url": "http://app.example.org"},
        {"cors_origins": ["*"]},
        {"cors_origins": ["http://insecure.example.org"]},
        {"trusted_hosts": ["*"]},
        {"database_url": ""},
        {"redis_url": ""},
        {"captcha_bypass": True},
        {"sms_provider": "console"},
        {"email_provider": "console"},
    ],
)
def test_insecure_production_refused(over):
    with pytest.raises((ConfigError, ValidationError)):
        make(**over)


def test_error_message_never_contains_secret_value():
    with pytest.raises((ConfigError, ValidationError)) as exc:
        make(secret_key="change-me")
    assert "change-me" not in str(exc.value)


def test_staging_is_treated_as_production():
    with pytest.raises((ConfigError, ValidationError)):
        make(cg_env="staging", secret_key="")


def test_out_of_range_pool_size_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, db_pool_size=0)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, db_pool_size=500)


def test_invalid_env_value_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, cg_env="prod")


def test_origin_for_links_prefers_public_origin():
    assert make(public_origin="https://x.example.org/").origin_for_links == "https://x.example.org"
    assert make().origin_for_links == "https://app.example.org"


@pytest.mark.security
@pytest.mark.parametrize("env", ["test", "development"])
def test_hosted_platform_refuses_test_and_development_modes(monkeypatch, env):
    monkeypatch.setenv("RENDER", "true")
    with pytest.raises(ConfigError):
        Settings(_env_file=None, cg_env=env)
    monkeypatch.delenv("RENDER")
    assert Settings(_env_file=None, cg_env=env).cg_env == env  # locally they are fine
