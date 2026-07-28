from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.chunker import TextChunker
from app.models.document import DocumentChunk
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.embedding_service import EmbeddingService


@dataclass(frozen=True, slots=True)
class IngestResult:
    changed: bool
    chunks_written: int


class IngestService:
    def __init__(
        self,
        db: AsyncSession,
        repository: DocumentRepository,
        embedding_service: EmbeddingService,
    ) -> None:
        self.db = db
        self.repository = repository
        self.embedding_service = embedding_service

    async def ingest_file(
        self,
        file_path: Path,
        source: str,
    ) -> IngestResult:
        text = file_path.read_text(encoding="utf-8")
        chunks = TextChunker.chunk(text)

        existing_contents = (
            await self.repository.get_contents_by_source(
                source
            )
        )

        if existing_contents == chunks:
            return IngestResult(
                changed=False,
                chunks_written=0,
            )

        document_chunks: list[DocumentChunk] = []

        for chunk in chunks:
            embedding = (
                await self.embedding_service.create_embedding(
                    chunk
                )
            )

            document_chunks.append(
                DocumentChunk(
                    source=source,
                    content=chunk,
                    embedding=embedding,
                )
            )

        await self.repository.replace_source(
            source=source,
            chunks=document_chunks,
        )

        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return IngestResult(
            changed=True,
            chunks_written=len(document_chunks),
        )
