from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_by_session(self, session_id: str) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.session_id == session_id
            )
        )
        return list(result.scalars().all())