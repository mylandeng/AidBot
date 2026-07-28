from enum import StrEnum
from typing import Any

from fastapi import status
from starlette.exceptions import HTTPException

from app.schemas.error import ErrorPayload


class ErrorCode(StrEnum):
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    FORBIDDEN = "FORBIDDEN"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    BAD_REQUEST = "BAD_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    CONVERSATION_ARCHIVED = "CONVERSATION_ARCHIVED"
    KNOWLEDGE_SPACE_NOT_FOUND = "KNOWLEDGE_SPACE_NOT_FOUND"
    KNOWLEDGE_SPACE_PRODUCT_LINE_REQUIRED = "KNOWLEDGE_SPACE_PRODUCT_LINE_REQUIRED"
    KNOWLEDGE_SPACE_CONFLICT = "KNOWLEDGE_SPACE_CONFLICT"
    RETRIEVAL_UNAVAILABLE = "RETRIEVAL_UNAVAILABLE"
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


DEFAULT_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.INVALID_CREDENTIALS: "邮箱或密码不正确。",
    ErrorCode.AUTH_EXPIRED: "登录已失效，请重新登录。",
    ErrorCode.FORBIDDEN: "当前账号没有执行此操作的权限。",
    ErrorCode.VALIDATION_FAILED: "请求参数不正确，请检查后重试。",
    ErrorCode.BAD_REQUEST: "请求无法处理，请检查后重试。",
    ErrorCode.NOT_FOUND: "请求的资源不存在。",
    ErrorCode.CONFLICT: "当前状态不允许执行此操作。",
    ErrorCode.CONVERSATION_NOT_FOUND: "会话不存在或已被删除。",
    ErrorCode.CONVERSATION_ARCHIVED: "已归档的会话不能继续提问。",
    ErrorCode.KNOWLEDGE_SPACE_NOT_FOUND: "知识库不存在或已被删除。",
    ErrorCode.KNOWLEDGE_SPACE_PRODUCT_LINE_REQUIRED: "知识库尚未配置产品线。",
    ErrorCode.KNOWLEDGE_SPACE_CONFLICT: "当前会话已绑定其他产品知识库。",
    ErrorCode.RETRIEVAL_UNAVAILABLE: "知识库检索暂时不可用，请稍后重试。",
    ErrorCode.LLM_UNAVAILABLE: "模型暂时不可用，请稍后重试。",
    ErrorCode.INTERNAL_ERROR: "服务暂时不可用，请稍后重试。",
}


class AppException(Exception):
    def __init__(
        self,
        code: ErrorCode,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        message: str | None = None,
        retryable: bool = False,
        details: Any | None = None,
    ) -> None:
        self.code = code
        self.status_code = status_code
        self.message = message or DEFAULT_MESSAGES[code]
        self.retryable = retryable
        self.details = details
        super().__init__(self.message)


def payload_for_app_exception(exc: AppException, request_id: str) -> ErrorPayload:
    return ErrorPayload(
        code=exc.code,
        message=exc.message,
        retryable=exc.retryable,
        request_id=request_id,
        details=exc.details,
    )


def payload_for_http_exception(exc: HTTPException, request_id: str) -> ErrorPayload:
    detail = exc.detail
    if isinstance(detail, dict):
        explicit_code = str(detail.get("code", "")).strip()
        explicit_message = str(detail.get("message", "")).strip()
        code = explicit_code or fallback_code(exc.status_code).value
        message = explicit_message or fallback_message(exc.status_code)
        return ErrorPayload(code=code, message=message, retryable=False, request_id=request_id)

    raw_message = str(detail)
    code = code_for_legacy_error(exc.status_code, raw_message)
    return ErrorPayload(
        code=code,
        message=localized_message(code, raw_message),
        retryable=code in {ErrorCode.RETRIEVAL_UNAVAILABLE},
        request_id=request_id,
    )


def code_for_legacy_error(status_code: int, message: str) -> ErrorCode:
    normalized = message.strip().lower()
    known_messages = {
        "invalid email or password": ErrorCode.INVALID_CREDENTIALS,
        "invalid token": ErrorCode.AUTH_EXPIRED,
        "token expired": ErrorCode.AUTH_EXPIRED,
        "missing bearer token": ErrorCode.AUTH_EXPIRED,
        "insufficient permissions": ErrorCode.FORBIDDEN,
        "conversation not found": ErrorCode.CONVERSATION_NOT_FOUND,
        "archived conversations cannot receive new messages": ErrorCode.CONVERSATION_ARCHIVED,
        "knowledge space not found": ErrorCode.KNOWLEDGE_SPACE_NOT_FOUND,
        "knowledge space has no product line": ErrorCode.KNOWLEDGE_SPACE_PRODUCT_LINE_REQUIRED,
        "conversation is bound to another knowledge space": ErrorCode.KNOWLEDGE_SPACE_CONFLICT,
    }
    if normalized in known_messages:
        return known_messages[normalized]
    if "外部知识库尚未配置" in message:
        return ErrorCode.RETRIEVAL_UNAVAILABLE
    return fallback_code(status_code)


def fallback_code(status_code: int) -> ErrorCode:
    if status_code == status.HTTP_401_UNAUTHORIZED:
        return ErrorCode.AUTH_EXPIRED
    if status_code == status.HTTP_403_FORBIDDEN:
        return ErrorCode.FORBIDDEN
    if status_code == status.HTTP_404_NOT_FOUND:
        return ErrorCode.NOT_FOUND
    if status_code == status.HTTP_409_CONFLICT:
        return ErrorCode.CONFLICT
    if status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        return ErrorCode.VALIDATION_FAILED
    return ErrorCode.BAD_REQUEST


def fallback_message(status_code: int) -> str:
    return DEFAULT_MESSAGES[fallback_code(status_code)]


def localized_message(code: ErrorCode, original: str) -> str:
    if any("\u4e00" <= character <= "\u9fff" for character in original):
        return original
    return DEFAULT_MESSAGES[code]
