from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

MessageText = Annotated[
    str,
    Field(
        min_length=1,
        max_length=4000,
        description="User message sent to the support assistant.",
    ),
]


class ChatRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    message: MessageText


class ChatResponse(BaseModel):
    session_id: str
    message: str
    reply: str


class MessageHistory(BaseModel):
    user_message: str
    ai_response: str
    created_at: datetime


class HistoryResponse(BaseModel):
    session_id: str
    messages: list[MessageHistory]
