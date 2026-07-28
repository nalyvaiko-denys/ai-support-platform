from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.router import router as api_router
from app.core.exceptions import register_exception_handlers

app = FastAPI(
    title="Мій Банк - AI Підтримка",
    description="API для інтелектуального чат-бота з RAG-архітектурою",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router, prefix="/api")