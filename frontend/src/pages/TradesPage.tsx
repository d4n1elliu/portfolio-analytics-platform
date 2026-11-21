import { useCallback, useState } from 'react'

import { listTrades } from '../api/trades'
import Card from '../components/Card'
import LoadError from '../components/LoadError'
import PageLayout from '../components/PageLayout'
import Pagination from '../components/Pagination'
import TradeImport from '../components/TradeImport'
import TradeImportNotAllowed from '../components/TradeImportNotAllowed'
import TradeTable from '../components/TradeTable'
import { PAGE_SIZE } from '../config'
import { useApiQuery } from '../hooks/useApiQuery'
import { useAuth } from '../lib/auth'
import { formatRange } from '../lib/format'
import { canImportTrades } from '../lib/roles'
import { MUTED_TEXT } from '../lib/styles'

function TradesPage() {
  const [offset, setOffset] = useState(0)

  const loadTrades = useCallback(
    (signal: AbortSignal) => listTrades({ limit: PAGE_SIZE, offset }, signal),
    [offset],
  )
  const { state: trades, reload: reloadTrades } = useApiQuery(loadTrades)
  const { state: auth } = useAuth()
  const role = auth.status === 'signedIn' ? auth.user.role : null
  const canImport = role !== null && canImportTrades(role)

  function handleImported() {
    // New trades can fall anywhere in date order, so return to the first page.
    setOffset(0)
    reloadTrades()
  }

  const page = trades.status === 'loaded' ? trades.data : null

  return (
    <PageLayout title="Trades">
      {canImport && <TradeImport onImported={handleImported} />}
      {role && !canImport && <TradeImportNotAllowed role={role} />}

      <Card
        title="Trades"
        padded={false}
        aside={page && page.total > 0 && formatRange(page.offset, page.items.length, page.total)}
      >
        {trades.status === 'loading' && (
          <p className={`px-6 pb-6 ${MUTED_TEXT}`}>Loading trades…</p>
        )}

        {trades.status === 'error' && (
          <LoadError message={trades.message} onRetry={reloadTrades} className="px-6 pb-6" />
        )}

        {page && page.total === 0 && (
          <p className={`px-6 pb-6 ${MUTED_TEXT}`}>
            No trades yet.{canImport && ' Import a CSV file to get started.'}
          </p>
        )}

        {page && page.total > 0 && (
          <>
            <TradeTable trades={page.items} />
            <Pagination
              offset={offset}
              pageSize={PAGE_SIZE}
              total={page.total}
              onChange={setOffset}
            />
          </>
        )}
      </Card>
    </PageLayout>
  )
}

export default TradesPage
