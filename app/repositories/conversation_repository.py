from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def add(
        self,
        conversation: Conversation,
    ) -> None:
        self.db.add(conversation)

    async def get_last_messages(
        self,
        owner_id: str,
        session_id: str,
        limit: int = 10,
    ) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.owner_id == owner_id,
                Conversation.session_id == session_id,
            )
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )

        conversations = list(result.scalars().all())
        conversations.reverse()

        return conversations
