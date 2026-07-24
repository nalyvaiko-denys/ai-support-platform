from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/chat")
async def chat(
    session_id: str,
    message: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    service = ChatService(db)

    answer = await service.ask(
        session_id=session_id,
        message=message,
    )

    return {"answer": answer}