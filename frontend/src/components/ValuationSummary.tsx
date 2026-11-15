import { NO_VALUE, formatCurrency, formatPercent } from '../lib/format'
import { profitColour } from '../lib/profit'
import type { ValuationSummary as Summary } from '../lib/valuation'
import Profit from './Profit'
import StatTiles from './StatTiles'

function ValuationSummary({ summary, currency }: { summary: Summary; currency: string }) {
  const colour = profitColour(summary.unrealisedPnl)

  return (
    <StatTiles
      stats={[
        { label: 'Market value', value: formatCurrency(summary.marketValue, currency) },
        {
          label: 'Unrealised P&L',
          value: <Profit amount={summary.unrealisedPnl} currency={currency} />,
        },
        {
          label: 'Unrealised return',
          value:
            summary.unrealisedReturn === null ? (
              NO_VALUE
            ) : (
              <span className={colour}>{formatPercent(summary.unrealisedReturn)}</span>
            ),
        },
      ]}
    />
  )
}

export default ValuationSummary
