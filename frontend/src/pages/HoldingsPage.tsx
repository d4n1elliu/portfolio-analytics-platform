import { useState } from 'react'
import { Link } from 'react-router'

import { listHoldings } from '../api/holdings'
import Alert from '../components/Alert'
import Button from '../components/Button'
import Card from '../components/Card'
import HoldingsFilters from '../components/HoldingsFilters'
import HoldingsSummary from '../components/HoldingsSummary'
import HoldingsTable from '../components/HoldingsTable'
import OversoldWarning from '../components/OversoldWarning'
import PageLayout from '../components/PageLayout'
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

  return (
    <PageLayout title="Holdings">
      {holdings && <OversoldWarning holdings={findOversold(holdings)} />}
      {holdings && <HoldingsSummary holdings={shown} />}

      <Card
        title="Positions"
        padded={false}
        aside={holdings && positionCount(shown.length, listed.length)}
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
          <p className="px-6 pb-6 text-sm text-slate-500">Loading holdings…</p>
        )}

        {state.status === 'error' && (
          <div className="space-y-3 px-6 pb-6">
            <Alert variant="error">{state.message}</Alert>
            <Button variant="secondary" onClick={reload}>
              Try again
            </Button>
          </div>
        )}

        {holdings && holdings.length === 0 && (
          <p className="px-6 pb-6 text-sm text-slate-500">
            No positions yet.{' '}
            <Link to={ROUTES.trades} className="font-medium text-slate-900 underline">
              Import trades
            </Link>{' '}
            to get started.
          </p>
        )}

        {holdings && holdings.length > 0 && listed.length === 0 && (
          <p className="px-6 pb-6 text-sm text-slate-500">
            No open positions. Tick "Show closed positions" to see the ones that have been sold.
          </p>
        )}

        {listed.length > 0 && shown.length === 0 && (
          <div className="space-y-3 px-6 pb-6">
            <p className="text-sm text-slate-500">No positions match the search and filters.</p>
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

/** "10 positions", or "3 of 10 positions" when filters hide some. */
function positionCount(shown: number, total: number): string {
  const count = formatCount(total, 'position', 'positions')
  return shown === total ? count : `${shown} of ${count}`
}

export default HoldingsPage
