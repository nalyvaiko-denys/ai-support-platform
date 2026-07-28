from pydantic import BaseModel
from typing import List
from datetime import datetime

class ChatRequest(BaseModel):
    message: str

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
    messages: List[MessageHistory]