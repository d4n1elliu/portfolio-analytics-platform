import type { ReactNode } from 'react'

import type { Holding } from '../api/types'
import {
  NO_VALUE,
  UNIT_PRICE_DECIMALS,
  formatCurrency,
  formatPercent,
  formatQuantity,
} from '../lib/format'
import Profit from './Profit'
import StatTiles from './StatTiles'

/** The position in one security, as a row of tiles. */
function SecurityPosition({ holding }: { holding: Holding }) {
  const { currency } = holding
  const unitPrice = (value: string) => formatCurrency(value, currency, UNIT_PRICE_DECIMALS)

  return (
    <StatTiles
      stats={[
        { label: 'Quantity', value: formatQuantity(holding.quantity) },
        { label: 'Average cost', value: orDash(holding.average_cost, unitPrice) },
        { label: 'Last price', value: orDash(holding.last_price, unitPrice) },
        {
          label: 'Market value',
          value: orDash(holding.market_value, (value) => formatCurrency(value, currency)),
        },
        {
          label: 'Unrealised P&L',
          value: orDash(holding.unrealised_pnl, (value) => (
            <Profit amount={value} currency={currency} returnOnCost={holding.unrealised_return} />
          )),
        },
        {
          label: 'Realised P&L',
          value: <Profit amount={holding.realised_pnl} currency={currency} />,
        },
        {
          label: 'Weight',
          value: orDash(holding.weight, (value) => formatPercent(Number(value))),
        },
      ]}
    />
  )
}

function orDash(value: string | null, show: (value: string) => ReactNode): ReactNode {
  return value === null ? NO_VALUE : show(value)
}

export default SecurityPosition
