from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter()

DbSession = Annotated[
    AsyncSession,
    Depends(get_db),
]


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check(
    db: DbSession,
) -> dict[str, str]:
    await db.execute(text("SELECT 1"))

    return {"status": "ready"}
