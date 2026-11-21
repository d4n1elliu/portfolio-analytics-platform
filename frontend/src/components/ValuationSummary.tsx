import { NO_VALUE, formatCurrency, formatPercent } from '../lib/format'
import { profitColour } from '../lib/profit'
import type { ProfitSummary, ValuationSummary as Summary } from '../lib/valuation'
import Profit from './Profit'
import StatTiles from './StatTiles'

interface ValuationSummaryProps {
  summary: Summary
  profit: ProfitSummary
  currency: string
}

function ValuationSummary({ summary, profit, currency }: ValuationSummaryProps) {
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
        {
          label: 'Realised P&L',
          value: <Profit amount={profit.realisedPnl} currency={currency} />,
        },
        {
          label: 'Total P&L',
          value: <Profit amount={profit.totalPnl} currency={currency} />,
        },
      ]}
    />
  )
}

export default ValuationSummary
