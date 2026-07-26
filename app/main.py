from fastapi import FastAPI

from app.api.routes.router import router
from app.core.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Support Platform",
        version="0.1.0",
        description="AI-powered customer support backend",
    )

    register_exception_handlers(app)

    app.include_router(router)

    return app


app = create_app()