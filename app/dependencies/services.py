from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.llm.openai_client import OpenAIClient
from app.repositories.conversation_repository import ConversationRepository
from app.services.chat_service import ChatService


def get_conversation_repository(
    db: AsyncSession = Depends(get_db),
) -> ConversationRepository:
    return ConversationRepository(db)


def get_llm_client() -> OpenAIClient:
    return OpenAIClient()


def get_chat_service(
    repository: ConversationRepository = Depends(
        get_conversation_repository,
    ),
    client: OpenAIClient = Depends(
        get_llm_client,
    ),
) -> ChatService:
    return ChatService(
        repository=repository,
        client=client,
    )