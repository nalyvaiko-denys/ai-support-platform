from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.llm.openai_client import OpenAIClient
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.document_repository import DocumentRepository
from app.services.chat_service import ChatService
from app.services.embedding_service import EmbeddingService


def get_conversation_repository(
    db: AsyncSession = Depends(get_db),
) -> ConversationRepository:
    return ConversationRepository(db)


def get_document_repository(
    db: AsyncSession = Depends(get_db),
) -> DocumentRepository:
    return DocumentRepository(db)


def get_llm_client() -> OpenAIClient:
    return OpenAIClient()


def get_embedding_service(
    client: OpenAIClient = Depends(get_llm_client),
) -> EmbeddingService:
    return EmbeddingService(client)


def get_chat_service(
    repository: ConversationRepository = Depends(get_conversation_repository),
    document_repository: DocumentRepository = Depends(get_document_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    client: OpenAIClient = Depends(get_llm_client),
) -> ChatService:
    return ChatService(
        repository=repository,
        document_repository=document_repository,
        embedding_service=embedding_service,
        client=client,
    )