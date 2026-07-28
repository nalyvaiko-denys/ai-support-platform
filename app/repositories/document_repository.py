from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add_chunk(self, chunk: DocumentChunk) -> None:
        self.db.add(chunk)
        await self.db.commit()

    async def search_similar(
            self,
            query_embedding: list[float],
            limit: int = 3
    ) -> list[DocumentChunk]:
        result = await self.db.execute(
            select(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        return list(result.scalars().all())