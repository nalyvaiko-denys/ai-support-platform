from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.router import router as api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.session import engine


@asynccontextmanager
async def lifespan(
    _app: FastAPI,
) -> AsyncIterator[None]:
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    application = FastAPI(
        title="AI Support Platform",
        summary="RAG-powered backend for AI-assisted customer support.",
        description=(
            "A Dockerized FastAPI backend that combines conversation "
            "history, knowledge-base retrieval, vector search and "
            "pluggable LLM providers."
        ),
        version="0.1.0",
        lifespan=lifespan,
        license_info={
            "name": "MIT",
            "identifier": "MIT",
        },
        openapi_tags=[
            {
                "name": "Chat",
                "description": ("Send messages and retrieve conversation history."),
            },
            {
                "name": "Health",
                "description": ("Application health and readiness endpoints."),
            },
            {
                "name": "Database",
                "description": ("Database connectivity diagnostics."),
            },
        ],
    )

    if settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    register_exception_handlers(application)

    application.include_router(
        api_router,
        prefix="/api",
    )

    return application


app = create_app()
