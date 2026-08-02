from types import SimpleNamespace

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.llm import LLMResponse
from app.services.chat_service import ChatService


class FakeSession:
    def __init__(self, *, fail_commit: bool = False) -> None:
        self.fail_commit = fail_commit
        self.commit_count = 0
        self.rollback_count = 0

    async def commit(self) -> None:
        self.commit_count += 1

        if self.fail_commit:
            raise SQLAlchemyError("commit failed")

    async def rollback(self) -> None:
        self.rollback_count += 1


class FakeConversationRepository:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.history = [
            SimpleNamespace(
                user_message="Previous question",
                ai_response="Previous answer",
            )
        ]

    async def get_last_messages(
        self,
        session_id: str,
        limit: int = 10,
    ) -> list[object]:
        del session_id, limit
        return self.history

    def add(self, conversation: object) -> None:
        self.added.append(conversation)


class FakeDocumentRepository:
    def __init__(self) -> None:
        self.search_arguments: dict[str, object] = {}

    async def search_similar(
        self,
        query_embedding: list[float],
        *,
        min_similarity: float,
        limit: int,
    ) -> list[object]:
        self.search_arguments = {
            "query_embedding": query_embedding,
            "min_similarity": min_similarity,
            "limit": limit,
        }
        return [
            SimpleNamespace(
                source="faq",
                content="Verified answer",
            )
        ]


class FakeEmbeddingService:
    async def create_embedding(self, text: str) -> list[float]:
        assert text == "Current question"
        return [0.1, 0.2, 0.3]


class FakeLLMClient:
    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    async def generate(
        self,
        messages: list[dict[str, str]],
    ) -> LLMResponse:
        self.messages = messages
        return LLMResponse(
            text="Current answer",
            model="test-model",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            response_time_ms=20,
        )


def create_service(
    session: FakeSession,
) -> tuple[
    ChatService,
    FakeConversationRepository,
    FakeDocumentRepository,
    FakeLLMClient,
]:
    conversation_repository = FakeConversationRepository()
    document_repository = FakeDocumentRepository()
    client = FakeLLMClient()

    service = ChatService(
        db=session,
        repository=conversation_repository,
        document_repository=document_repository,
        embedding_service=FakeEmbeddingService(),
        client=client,
        retrieval_min_similarity=0.4,
        retrieval_limit=4,
    )

    return (
        service,
        conversation_repository,
        document_repository,
        client,
    )


@pytest.mark.asyncio
async def test_ask_runs_rag_flow_and_persists_response() -> None:
    session = FakeSession()
    service, repository, document_repository, client = create_service(session)

    reply = await service.ask(
        session_id="session-1",
        message="Current question",
    )

    assert reply == "Current answer"
    assert document_repository.search_arguments == {
        "query_embedding": [0.1, 0.2, 0.3],
        "min_similarity": 0.4,
        "limit": 4,
    }
    assert "Verified answer" in client.messages[0]["content"]
    assert client.messages[-1] == {
        "role": "user",
        "content": "Current question",
    }
    assert len(repository.added) == 1

    conversation = repository.added[0]
    assert conversation.session_id == "session-1"
    assert conversation.ai_response == "Current answer"
    assert conversation.total_tokens == 15
    assert session.commit_count == 1
    assert session.rollback_count == 0


@pytest.mark.asyncio
async def test_ask_rolls_back_when_commit_fails() -> None:
    session = FakeSession(fail_commit=True)
    service, _, _, _ = create_service(session)

    with pytest.raises(SQLAlchemyError, match="commit failed"):
        await service.ask(
            session_id="session-1",
            message="Current question",
        )

    assert session.commit_count == 1
    assert session.rollback_count == 1


@pytest.mark.asyncio
async def test_get_history_delegates_to_repository() -> None:
    session = FakeSession()
    service, repository, _, _ = create_service(session)

    history = await service.get_history(
        session_id="session-1",
        limit=25,
    )

    assert history == repository.history
