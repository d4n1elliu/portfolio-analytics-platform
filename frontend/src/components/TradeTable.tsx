import type { Trade, TradeSide } from '../api/types'
import { formatCurrency, formatDate, formatQuantity } from '../lib/format'
import DataTable from './DataTable'
import type { Column } from './DataTable'

// Unit prices can be quoted in fractions of a cent.
const PRICE_DECIMALS = 4

const SIDE_COLOURS: Record<TradeSide, string> = {
  BUY: 'bg-emerald-50 text-emerald-700',
  SELL: 'bg-red-50 text-red-700',
}

const COLUMNS: Column<Trade>[] = [
  {
    header: 'Date',
    render: (trade) => formatDate(trade.trade_date),
    className: 'whitespace-nowrap',
  },
  { header: 'Ticker', render: (trade) => trade.ticker, className: 'font-medium' },
  { header: 'Security', render: (trade) => trade.security_name, className: 'text-slate-600' },
  {
    header: 'Side',
    render: (trade) => (
      <span className={`rounded px-2 py-0.5 text-xs font-medium ${SIDE_COLOURS[trade.side]}`}>
        {trade.side}
      </span>
    ),
  },
  { header: 'Quantity', align: 'right', render: (trade) => formatQuantity(trade.quantity) },
  {
    header: 'Price',
    align: 'right',
    render: (trade) => formatCurrency(trade.price, trade.currency, PRICE_DECIMALS),
  },
  {
    header: 'Fees',
    align: 'right',
    render: (trade) => formatCurrency(trade.fees, trade.currency),
  },
]

/** The trades table: a DataTable with the columns for a trade. */
function TradeTable({ trades }: { trades: Trade[] }) {
  return <DataTable columns={COLUMNS} rows={trades} getRowKey={(trade) => trade.id} />
}

export default TradeTable
