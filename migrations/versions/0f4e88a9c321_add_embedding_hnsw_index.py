"""add embedding hnsw index

Revision ID: 0f4e88a9c321
Revises: 8d10e4c1427a
Create Date: 2026-08-02

"""

from collections.abc import Sequence

from alembic import op

revision: str = "0f4e88a9c321"
down_revision: str | Sequence[str] | None = "8d10e4c1427a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_document_chunks_embedding_hnsw",
        "document_chunks",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={
            "embedding": "vector_cosine_ops",
        },
    )


def downgrade() -> None:
    op.drop_index(
        "ix_document_chunks_embedding_hnsw",
        table_name="document_chunks",
    )
