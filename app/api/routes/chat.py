from fastapi import APIRouter

from app.services.chat_service import ChatService

router = APIRouter()

service = ChatService()


@router.post("/chat")
async def chat(message: str) -> dict[str, str]:
    answer = await service.ask(message)
    return {"answer": answer}