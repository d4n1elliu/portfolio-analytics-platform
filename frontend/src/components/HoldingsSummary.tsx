import type { ReactNode } from 'react'

import type { Holding } from '../api/types'
import { NO_VALUE, formatCurrency } from '../lib/format'
import { summariseHoldings } from '../lib/holdings'
import { summariseValuation, valuedHoldings } from '../lib/valuation'
import Profit from './Profit'
import StatTiles from './StatTiles'

function HoldingsSummary({ holdings }: { holdings: Holding[] }) {
  const summary = summariseHoldings(holdings)
  const priced = valuedHoldings(holdings)
  const valuation = summariseValuation(priced)
  // Null when the holdings mix currencies, so no total can be shown.
  const currency = summary.currency
  // Also null when no holding has a price, so there is nothing to value.
  const valuationCurrency = priced.length > 0 ? currency : null

  return (
    <StatTiles
      stats={[
        { label: 'Positions', value: summary.positions },
        {
          label: 'Total cost basis',
          value: total(currency, (currency) => formatCurrency(summary.costBasis, currency)),
        },
        {
          label: 'Market value',
          value: total(valuationCurrency, (currency) =>
            formatCurrency(valuation.marketValue, currency),
          ),
        },
        {
          label: 'Unrealised P&L',
          value: total(valuationCurrency, (currency) => (
            <Profit amount={valuation.unrealisedPnl} currency={currency} />
          )),
        },
        {
          label: 'Realised P&L',
          value: total(currency, (currency) => (
            <Profit amount={summary.realisedPnl} currency={currency} />
          )),
        },
      ]}
    />
  )
}

/** A total, or a dash when there is no currency to show it in. */
function total(currency: string | null, show: (currency: string) => ReactNode): ReactNode {
  return currency === null ? NO_VALUE : show(currency)
}

export default HoldingsSummary
