import type { ReactNode } from 'react'

import type { Holding } from '../api/types'
import { NO_VALUE, formatCurrency, formatPercent, formatQuantity } from '../lib/format'
import DataTable from './DataTable'
import type { Column } from './DataTable'
import Profit from './Profit'

const UNIT_COST_DECIMALS = 4

const COLUMNS: Column<Holding>[] = [
  {
    header: 'Security',
    render: (holding) => <TwoLines main={holding.ticker} detail={holding.security_name} bold />,
    sortValue: (holding) => holding.ticker,
  },
  {
    header: 'Sector',
    render: (holding) => <TwoLines main={holding.sector} detail={holding.asset_class} />,
    sortValue: (holding) => holding.sector,
  },
  numberColumn('Quantity', (holding) => holding.quantity, formatQuantity),
  moneyColumn('Avg cost', (holding) => holding.average_cost, formatUnitCost),
  moneyColumn('Last price', (holding) => holding.last_price),
  moneyColumn('Cost basis', (holding) => holding.cost_basis),
  moneyColumn('Market value', (holding) => holding.market_value),
  numberColumn(
    'Unrealised P&L',
    (holding) => holding.unrealised_pnl,
    (pnl, holding) => (
      <Profit amount={pnl} currency={holding.currency} returnOnCost={holding.unrealised_return} />
    ),
  ),
  numberColumn(
    'Weight',
    (holding) => holding.weight,
    (weight) => formatPercent(Number(weight)),
  ),
  numberColumn(
    'Realised P&L',
    (holding) => holding.realised_pnl,
    (pnl, holding) => <Profit amount={pnl} currency={holding.currency} />,
  ),
]

/** A sortable column of numbers. A missing value shows a dash and is sorted last. */
function numberColumn(
  header: string,
  valueOf: (holding: Holding) => string | null,
  show: (value: string, holding: Holding) => ReactNode,
): Column<Holding> {
  return {
    header,
    align: 'right',
    render: (holding) => {
      const value = valueOf(holding)
      return value === null ? NO_VALUE : show(value, holding)
    },
    sortValue: (holding) => {
      const value = valueOf(holding)
      return value === null ? null : Number(value)
    },
  }
}

function moneyColumn(
  header: string,
  amountOf: (holding: Holding) => string | null,
  format: (amount: string, currency: string) => string = formatCurrency,
): Column<Holding> {
  return numberColumn(header, amountOf, (amount, holding) => format(amount, holding.currency))
}

interface TwoLinesProps {
  main: string
  detail: string
  bold?: boolean
}

/** A value with a smaller line of detail under it. */
function TwoLines({ main, detail, bold = false }: TwoLinesProps) {
  return (
    <div className="min-w-32">
      <div className={bold ? 'font-medium' : ''}>{main}</div>
      <div className="text-xs text-slate-500">{detail}</div>
    </div>
  )
}

/** Shows the same number of decimals on every row. */
function formatUnitCost(value: string, currency: string): string {
  return formatCurrency(value, currency, UNIT_COST_DECIMALS, UNIT_COST_DECIMALS)
}

function HoldingsTable({ holdings }: { holdings: Holding[] }) {
  return <DataTable columns={COLUMNS} rows={holdings} getRowKey={(holding) => holding.ticker} />
}

export default HoldingsTable
