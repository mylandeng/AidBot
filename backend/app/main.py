from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, chat, conversations, feedback, health, knowledge, user
from app.core.config import settings
from app.core.database import Base, engine
from app.core.schema import ensure_runtime_schema
from app import models  # noqa: F401


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
    )

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
    app.include_router(user.router, prefix="/api/user", tags=["user"])
    app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
    app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
    app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
    return app


app = create_app()
