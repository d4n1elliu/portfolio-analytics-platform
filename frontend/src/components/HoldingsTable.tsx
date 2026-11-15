import type { Holding } from '../api/types'
import { formatCurrency, formatProfit, formatQuantity } from '../lib/format'
import { profitColour } from '../lib/profit'
import DataTable from './DataTable'
import type { Column } from './DataTable'

const UNIT_COST_DECIMALS = 4

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
      holding.average_cost === null
        ? '—'
        : formatCurrency(holding.average_cost, holding.currency, UNIT_COST_DECIMALS),
    sortValue: (holding) => (holding.average_cost === null ? null : Number(holding.average_cost)),
  },
  {
    header: 'Cost basis',
    align: 'right',
    render: (holding) => formatCurrency(holding.cost_basis, holding.currency),
    sortValue: (holding) => Number(holding.cost_basis),
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

function HoldingsTable({ holdings }: { holdings: Holding[] }) {
  return <DataTable columns={COLUMNS} rows={holdings} getRowKey={(holding) => holding.ticker} />
}

export default HoldingsTable
