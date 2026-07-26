from fastapi import APIRouter
from fastapi import Depends

from app.dependencies.services import get_chat_service
from app.schemas.chat import ChatRequest
from app.schemas.chat import ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    answer = await service.ask(
        session_id=request.session_id,
        message=request.message,
    )

    return ChatResponse(answer=answer)