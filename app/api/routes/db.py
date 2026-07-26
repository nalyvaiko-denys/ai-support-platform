from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.session import get_db

router = APIRouter()


@router.get("/db")
async def check_database(
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(text("SELECT 1"))

    return {
        "database": result.scalar(),
    }