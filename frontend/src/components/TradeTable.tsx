import type { Trade, TradeSide, TradeSortKey } from '../api/types'
import { UNIT_PRICE_DECIMALS, formatCurrency, formatDate, formatQuantity } from '../lib/format'
import DataTable from './DataTable'
import type { Column } from './DataTable'
import TickerLink from './TickerLink'
import type { SortBy } from '../lib/sorting'

const SIDE_COLOURS: Record<TradeSide, string> = {
  BUY: 'bg-emerald-50 text-emerald-700',
  SELL: 'bg-red-50 text-red-700',
}

const COLUMNS: (Column<Trade> & { sortKey?: TradeSortKey })[] = [
  {
    header: 'Date',
    render: (trade) => formatDate(trade.trade_date),
    className: 'whitespace-nowrap',
    sortKey: 'trade_date',
  },
  {
    header: 'Ticker',
    render: (trade) => <TickerLink ticker={trade.ticker} />,
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
    render: (trade) => formatCurrency(trade.price, trade.currency, UNIT_PRICE_DECIMALS),
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
  trades: Trade[]
  sort: SortBy<TradeSortKey>
  onSort: (sortKey: TradeSortKey) => void
}

function TradeTable({ trades, sort, onSort }: TradeTableProps) {
  return (
    <DataTable
      columns={COLUMNS}
      rows={trades}
      getRowKey={(trade) => trade.id}
      sort={sort}
      onSort={(sortKey) => onSort(sortKey as TradeSortKey)}
    />
  )
}

export default TradeTable
