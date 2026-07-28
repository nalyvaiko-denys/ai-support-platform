from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.chunker import TextChunker
from app.models.document import DocumentChunk
from app.services.embedding_service import EmbeddingService


class IngestService:
    def __init__(
        self,
        db: AsyncSession,
        embedding_service: EmbeddingService,
    ) -> None:
        self.db = db
        self.embedding_service = embedding_service

    async def ingest_file(
        self,
        file_path: Path,
        source: str,
    ) -> None:
        text = file_path.read_text(encoding="utf-8")

        chunks = TextChunker.chunk(text)

        for chunk in chunks:
            embedding = await self.embedding_service.create_embedding(chunk)

            self.db.add(
                DocumentChunk(
                    source=source,
                    content=chunk,
                    embedding=embedding,
                )
            )

        await self.db.commit()