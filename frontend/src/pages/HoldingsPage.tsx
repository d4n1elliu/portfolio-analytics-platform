import { useState } from 'react'
import { Link } from 'react-router'

import { listHoldings } from '../api/holdings'
import Button from '../components/Button'
import Card from '../components/Card'
import HoldingsFilters from '../components/HoldingsFilters'
import HoldingsSummary from '../components/HoldingsSummary'
import HoldingsTable from '../components/HoldingsTable'
import LoadError from '../components/LoadError'
import OversoldWarning from '../components/OversoldWarning'
import PageLayout from '../components/PageLayout'
import StalePriceWarning from '../components/StalePriceWarning'
import { useApiQuery } from '../hooks/useApiQuery'
import { formatCount } from '../lib/format'
import {
  NO_FILTERS,
  assetClassesOf,
  countClosed,
  filterHoldings,
  findOversold,
  hasFilters,
  sectorsOf,
  selectByStatus,
} from '../lib/holdings'
import { MUTED_TEXT } from '../lib/styles'
import { latestPriceDate, pricesAsAt } from '../lib/valuation'
import { ROUTES } from '../routes'

/** Every position is fetched once. Closed ones are hidden in the browser. */
function loadAllHoldings(signal: AbortSignal) {
  return listHoldings({ includeClosed: true }, signal)
}

function HoldingsPage() {
  const [showClosed, setShowClosed] = useState(false)
  const [filters, setFilters] = useState(NO_FILTERS)

  const { state, reload } = useApiQuery(loadAllHoldings, { keepPreviousData: true })

  const holdings = state.status === 'loaded' ? state.data : null
  const listed = holdings ? selectByStatus(holdings, showClosed) : []
  const shown = filterHoldings(listed, filters)
  const priceDate = holdings ? latestPriceDate(holdings) : null

  return (
    <PageLayout title="Holdings">
      {holdings && <OversoldWarning holdings={findOversold(holdings)} />}
      <StalePriceWarning priceDate={priceDate} />
      {holdings && <HoldingsSummary holdings={shown} />}

      <Card
        title="Positions"
        padded={false}
        aside={holdings && cardAside(shown.length, listed.length, priceDate)}
      >
        <HoldingsFilters
          filters={filters}
          sectors={holdings ? sectorsOf(holdings) : []}
          assetClasses={holdings ? assetClassesOf(holdings) : []}
          showClosed={showClosed}
          closedCount={holdings ? countClosed(holdings) : 0}
          onFiltersChange={setFilters}
          onShowClosedChange={setShowClosed}
        />

        {state.status === 'loading' && (
          <p className={`px-6 pb-6 ${MUTED_TEXT}`}>Loading holdings…</p>
        )}

        {state.status === 'error' && (
          <LoadError message={state.message} onRetry={reload} className="px-6 pb-6" />
        )}

        {holdings && holdings.length === 0 && (
          <p className={`px-6 pb-6 ${MUTED_TEXT}`}>
            No positions yet.{' '}
            <Link to={ROUTES.trades} className="font-medium text-slate-900 underline">
              Import trades
            </Link>{' '}
            to get started.
          </p>
        )}

        {holdings && holdings.length > 0 && listed.length === 0 && (
          <p className={`px-6 pb-6 ${MUTED_TEXT}`}>
            No open positions. Tick "Show closed positions" to see the ones that have been sold.
          </p>
        )}

        {listed.length > 0 && shown.length === 0 && (
          <div className="space-y-3 px-6 pb-6">
            <p className={MUTED_TEXT}>No positions match the search and filters.</p>
            {hasFilters(filters) && (
              <Button variant="secondary" onClick={() => setFilters(NO_FILTERS)}>
                Clear filters
              </Button>
            )}
          </div>
        )}

        {shown.length > 0 && <HoldingsTable holdings={shown} />}
      </Card>
    </PageLayout>
  )
}

/** "10 positions · Prices as at 13 Nov 2026". The date is left out when there are no prices. */
function cardAside(shown: number, total: number, priceDate: string | null): string {
  const parts = [positionCount(shown, total), pricesAsAt(priceDate)]
  return parts.filter((part) => part !== '').join(' · ')
}

/** "10 positions", or "3 of 10 positions" when filters hide some. */
function positionCount(shown: number, total: number): string {
  const count = formatCount(total, 'position', 'positions')
  return shown === total ? count : `${shown} of ${count}`
}

export default HoldingsPage
