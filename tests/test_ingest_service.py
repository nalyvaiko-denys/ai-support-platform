from pathlib import Path

import pytest

from app.models.document import DocumentChunk
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
        self.contents_by_source: dict[
            str,
            list[str],
        ] = {}

    async def get_contents_by_source(
        self,
        source: str,
    ) -> list[str]:
        return self.contents_by_source.get(
            source,
            [],
        )

    async def replace_source(
        self,
        *,
        source: str,
        chunks: list[DocumentChunk],
    ) -> None:
        self.contents_by_source[source] = [
            chunk.content
            for chunk in chunks
        ]


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.calls: list[str] = []

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
