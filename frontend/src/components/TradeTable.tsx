import type { Trade, TradeSide, TradeSortKey } from '../api/types'
import { formatCurrency, formatDate, formatQuantity } from '../lib/format'
import DataTable from './DataTable'
import type { Column } from './DataTable'
import type { SortBy } from '../lib/sorting'

// Unit prices can be quoted in fractions of a cent.
const PRICE_DECIMALS = 4

const SIDE_COLOURS: Record<TradeSide, string> = {
  BUY: 'bg-emerald-50 text-emerald-700',
  SELL: 'bg-red-50 text-red-700',
}

/** Every column the API can order by has a sortKey. */
const COLUMNS: (Column<Trade> & { sortKey?: TradeSortKey })[] = [
  {
    header: 'Date',
    render: (trade) => formatDate(trade.trade_date),
    className: 'whitespace-nowrap',
    sortKey: 'trade_date',
  },
  {
    header: 'Ticker',
    render: (trade) => trade.ticker,
    className: 'font-medium',
    sortKey: 'ticker',
  },
  { header: 'Security', render: (trade) => trade.security_name, className: 'text-slate-600' },
  {
    header: 'Side',
    sortKey: 'side',
    render: (trade) => (
      <span className={`rounded px-2 py-0.5 text-xs font-medium ${SIDE_COLOURS[trade.side]}`}>
        {trade.side}
      </span>
    ),
  },
  {
    header: 'Quantity',
    align: 'right',
    render: (trade) => formatQuantity(trade.quantity),
    sortKey: 'quantity',
  },
  {
    header: 'Price',
    align: 'right',
    render: (trade) => formatCurrency(trade.price, trade.currency, PRICE_DECIMALS),
    sortKey: 'price',
  },
  {
    header: 'Fees',
    align: 'right',
    render: (trade) => formatCurrency(trade.fees, trade.currency),
    sortKey: 'fees',
  },
]

interface TradeTableProps {
  /** One page of trades, already in the order of `sort`. */
  trades: Trade[]
  sort: SortBy<TradeSortKey>
  onSort: (sortKey: TradeSortKey) => void
}

/** The trades table: a DataTable with the columns for a trade, sorted by the API. */
function TradeTable({ trades, sort, onSort }: TradeTableProps) {
  return (
    <DataTable
      columns={COLUMNS}
      rows={trades}
      getRowKey={(trade) => trade.id}
      sort={sort}
      // The table only passes back a sortKey from COLUMNS.
      onSort={(sortKey) => onSort(sortKey as TradeSortKey)}
    />
  )
}

export default TradeTable
