from pathlib import Path

import pytest

from app.llm.client import EmbeddingProfile
from app.models.document import DocumentChunk
from app.repositories.document_repository import DocumentChunkState
from app.services.ingest_service import IngestService


class FakeSession:
    def __init__(self) -> None:
        self.commit_count = 0
        self.rollback_count = 0

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1


class FakeDocumentRepository:
    def __init__(self) -> None:
        self.states_by_source: dict[
            str,
            list[DocumentChunkState],
        ] = {}

    async def get_ingestion_state(
        self,
        source: str,
    ) -> list[DocumentChunkState]:
        return self.states_by_source.get(
            source,
            [],
        )

    async def replace_source(
        self,
        *,
        source: str,
        chunks: list[DocumentChunk],
    ) -> None:
        self.states_by_source[source] = [
            DocumentChunkState(
                content_hash=chunk.content_hash,
                embedding_provider=chunk.embedding_provider,
                embedding_model=chunk.embedding_model,
                embedding_dimension=chunk.embedding_dimension,
            )
            for chunk in chunks
        ]


class FakeEmbeddingService:
    def __init__(
        self,
        profile: EmbeddingProfile | None = None,
    ) -> None:
        self.calls: list[str] = []
        self.profile = profile or EmbeddingProfile(
            provider="mock",
            model="sha256-byte-vector-v1",
            dimension=3,
        )

    async def create_embedding(
        self,
        text: str,
    ) -> list[float]:
        self.calls.append(text)

        return [
            0.1,
            0.2,
            0.3,
        ]


@pytest.mark.asyncio
async def test_ingestion_is_idempotent(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "faq.md"
    file_path.write_text(
        "Knowledge base example.",
        encoding="utf-8",
    )

    session = FakeSession()
    repository = FakeDocumentRepository()
    embedding_service = FakeEmbeddingService()

    service = IngestService(
        db=session,
        repository=repository,
        embedding_service=embedding_service,
    )

    first_result = await service.ingest_file(
        file_path=file_path,
        source="faq",
    )

    second_result = await service.ingest_file(
        file_path=file_path,
        source="faq",
    )

    assert first_result.changed is True
    assert first_result.chunks_written == 1

    assert second_result.changed is False
    assert second_result.chunks_written == 0

    assert session.commit_count == 1
    assert session.rollback_count == 0
    assert len(embedding_service.calls) == 1


@pytest.mark.asyncio
async def test_ingestion_refreshes_embeddings_when_profile_changes(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "faq.md"
    file_path.write_text(
        "Knowledge base example.",
        encoding="utf-8",
    )

    session = FakeSession()
    repository = FakeDocumentRepository()
    first_embedding_service = FakeEmbeddingService()

    first_service = IngestService(
        db=session,
        repository=repository,
        embedding_service=first_embedding_service,
    )

    await first_service.ingest_file(
        file_path=file_path,
        source="faq",
    )

    second_embedding_service = FakeEmbeddingService(
        EmbeddingProfile(
            provider="openai",
            model="text-embedding-3-small",
            dimension=3,
        )
    )
    second_service = IngestService(
        db=session,
        repository=repository,
        embedding_service=second_embedding_service,
    )

    result = await second_service.ingest_file(
        file_path=file_path,
        source="faq",
    )

    assert result.changed is True
    assert result.chunks_written == 1
    assert session.commit_count == 2
    assert second_embedding_service.calls == ["Knowledge base example."]
