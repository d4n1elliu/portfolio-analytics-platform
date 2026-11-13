import { useCallback } from 'react'
import { Link } from 'react-router'

import { listHoldings } from '../api/holdings'
import Alert from '../components/Alert'
import Button from '../components/Button'
import Card from '../components/Card'
import HoldingsTable from '../components/HoldingsTable'
import OversoldWarning from '../components/OversoldWarning'
import PageLayout from '../components/PageLayout'
import { useApiQuery } from '../hooks/useApiQuery'
import { formatCount } from '../lib/format'
import { findOversold } from '../lib/holdings'
import { ROUTES } from '../routes'

function HoldingsPage() {
  const loadHoldings = useCallback(
    (signal: AbortSignal) => listHoldings({ includeClosed: false }, signal),
    [],
  )
  const { state, reload } = useApiQuery(loadHoldings)

  const holdings = state.status === 'loaded' ? state.data : null

  return (
    <PageLayout title="Holdings">
      {holdings && <OversoldWarning holdings={findOversold(holdings)} />}

      <Card
        title="Positions"
        padded={false}
        aside={
          holdings &&
          holdings.length > 0 &&
          formatCount(holdings.length, 'position', 'positions')
        }
      >
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
            No open positions.{' '}
            <Link to={ROUTES.trades} className="font-medium text-slate-900 underline">
              Import trades
            </Link>{' '}
            to get started.
          </p>
        )}

        {holdings && holdings.length > 0 && <HoldingsTable holdings={holdings} />}
      </Card>
    </PageLayout>
  )
}

export default HoldingsPage
