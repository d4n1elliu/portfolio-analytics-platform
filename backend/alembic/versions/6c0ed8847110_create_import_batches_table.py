"""create import batches table

Revision ID: 6c0ed8847110
Revises: 7c1f4a9d2b6e
Create Date: 2026-11-21 15:30:22.672212

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6c0ed8847110"
down_revision: str | Sequence[str] | None = "7c1f4a9d2b6e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the import_batches table and link each trade to its import.

    Trades saved before this migration keep an empty import_batch_id.
    """
    op.create_table(
        "import_batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("imported_by_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["imported_by_id"], ["users.id"], name=op.f("fk_import_batches_imported_by_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_import_batches")),
        sa.UniqueConstraint("file_hash", name=op.f("uq_import_batches_file_hash")),
    )
    op.add_column("trades", sa.Column("import_batch_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_trades_import_batch_id"), "trades", ["import_batch_id"], unique=False)
    op.create_foreign_key(
        op.f("fk_trades_import_batch_id_import_batches"),
        "trades",
        "import_batches",
        ["import_batch_id"],
        ["id"],
    )


def downgrade() -> None:
    """Remove the link from trades, then the import_batches table."""
    op.drop_constraint(
        op.f("fk_trades_import_batch_id_import_batches"), "trades", type_="foreignkey"
    )
    op.drop_index(op.f("ix_trades_import_batch_id"), table_name="trades")
    op.drop_column("trades", "import_batch_id")
    op.drop_table("import_batches")
