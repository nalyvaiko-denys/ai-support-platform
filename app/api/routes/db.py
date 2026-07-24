from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import engine

router = APIRouter()


@router.get("/db")
def check_database():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

    return {"database": result.scalar()}