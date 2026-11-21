"""create research tables

Revision ID: db777fbb47c6
Revises: aaa09affa7e0
Create Date: 2026-11-21 19:28:33.527817

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "db777fbb47c6"
down_revision: str | Sequence[str] | None = "aaa09affa7e0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Turn on pgvector and create the research tables. No existing table is changed."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "research_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("security_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("document_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["security_id"],
            ["securities.id"],
            name=op.f("fk_research_documents_security_id_securities"),
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by_id"],
            ["users.id"],
            name=op.f("fk_research_documents_uploaded_by_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_research_documents")),
        sa.UniqueConstraint("file_hash", name=op.f("uq_research_documents_file_hash")),
    )
    op.create_index(
        op.f("ix_research_documents_document_date"),
        "research_documents",
        ["document_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_research_documents_security_id"),
        "research_documents",
        ["security_id"],
        unique=False,
    )
    op.create_table(
        "research_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["research_documents.id"],
            name=op.f("fk_research_chunks_document_id_research_documents"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_research_chunks")),
        sa.UniqueConstraint(
            "document_id", "position", name="uq_research_chunks_document_id_position"
        ),
    )
    op.create_index(
        op.f("ix_research_chunks_document_id"), "research_chunks", ["document_id"], unique=False
    )
    op.create_index(
        "ix_research_chunks_embedding",
        "research_chunks",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    """Remove the research tables. The pgvector extension is left turned on."""
    op.drop_index(
        "ix_research_chunks_embedding",
        table_name="research_chunks",
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.drop_index(op.f("ix_research_chunks_document_id"), table_name="research_chunks")
    op.drop_table("research_chunks")
    op.drop_index(op.f("ix_research_documents_security_id"), table_name="research_documents")
    op.drop_index(op.f("ix_research_documents_document_date"), table_name="research_documents")
    op.drop_table("research_documents")
