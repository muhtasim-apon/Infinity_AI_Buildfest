"""Request bodies. `extra="forbid"` on every model: unknown fields (role, tenant_id, status,
user_id, synthetic...) are a 422, which is the mass-assignment defence at the edge (spec 16.5)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Locale = Literal["bn", "en"]
EMAIL = r"^[^@\s]{1,64}@[^@\s]{1,189}\.[^@\s]{2,}$"
OTP = r"^[0-9]{6}$"


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RegisterFarmerIn(Strict):
    phone: str = Field(min_length=1, max_length=40)
    password: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=80)
    locale: Locale = "bn"
    accept_service: Literal[True]  # required consent; cannot be omitted or false
    training_use: bool = False
    push_alerts: bool = False
    captcha: str | None = Field(default=None, max_length=2048)
    website: str = Field(default="", max_length=200)  # honeypot: humans never see it


class OtpSendIn(Strict):
    phone: str = Field(min_length=1, max_length=40)
    purpose: Literal["register", "reset"] = "register"
    captcha: str | None = Field(default=None, max_length=2048)


class OtpVerifyIn(Strict):
    phone: str = Field(min_length=1, max_length=40)
    code: str = Field(pattern=OTP)
    keep_signed_in: bool = False


class LoginIn(Strict):
    identifier: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=128)
    keep_signed_in: bool = False
    captcha: str | None = Field(default=None, max_length=2048)


class TotpIn(Strict):
    code: str = Field(min_length=6, max_length=16)
    recovery: bool = False


class CodeIn(Strict):
    code: str = Field(pattern=OTP)


class ForgotIn(Strict):
    identifier: str = Field(min_length=1, max_length=254)
    captcha: str | None = Field(default=None, max_length=2048)


class ResetIn(Strict):
    new_password: str = Field(min_length=1, max_length=128)
    token: str | None = Field(default=None, max_length=256)
    phone: str | None = Field(default=None, max_length=40)
    code: str | None = Field(default=None, pattern=OTP)


class ChangePasswordIn(Strict):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=1, max_length=128)


class StaffRegisterIn(Strict):
    token: str = Field(min_length=16, max_length=256)
    password: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=80)
    locale: Locale = "bn"


class TokenIn(Strict):
    token: str = Field(min_length=16, max_length=256)


class DemoIn(Strict):
    role: Literal["DEMO_FARMER", "DEMO_REVIEWER", "DEMO_ADMIN"]
    captcha: str | None = Field(default=None, max_length=2048)


class InviteIn(Strict):
    email: str = Field(pattern=EMAIL, max_length=254)
    role: Literal["REVIEWER", "ADMIN"]
    region_codes: list[str] = Field(default_factory=list, max_length=30)


class ProfilePatch(Strict):
    display_name: str | None = Field(default=None, min_length=1, max_length=80)
    locale: Locale | None = None


class ConsentPut(Strict):
    purpose: Literal["training_use", "push_alerts", "service"]
    granted: bool
