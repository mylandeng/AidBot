from typing import Literal

from pydantic import BaseModel, Field


AccessKeyDuration = Literal["7d", "30d", "180d", "365d"]
AccessKeyStatus = Literal["active", "disabled", "deleted"]


class AccessKeyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    expires_in: AccessKeyDuration = "30d"
    max_requests: int | None = Field(default=None, ge=1)
    max_tokens: int | None = Field(default=None, ge=1)
    note: str = Field(default="", max_length=1000)


class AccessKeyUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    expires_in: AccessKeyDuration | None = None
    max_requests: int | None = Field(default=None, ge=1)
    max_tokens: int | None = Field(default=None, ge=1)
    note: str | None = Field(default=None, max_length=1000)


class AccessKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    status: AccessKeyStatus
    expires_at: str
    max_requests: int | None = None
    used_requests: int
    max_tokens: int | None = None
    used_tokens: int
    note: str
    last_used_at: str | None = None
    created_at: str
    updated_at: str


class AccessKeyCreateResponse(BaseModel):
    item: AccessKeyResponse
    access_key: str


class AccessKeyListResponse(BaseModel):
    items: list[AccessKeyResponse]
