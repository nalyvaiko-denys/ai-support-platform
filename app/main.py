from fastapi import FastAPI

from app.api.routes.router import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Support Platform",
        version="0.1.0",
        description="AI-powered customer support backend",
    )

    app.include_router(router)

    return app


app = create_app()