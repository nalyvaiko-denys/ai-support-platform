from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.client import BaseLLMClient
from app.llm.prompt_builder import PromptBuilder
from app.models.conversation import Conversation
from app.repositories.conversation_repository import (
    ConversationRepository,
)
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.embedding_service import EmbeddingService


class ChatService:
    def __init__(
        self,
        db: AsyncSession,
        repository: ConversationRepository,
        document_repository: DocumentRepository,
        embedding_service: EmbeddingService,
        client: BaseLLMClient,
        retrieval_min_similarity: float,
        retrieval_limit: int,
    ) -> None:
        self.db = db
        self.repository = repository
        self.document_repository = document_repository
        self.embedding_service = embedding_service
        self.client = client
        self.retrieval_min_similarity = retrieval_min_similarity
        self.retrieval_limit = retrieval_limit

    async def ask(
        self,
        owner_id: str,
        session_id: str,
        message: str,
    ) -> str:
        history = await self.repository.get_last_messages(
            owner_id,
            session_id,
        )

        query_embedding = await self.embedding_service.create_embedding(
            message,
        )

        similar_docs = await self.document_repository.search_similar(
            query_embedding=query_embedding,
            min_similarity=self.retrieval_min_similarity,
            limit=self.retrieval_limit,
        )

        context = "\n\n".join(
            (f"Source: {document.source}\nInformation: {document.content}")
            for document in similar_docs
        )

        messages = PromptBuilder.build(
            history=history,
            message=message,
            context=context,
        )

        result = await self.client.generate(messages)

        conversation = Conversation(
            owner_id=owner_id,
            session_id=session_id,
            user_message=message,
            ai_response=result.text,
            model=result.model,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.total_tokens,
            response_time_ms=result.response_time_ms,
        )

        self.repository.add(conversation)

        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return result.text

    async def get_history(
        self,
        owner_id: str,
        session_id: str,
        *,
        limit: int = 50,
    ) -> list[Conversation]:
        return await self.repository.get_last_messages(
            owner_id=owner_id,
            session_id=session_id,
            limit=limit,
        )
