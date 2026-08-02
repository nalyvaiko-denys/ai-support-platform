from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        Index(
            "ix_conversations_owner_session_created",
            "owner_id",
            "session_id",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    owner_id: Mapped[str] = mapped_column(String(255))

    session_id: Mapped[str] = mapped_column(String(64))

    user_message: Mapped[str] = mapped_column(Text)

    ai_response: Mapped[str] = mapped_column(Text)

    model: Mapped[str] = mapped_column(String(50))

    prompt_tokens: Mapped[int] = mapped_column(Integer)

    completion_tokens: Mapped[int] = mapped_column(Integer)

    total_tokens: Mapped[int] = mapped_column(Integer)

    response_time_ms: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
