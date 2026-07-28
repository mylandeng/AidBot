from typing import Any

from pydantic import BaseModel


class ErrorPayload(BaseModel):
    code: str
    message: str
    retryable: bool = False
    request_id: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorPayload
    detail: Any | None = None
