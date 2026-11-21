"""Write trades as CSV text. Uses no database."""

import csv
import io
from collections.abc import Iterable

from app.models import Trade
from app.services.trade_csv import REQUIRED_COLUMNS

EXPORT_COLUMNS = (*REQUIRED_COLUMNS, "fees")


def trades_to_csv(trades: Iterable[Trade]) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(EXPORT_COLUMNS)
    for trade in trades:
        writer.writerow(
            [
                trade.trade_date.isoformat(),
                trade.security.ticker,
                trade.side,
                trade.quantity,
                trade.price,
                trade.fees,
            ]
        )
    return output.getvalue()
