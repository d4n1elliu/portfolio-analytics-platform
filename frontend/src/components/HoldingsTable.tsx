import type { ReactNode } from 'react'

import type { Holding } from '../api/types'
import {
  NO_VALUE,
  UNIT_PRICE_DECIMALS,
  formatCurrency,
  formatPercent,
  formatQuantity,
} from '../lib/format'
import DataTable from './DataTable'
import type { Column } from './DataTable'
import Profit from './Profit'
import TickerLink from './TickerLink'

const COLUMNS: Column<Holding>[] = [
  {
    header: 'Security',
    render: (holding) => (
      <TwoLines main={<TickerLink ticker={holding.ticker} />} detail={holding.security_name} />
    ),
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
  main: ReactNode
  detail: string
}

function TwoLines({ main, detail }: TwoLinesProps) {
  return (
    <div className="min-w-32">
      <div>{main}</div>
      <div className="text-xs text-slate-500">{detail}</div>
    </div>
  )
}

/** Shows the same number of decimals on every row. */
function formatUnitCost(value: string, currency: string): string {
  return formatCurrency(value, currency, UNIT_PRICE_DECIMALS, UNIT_PRICE_DECIMALS)
}

function HoldingsTable({ holdings }: { holdings: Holding[] }) {
  return <DataTable columns={COLUMNS} rows={holdings} getRowKey={(holding) => holding.ticker} />
}

export default HoldingsTable
