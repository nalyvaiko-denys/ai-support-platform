from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, HistoryResponse, MessageHistory
from app.services.chat_service import ChatService
from app.dependencies.services import get_chat_service

router = APIRouter()

@router.post("/{session_id}", response_model=ChatResponse)
async def send_message(
    session_id: str,
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    try:
        reply = await chat_service.ask(session_id=session_id, message=request.message)
        return ChatResponse(
            session_id=session_id,
            message=request.message,
            reply=reply
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка генерації відповіді: {str(e)}")

@router.get("/{session_id}/history", response_model=HistoryResponse)
async def get_history(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    history_records = await chat_service.repository.get_last_messages(session_id, limit=50)

    messages = [
        MessageHistory(
            user_message=record.user_message,
            ai_response=record.ai_response,
            created_at=record.created_at
        )
        for record in history_records
    ]

    return HistoryResponse(session_id=session_id, messages=messages)