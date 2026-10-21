import pytest
from pydantic import ValidationError

from app.core.config import ConfigError, Settings

GOOD = {
    "cg_env": "production",
    "secret_key": "x" * 40,
    "app_base_url": "https://app.example.org",
    "database_url": "postgresql://u:p@h:6543/db",
    "trusted_hosts": ["api.example.org"],
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
