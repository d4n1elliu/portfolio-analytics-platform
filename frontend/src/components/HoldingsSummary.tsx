import type { Holding } from '../api/types'
import { formatCurrency, formatProfit } from '../lib/format'
import { summariseHoldings } from '../lib/holdings'
import { profitColour } from '../lib/profit'
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
          value: currency ? formatCurrency(summary.costBasis, currency) : '—',
        },
        {
          label: 'Realised P&L',
          value: currency ? (
            <span className={profitColour(summary.realisedPnl)}>
              {formatProfit(summary.realisedPnl, currency)}
            </span>
          ) : (
            '—'
          ),
        },
      ]}
    />
  )
}

export default HoldingsSummary
