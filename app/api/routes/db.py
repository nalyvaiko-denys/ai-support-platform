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


@router.get("/db")
async def check_database(
    db: DbSession,
) -> dict[str, int]:
    result = await db.execute(text("SELECT 1"))

    return {
        "database": result.scalar_one(),
    }
