from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk


@dataclass(frozen=True, slots=True)
class DocumentChunkState:
    content_hash: str
    embedding_provider: str
    embedding_model: str
    embedding_dimension: int


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_ingestion_state(
        self,
        source: str,
    ) -> list[DocumentChunkState]:
        result = await self.db.execute(
            select(
                DocumentChunk.content_hash,
                DocumentChunk.embedding_provider,
                DocumentChunk.embedding_model,
                DocumentChunk.embedding_dimension,
            )
            .where(DocumentChunk.source == source)
            .order_by(DocumentChunk.id)
        )

        return [
            DocumentChunkState(
                content_hash=row.content_hash,
                embedding_provider=row.embedding_provider,
                embedding_model=row.embedding_model,
                embedding_dimension=row.embedding_dimension,
            )
            for row in result.all()
        ]

    async def replace_source(
        self,
        *,
        source: str,
        chunks: list[DocumentChunk],
    ) -> None:
        await self.db.execute(
            delete(DocumentChunk).where(DocumentChunk.source == source)
        )

        self.db.add_all(chunks)

    async def search_similar(
        self,
        query_embedding: list[float],
        *,
        min_similarity: float,
        limit: int = 3,
    ) -> list[DocumentChunk]:
        distance = DocumentChunk.embedding.cosine_distance(query_embedding)
        max_distance = 1.0 - min_similarity

        result = await self.db.execute(
            select(DocumentChunk)
            .where(distance <= max_distance)
            .order_by(distance)
            .limit(limit)
        )

        return list(result.scalars().all())
