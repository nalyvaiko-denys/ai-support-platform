"""add conversation ownership

Revision ID: 34f2a91d8c70
Revises: 0f4e88a9c321
Create Date: 2026-08-02

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "34f2a91d8c70"
down_revision: str | Sequence[str] | None = "0f4e88a9c321"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column(
            "owner_id",
            sa.String(length=255),
            nullable=False,
            server_default="legacy",
        ),
    )
    op.alter_column(
        "conversations",
        "owner_id",
        server_default=None,
    )
    op.drop_index(
        op.f("ix_conversations_session_id"),
        table_name="conversations",
    )
    op.create_index(
        "ix_conversations_owner_session_created",
        "conversations",
        ["owner_id", "session_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_conversations_owner_session_created",
        table_name="conversations",
    )
    op.create_index(
        op.f("ix_conversations_session_id"),
        "conversations",
        ["session_id"],
        unique=False,
    )
    op.drop_column("conversations", "owner_id")
