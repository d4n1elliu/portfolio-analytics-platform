"""create securities, trades and prices tables

Revision ID: e403624ebfbd
Revises:
Create Date: 2026-11-13 00:23:54.661725

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e403624ebfbd"
# None means this is the first migration: there is nothing before it.
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the three core tables."""
    # securities is created first because trades and prices both refer to it.
    op.create_table(
        "securities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=12), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("sector", sa.String(length=100), nullable=False),
        sa.Column("asset_class", sa.String(length=50), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="AUD", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_securities")),
    )
    # A unique index makes ticker lookups fast and rejects duplicate tickers.
    op.create_index(op.f("ix_securities_ticker"), "securities", ["ticker"], unique=True)

    op.create_table(
        "prices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("security_id", sa.Integer(), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("close", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.CheckConstraint("close > 0", name=op.f("ck_prices_close_positive")),
        sa.ForeignKeyConstraint(
            ["security_id"], ["securities.id"], name=op.f("fk_prices_security_id_securities")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_prices")),
        sa.UniqueConstraint(
            "security_id", "price_date", name=op.f("uq_prices_security_id_price_date")
        ),
    )

    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("security_id", sa.Integer(), nullable=False),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("side", sa.String(length=4), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("fees", sa.Numeric(precision=18, scale=2), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("side IN ('BUY', 'SELL')", name=op.f("ck_trades_side_valid")),
        sa.CheckConstraint("fees >= 0", name=op.f("ck_trades_fees_not_negative")),
        sa.CheckConstraint("price > 0", name=op.f("ck_trades_price_positive")),
        sa.CheckConstraint("quantity > 0", name=op.f("ck_trades_quantity_positive")),
        sa.ForeignKeyConstraint(
            ["security_id"], ["securities.id"], name=op.f("fk_trades_security_id_securities")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_trades")),
    )
    op.create_index(op.f("ix_trades_security_id"), "trades", ["security_id"], unique=False)
    op.create_index(op.f("ix_trades_trade_date"), "trades", ["trade_date"], unique=False)


def downgrade() -> None:
    """Remove the three tables, in the reverse order to upgrade().

    trades and prices go first because they refer to securities. Dropping a
    table deletes all of its rows.
    """
    op.drop_index(op.f("ix_trades_trade_date"), table_name="trades")
    op.drop_index(op.f("ix_trades_security_id"), table_name="trades")
    op.drop_table("trades")
    op.drop_table("prices")
    op.drop_index(op.f("ix_securities_ticker"), table_name="securities")
    op.drop_table("securities")
