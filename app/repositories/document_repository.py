from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_contents_by_source(
        self,
        source: str,
    ) -> list[str]:
        result = await self.db.execute(
            select(DocumentChunk.content)
            .where(DocumentChunk.source == source)
            .order_by(DocumentChunk.id)
        )

        return list(result.scalars().all())

    async def replace_source(
        self,
        *,
        source: str,
        chunks: list[DocumentChunk],
    ) -> None:
        await self.db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.source == source
            )
        )

        self.db.add_all(chunks)

    async def search_similar(
        self,
        query_embedding: list[float],
        limit: int = 3,
    ) -> list[DocumentChunk]:
        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding
        )

        result = await self.db.execute(
            select(DocumentChunk)
            .order_by(distance)
            .limit(limit)
        )

        return list(result.scalars().all())
