import type { Holding } from '../api/types'
import { NO_VALUE, formatCurrency } from '../lib/format'
import { summariseHoldings } from '../lib/holdings'
import Profit from './Profit'
import StatTiles from './StatTiles'

function HoldingsSummary({ holdings }: { holdings: Holding[] }) {
  const summary = summariseHoldings(holdings)
  // Null when the holdings mix currencies, so no total can be shown.
  const currency = summary.currency

  return (
    <StatTiles
      stats={[
        { label: 'Positions', value: summary.positions },
        {
          label: 'Total cost basis',
          value: currency ? formatCurrency(summary.costBasis, currency) : NO_VALUE,
        },
        {
          label: 'Realised P&L',
          value: currency ? <Profit amount={summary.realisedPnl} currency={currency} /> : NO_VALUE,
        },
      ]}
    />
  )
}

export default HoldingsSummary
