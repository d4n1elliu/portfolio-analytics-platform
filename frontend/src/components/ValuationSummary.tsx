import { formatCurrency, formatPercent, formatProfit } from '../lib/format'
import { profitColour } from '../lib/profit'
import type { ValuationSummary as Summary } from '../lib/valuation'
import StatTiles from './StatTiles'

function ValuationSummary({ summary, currency }: { summary: Summary; currency: string }) {
  const colour = profitColour(summary.unrealisedPnl)

  return (
    <StatTiles
      stats={[
        { label: 'Market value', value: formatCurrency(summary.marketValue, currency) },
        {
          label: 'Unrealised P&L',
          value: <span className={colour}>{formatProfit(summary.unrealisedPnl, currency)}</span>,
        },
        {
          label: 'Unrealised return',
          value:
            summary.unrealisedReturn === null ? (
              '—'
            ) : (
              <span className={colour}>{formatPercent(summary.unrealisedReturn)}</span>
            ),
        },
      ]}
    />
  )
}

export default ValuationSummary
