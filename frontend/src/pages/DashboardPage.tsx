import { Link } from 'react-router'

import { listHoldings } from '../api/holdings'
import type { Holding } from '../api/types'
import Alert from '../components/Alert'
import Card from '../components/Card'
import LoadError from '../components/LoadError'
import PageLayout from '../components/PageLayout'
import RankedBarChart from '../components/RankedBarChart'
import type { RankedBar } from '../components/RankedBarChart'
import ValuationSummary from '../components/ValuationSummary'
import { useApiQuery } from '../hooks/useApiQuery'
import { formatCount, formatCurrency, formatDate, formatPercent, formatProfit } from '../lib/format'
import { sectorAllocation, summariseValuation, valuedHoldings } from '../lib/valuation'
import type { SectorShare, ValuedHolding } from '../lib/valuation'
import { ROUTES } from '../routes'

function loadOpenHoldings(signal: AbortSignal) {
  return listHoldings({ includeClosed: false }, signal)
}

function DashboardPage() {
  const { state, reload } = useApiQuery(loadOpenHoldings)

  return (
    <PageLayout title="Dashboard">
      {state.status === 'loading' && <p className="text-sm text-slate-500">Loading dashboard…</p>}
      {state.status === 'error' && <LoadError message={state.message} onRetry={reload} />}
      {state.status === 'loaded' && <Valuation openHoldings={state.data} />}
    </PageLayout>
  )
}

function Valuation({ openHoldings }: { openHoldings: Holding[] }) {
  const holdings = valuedHoldings(openHoldings)
  const unpricedCount = openHoldings.length - holdings.length
  const summary = summariseValuation(holdings)
  const currency = summary.currency

  if (holdings.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No priced positions yet.{' '}
        <Link to={ROUTES.trades} className="font-medium text-slate-900 underline">
          Import trades
        </Link>{' '}
        to get started.
      </p>
    )
  }
  if (currency === null) {
    return (
      <Alert variant="warning">
        The positions use more than one currency, so they cannot be added together.
      </Alert>
    )
  }

  const pricesAsAt = pricedAsAt(holdings)

  return (
    <>
      {unpricedCount > 0 && (
        <Alert variant="warning">
          {formatCount(unpricedCount, 'position has', 'positions have')} no stored price and{' '}
          {unpricedCount === 1 ? 'is' : 'are'} left out.
        </Alert>
      )}

      <ValuationSummary summary={summary} currency={currency} />

      <Card title="Sector allocation" aside={pricesAsAt}>
        <RankedBarChart
          label="Share of market value in each sector"
          bars={sectorAllocation(holdings).map((share) => sectorBar(share, currency))}
        />
      </Card>

      <Card title="Unrealised P&L by holding" aside={pricesAsAt}>
        <RankedBarChart
          label="Unrealised profit or loss of each holding"
          bars={byLargestGain(holdings).map(pnlBar)}
        />
      </Card>
    </>
  )
}

function sectorBar(share: SectorShare, currency: string): RankedBar {
  return {
    name: share.sector,
    value: share.weight,
    valueLabel: formatPercent(share.weight),
    tooltipLabel: `${formatPercent(share.weight)} · ${formatCurrency(share.marketValue, currency)}`,
  }
}

function pnlBar(holding: ValuedHolding): RankedBar {
  return {
    name: holding.ticker,
    value: Number(holding.unrealised_pnl),
    valueLabel: formatProfit(holding.unrealised_pnl, holding.currency),
  }
}

function byLargestGain(holdings: ValuedHolding[]): ValuedHolding[] {
  return [...holdings].sort((a, b) => Number(b.unrealised_pnl) - Number(a.unrealised_pnl))
}

/** "Prices as at 13 Nov 2026", using the most recent price date. */
function pricedAsAt(holdings: ValuedHolding[]): string {
  const latest = holdings.map((holding) => holding.price_date ?? '').sort().at(-1)
  return latest ? `Prices as at ${formatDate(latest)}` : ''
}

export default DashboardPage
