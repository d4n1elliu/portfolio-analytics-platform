import { Link } from 'react-router'

import { listHoldings } from '../api/holdings'
import type { Holding } from '../api/types'
import Alert from '../components/Alert'
import Card from '../components/Card'
import LoadError from '../components/LoadError'
import PageLayout from '../components/PageLayout'
import PortfolioHistory from '../components/PortfolioHistory'
import RankedBarChart from '../components/RankedBarChart'
import type { RankedBar } from '../components/RankedBarChart'
import ValuationSummary from '../components/ValuationSummary'
import { useApiQuery } from '../hooks/useApiQuery'
import { formatCount, formatCurrency, formatPercent, formatProfit } from '../lib/format'
import { MUTED_TEXT, TEXT_LINK } from '../lib/styles'
import {
  latestPriceDate,
  pricesAsAt,
  sectorAllocation,
  summariseValuation,
  valuedHoldings,
} from '../lib/valuation'
import type { SectorShare, ValuedHolding } from '../lib/valuation'
import { ROUTES } from '../routes'

function loadOpenHoldings(signal: AbortSignal) {
  return listHoldings({ includeClosed: false }, signal)
}

function DashboardPage() {
  const { state, reload } = useApiQuery(loadOpenHoldings)

  return (
    <PageLayout title="Dashboard">
      {state.status === 'loading' && <p className={MUTED_TEXT}>Loading dashboard…</p>}
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
      <p className={MUTED_TEXT}>
        No priced positions yet.{' '}
        <Link to={ROUTES.trades} className={TEXT_LINK}>
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

  const priceDateLabel = pricesAsAt(latestPriceDate(holdings))

  return (
    <>
      {unpricedCount > 0 && (
        <Alert variant="warning">
          {formatCount(unpricedCount, 'position has', 'positions have')} no stored price and{' '}
          {unpricedCount === 1 ? 'is' : 'are'} left out.
        </Alert>
      )}

      <ValuationSummary summary={summary} currency={currency} />

      <PortfolioHistory currency={currency} />

      <Card title="Sector allocation" aside={priceDateLabel}>
        <RankedBarChart
          label="Share of market value in each sector"
          bars={sectorAllocation(holdings).map((share) => sectorBar(share, currency))}
        />
      </Card>

      <Card title="Unrealised P&L by holding" aside={priceDateLabel}>
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

export default DashboardPage
