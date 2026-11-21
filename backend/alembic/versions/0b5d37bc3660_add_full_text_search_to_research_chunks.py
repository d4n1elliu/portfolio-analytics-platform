"""add full text search to research chunks

Revision ID: 0b5d37bc3660
Revises: b22401c42635
Create Date: 2026-11-21 22:34:13.630651

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0b5d37bc3660"
down_revision: str | Sequence[str] | None = "b22401c42635"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add a column Postgres fills in itself with the searchable words of each chunk."""
    op.add_column(
        "research_chunks",
        sa.Column(
            "search_vector",
            postgresql.TSVECTOR(),
            sa.Computed("to_tsvector('english', text)", persisted=True),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_research_chunks_search_vector",
        "research_chunks",
        ["search_vector"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Remove the full-text column and its index. No chunk is lost."""
    op.drop_index(
        "ix_research_chunks_search_vector", table_name="research_chunks", postgresql_using="gin"
    )
    op.drop_column("research_chunks", "search_vector")
