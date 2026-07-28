from contextlib import asynccontextmanager
import logging
import re
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.api import admin, auth, chat, conversations, feedback, health, knowledge, user
from app.core.config import settings
from app.core.database import Base, engine
from app.core.errors import AppException, ErrorCode, payload_for_app_exception, payload_for_http_exception
from app.core.schema import ensure_runtime_schema
from app.schemas.error import ErrorPayload, ErrorResponse
from app import models  # noqa: F401

logger = logging.getLogger(__name__)
request_id_pattern = re.compile(r"^[A-Za-z0-9._-]{1,80}$")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_runtime_schema(engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AidBot internal support Q&A API.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def attach_request_id(request: Request, call_next):
        requested_id = request.headers.get("X-Request-ID", "")
        request_id = requested_id if request_id_pattern.fullmatch(requested_id) else f"req_{uuid4().hex}"
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        payload = payload_for_app_exception(exc, _request_id(request))
        return _error_response(exc.status_code, payload, exc.details or exc.message)

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        payload = payload_for_http_exception(exc, _request_id(request))
        return _error_response(exc.status_code, payload, exc.detail, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"], "type": error["type"]}
            for error in exc.errors()
        ]
        payload = ErrorPayload(
            code=ErrorCode.VALIDATION_FAILED,
            message="请求参数不正确，请检查后重试。",
            retryable=False,
            request_id=_request_id(request),
            details=details,
        )
        return _error_response(422, payload, details)

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        request_id = _request_id(request)
        logger.exception("Unhandled request error request_id=%s path=%s", request_id, request.url.path, exc_info=exc)
        payload = ErrorPayload(
            code=ErrorCode.INTERNAL_ERROR,
            message="服务暂时不可用，请稍后重试。",
            retryable=True,
            request_id=request_id,
        )
        return _error_response(500, payload, "Internal server error")

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
    app.include_router(user.router, prefix="/api/user", tags=["user"])
    app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
    app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
    app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
    return app


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", f"req_{uuid4().hex}")


def _error_response(status_code: int, payload: ErrorPayload, legacy_detail, headers: dict[str, str] | None = None) -> JSONResponse:
    body = ErrorResponse(error=payload, detail=legacy_detail)
    response_headers = {**(headers or {}), "X-Request-ID": payload.request_id}
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"), headers=response_headers)


app = create_app()
