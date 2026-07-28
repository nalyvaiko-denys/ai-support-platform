from typing import Annotated

from fastapi import APIRouter, Path

from app.dependencies.services import ChatServiceDep
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    MessageHistory,
)

router = APIRouter()

SessionId = Annotated[
    str,
    Path(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Client-generated conversation identifier.",
    ),
]


@router.post(
    "/{session_id}",
    response_model=ChatResponse,
)
async def send_message(
    session_id: SessionId,
    request: ChatRequest,
    chat_service: ChatServiceDep,
) -> ChatResponse:
    reply = await chat_service.ask(
        session_id=session_id,
        message=request.message,
    )

    return ChatResponse(
        session_id=session_id,
        message=request.message,
        reply=reply,
    )


@router.get(
    "/{session_id}/history",
    response_model=HistoryResponse,
)
async def get_history(
    session_id: SessionId,
    chat_service: ChatServiceDep,
) -> HistoryResponse:
    history_records = await chat_service.get_history(
        session_id=session_id,
        limit=50,
    )

    messages = [
        MessageHistory(
            user_message=record.user_message,
            ai_response=record.ai_response,
            created_at=record.created_at,
        )
        for record in history_records
    ]

    return HistoryResponse(
        session_id=session_id,
        messages=messages,
    )
