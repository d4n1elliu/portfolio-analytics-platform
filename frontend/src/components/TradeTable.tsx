import type { Trade, TradeSide, TradeSortKey } from '../api/types'
import { UNIT_PRICE_DECIMALS, formatCurrency, formatDate, formatQuantity } from '../lib/format'
import Badge from './Badge'
import type { BadgeTone } from './Badge'
import DataTable from './DataTable'
import type { Column } from './DataTable'
import TickerLink from './TickerLink'
import type { SortBy } from '../lib/sorting'

const SIDE_TONES: Record<TradeSide, BadgeTone> = { BUY: 'positive', SELL: 'negative' }

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
    render: (trade) => <Badge tone={SIDE_TONES[trade.side]}>{trade.side}</Badge>,
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
