import type { Holding } from '../api/types'
import { NO_VALUE, formatCurrency, formatProfit, formatQuantity } from '../lib/format'
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
  moneyColumn('Avg cost', (holding) => holding.average_cost, formatUnitCost),
  moneyColumn('Last price', (holding) => holding.last_price),
  moneyColumn('Cost basis', (holding) => holding.cost_basis),
  moneyColumn('Market value', (holding) => holding.market_value),
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

/** A sortable money column. A missing amount shows a dash and is sorted last. */
function moneyColumn(
  header: string,
  amountOf: (holding: Holding) => string | null,
  format: (amount: string, currency: string) => string = formatCurrency,
): Column<Holding> {
  return {
    header,
    align: 'right',
    render: (holding) => {
      const amount = amountOf(holding)
      return amount === null ? NO_VALUE : format(amount, holding.currency)
    },
    sortValue: (holding) => {
      const amount = amountOf(holding)
      return amount === null ? null : Number(amount)
    },
  }
}

/** Shows the same number of decimals on every row. */
function formatUnitCost(value: string, currency: string): string {
  return formatCurrency(value, currency, UNIT_COST_DECIMALS, UNIT_COST_DECIMALS)
}

function HoldingsTable({ holdings }: { holdings: Holding[] }) {
  return <DataTable columns={COLUMNS} rows={holdings} getRowKey={(holding) => holding.ticker} />
}

export default HoldingsTable
