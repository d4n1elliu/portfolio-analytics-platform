import type { Holding } from '../api/types'
import { formatCurrency, formatProfit, formatQuantity } from '../lib/format'
import { profitColour } from '../lib/profit'
import DataTable from './DataTable'
import type { Column } from './DataTable'

const UNIT_COST_DECIMALS = 4
const NO_VALUE = '—'

const COLUMNS: Column<Holding>[] = [
  {
    header: 'Security',
    render: (holding) => (
      <>
        <div className="font-medium">{holding.ticker}</div>
        <div className="text-xs whitespace-nowrap text-slate-500">{holding.security_name}</div>
      </>
    ),
    sortValue: (holding) => holding.ticker,
  },
  {
    header: 'Sector',
    render: (holding) => holding.sector,
    sortValue: (holding) => holding.sector,
  },
  {
    header: 'Asset class',
    render: (holding) => holding.asset_class,
    sortValue: (holding) => holding.asset_class,
  },
  {
    header: 'Quantity',
    align: 'right',
    render: (holding) => formatQuantity(holding.quantity),
    sortValue: (holding) => Number(holding.quantity),
  },
  {
    header: 'Avg cost',
    align: 'right',
    render: (holding) =>
      orDash(holding.average_cost, (cost) => formatUnitCost(cost, holding.currency)),
    sortValue: (holding) => numberOrNull(holding.average_cost),
  },
  {
    header: 'Last price',
    align: 'right',
    render: (holding) =>
      orDash(holding.last_price, (price) => formatCurrency(price, holding.currency)),
    sortValue: (holding) => numberOrNull(holding.last_price),
  },
  {
    header: 'Cost basis',
    align: 'right',
    render: (holding) => formatCurrency(holding.cost_basis, holding.currency),
    sortValue: (holding) => Number(holding.cost_basis),
  },
  {
    header: 'Market value',
    align: 'right',
    render: (holding) =>
      orDash(holding.market_value, (value) => formatCurrency(value, holding.currency)),
    sortValue: (holding) => numberOrNull(holding.market_value),
  },
  {
    header: 'Realised P&L',
    align: 'right',
    render: (holding) => (
      <span className={profitColour(holding.realised_pnl)}>
        {formatProfit(holding.realised_pnl, holding.currency)}
      </span>
    ),
    sortValue: (holding) => Number(holding.realised_pnl),
  },
]

/** Shows a dash for a missing value, such as the price of a closed position. */
function orDash(value: string | null, format: (value: string) => string): string {
  return value === null ? NO_VALUE : format(value)
}

/** The value to sort by. A missing value stays null, so its row is listed last. */
function numberOrNull(value: string | null): number | null {
  return value === null ? null : Number(value)
}

/** Shows the same number of decimals on every row. */
function formatUnitCost(value: string, currency: string): string {
  return formatCurrency(value, currency, UNIT_COST_DECIMALS, UNIT_COST_DECIMALS)
}

function HoldingsTable({ holdings }: { holdings: Holding[] }) {
  return <DataTable columns={COLUMNS} rows={holdings} getRowKey={(holding) => holding.ticker} />
}

export default HoldingsTable
