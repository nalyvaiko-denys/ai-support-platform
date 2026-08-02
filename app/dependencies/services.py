from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.llm.client import BaseLLMClient
from app.llm.factory import get_llm_client
from app.repositories.conversation_repository import (
    ConversationRepository,
)
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.chat_service import ChatService
from app.services.embedding_service import EmbeddingService

DbSession = Annotated[
    AsyncSession,
    Depends(get_db),
]


def get_conversation_repository(
    db: DbSession,
) -> ConversationRepository:
    return ConversationRepository(db)


def get_document_repository(
    db: DbSession,
) -> DocumentRepository:
    return DocumentRepository(db)


LLMClientDep = Annotated[
    BaseLLMClient,
    Depends(get_llm_client),
]

ConversationRepositoryDep = Annotated[
    ConversationRepository,
    Depends(get_conversation_repository),
]

DocumentRepositoryDep = Annotated[
    DocumentRepository,
    Depends(get_document_repository),
]


def get_embedding_service(
    client: LLMClientDep,
) -> EmbeddingService:
    return EmbeddingService(client)


EmbeddingServiceDep = Annotated[
    EmbeddingService,
    Depends(get_embedding_service),
]


def get_chat_service(
    db: DbSession,
    repository: ConversationRepositoryDep,
    document_repository: DocumentRepositoryDep,
    embedding_service: EmbeddingServiceDep,
    client: LLMClientDep,
) -> ChatService:
    return ChatService(
        db=db,
        repository=repository,
        document_repository=document_repository,
        embedding_service=embedding_service,
        client=client,
        retrieval_min_similarity=settings.retrieval_min_similarity,
        retrieval_limit=settings.retrieval_limit,
    )


ChatServiceDep = Annotated[
    ChatService,
    Depends(get_chat_service),
]
