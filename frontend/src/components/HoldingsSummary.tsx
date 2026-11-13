import type { Holding } from '../api/types'
import { formatCurrency, formatProfit } from '../lib/format'
import { summariseHoldings } from '../lib/holdings'
import { profitColour } from '../lib/profit'
import StatTiles from './StatTiles'

/** Headline figures for the holdings given: how many, what they cost, and profit taken. */
function HoldingsSummary({ holdings }: { holdings: Holding[] }) {
  const summary = summariseHoldings(holdings)
  // Amounts in different currencies cannot be added together.
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
