"""add embedding metadata

Revision ID: 8d10e4c1427a
Revises: db13c1a5020d
Create Date: 2026-08-02

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8d10e4c1427a"
down_revision: str | Sequence[str] | None = "db13c1a5020d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "document_chunks",
        sa.Column(
            "content_hash",
            sa.String(length=64),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "document_chunks",
        sa.Column(
            "embedding_provider",
            sa.String(length=32),
            nullable=False,
            server_default="legacy",
        ),
    )
    op.add_column(
        "document_chunks",
        sa.Column(
            "embedding_model",
            sa.String(length=100),
            nullable=False,
            server_default="legacy",
        ),
    )
    op.add_column(
        "document_chunks",
        sa.Column(
            "embedding_dimension",
            sa.Integer(),
            nullable=False,
            server_default="1536",
        ),
    )

    op.alter_column(
        "document_chunks",
        "content_hash",
        server_default=None,
    )
    op.alter_column(
        "document_chunks",
        "embedding_provider",
        server_default=None,
    )
    op.alter_column(
        "document_chunks",
        "embedding_model",
        server_default=None,
    )
    op.alter_column(
        "document_chunks",
        "embedding_dimension",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("document_chunks", "embedding_dimension")
    op.drop_column("document_chunks", "embedding_model")
    op.drop_column("document_chunks", "embedding_provider")
    op.drop_column("document_chunks", "content_hash")
