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
          value: currency ? formatCurrency(summary.costBasis, currency) : NO_VALUE,
        },
        {
          label: 'Market value',
          value: valuationCurrency
            ? formatCurrency(valuation.marketValue, valuationCurrency)
            : NO_VALUE,
        },
        {
          label: 'Unrealised P&L',
          value: valuationCurrency ? (
            <Profit amount={valuation.unrealisedPnl} currency={valuationCurrency} />
          ) : (
            NO_VALUE
          ),
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
