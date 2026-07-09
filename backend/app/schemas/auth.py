from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=256)


class KeyLoginRequest(BaseModel):
    access_key: str = Field(min_length=12, max_length=160)


class CurrentUser(BaseModel):
    id: str
    email: str = ""
    name: str
    roles: list[str]
    auth_method: str = "password"
    key_id: str | None = None
    key_expires_at: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: CurrentUser
