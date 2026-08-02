from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.chunker import TextChunker
from app.models.document import DocumentChunk
from app.repositories.document_repository import (
    DocumentChunkState,
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
        profile = self.embedding_service.profile

        expected_state = [
            DocumentChunkState(
                content_hash=sha256(chunk.encode("utf-8")).hexdigest(),
                embedding_provider=profile.provider,
                embedding_model=profile.model,
                embedding_dimension=profile.dimension,
            )
            for chunk in chunks
        ]

        existing_state = await self.repository.get_ingestion_state(source)

        if existing_state == expected_state:
            return IngestResult(
                changed=False,
                chunks_written=0,
            )

        document_chunks: list[DocumentChunk] = []

        for chunk, state in zip(
            chunks,
            expected_state,
            strict=True,
        ):
            embedding = await self.embedding_service.create_embedding(chunk)

            document_chunks.append(
                DocumentChunk(
                    source=source,
                    content=chunk,
                    content_hash=state.content_hash,
                    embedding_provider=state.embedding_provider,
                    embedding_model=state.embedding_model,
                    embedding_dimension=state.embedding_dimension,
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
