import { useCallback, useState } from 'react'

import { exportTrades, listImports, listTrades } from '../api/trades'
import type { TradeQuery } from '../api/trades'
import type { TradeSortKey } from '../api/types'
import Card from '../components/Card'
import DownloadButton from '../components/DownloadButton'
import ImportHistory from '../components/ImportHistory'
import LoadError from '../components/LoadError'
import PageLayout from '../components/PageLayout'
import Pagination from '../components/Pagination'
import RoleNote from '../components/RoleNote'
import TradeFilters from '../components/TradeFilters'
import TradeImport from '../components/TradeImport'
import TradeTable from '../components/TradeTable'
import { IMPORT_HISTORY_SIZE, PAGE_SIZE } from '../config'
import { useApiQuery } from '../hooks/useApiQuery'
import { useTickers } from '../hooks/useTickers'
import { useAuth } from '../lib/auth'
import { formatRange } from '../lib/format'
import { can } from '../lib/roles'
import { nextSort } from '../lib/sorting'
import { MUTED_TEXT } from '../lib/styles'
import { NEWEST_FIRST, NO_TRADE_FILTERS, hasTradeFilters } from '../lib/trades'

const EXPORT_FILE_NAME = 'trades.csv'

function loadLatestImports(signal: AbortSignal) {
  return listImports(IMPORT_HISTORY_SIZE, signal)
}

function TradesPage() {
  const [query, setQuery] = useState<TradeQuery>({ filters: NO_TRADE_FILTERS, sort: NEWEST_FIRST })
  const [offset, setOffset] = useState(0)

  const loadTrades = useCallback(
    (signal: AbortSignal) => listTrades(query, { limit: PAGE_SIZE, offset }, signal),
    [query, offset],
  )
  const { state: trades, reload: reloadTrades } = useApiQuery(loadTrades, {
    keepPreviousData: true,
  })
  const { state: imports, reload: reloadImports } = useApiQuery(loadLatestImports)
  const tickers = useTickers()
  const { state: auth } = useAuth()

  const user = auth.status === 'signedIn' ? auth.user : null
  const canImport = can(user, 'import_trades')
  const canExport = can(user, 'export_trades')
  const page = trades.status === 'loaded' ? trades.data : null
  const filtered = hasTradeFilters(query.filters)

  function showFromFirstPage(next: TradeQuery) {
    setQuery(next)
    setOffset(0)
  }

  function handleSort(sortKey: TradeSortKey) {
    showFromFirstPage({ ...query, sort: nextSort(query.sort, sortKey) })
  }

  function handleImported() {
    setOffset(0)
    reloadTrades()
    reloadImports()
  }

  return (
    <PageLayout title="Trades">
      {canImport && <TradeImport tickers={tickers} onImported={handleImported} />}
      {user && !canImport && (
        <RoleNote title="Import trades" role={user.role} can="view trades" cannot="import them" />
      )}

      <Card
        title="Trades"
        padded={false}
        aside={page && page.total > 0 && formatRange(page.offset, page.items.length, page.total)}
      >
        <div className="flex flex-wrap items-center justify-between gap-3 px-6 pb-4">
          <TradeFilters
            filters={query.filters}
            tickers={tickers}
            onChange={(filters) => showFromFirstPage({ ...query, filters })}
          />
          {canExport && (
            <DownloadButton
              label="Export CSV"
              fileName={EXPORT_FILE_NAME}
              download={() => exportTrades(query)}
            />
          )}
        </div>

        {trades.status === 'loading' && (
          <p className={`px-6 pb-6 ${MUTED_TEXT}`}>Loading trades…</p>
        )}

        {trades.status === 'error' && (
          <LoadError message={trades.message} onRetry={reloadTrades} className="px-6 pb-6" />
        )}

        {page && page.total === 0 && !filtered && (
          <p className={`px-6 pb-6 ${MUTED_TEXT}`}>
            No trades yet.{canImport && ' Import a CSV file to get started.'}
          </p>
        )}

        {page && page.total === 0 && filtered && (
          <p className={`px-6 pb-6 ${MUTED_TEXT}`}>No trades match the filters.</p>
        )}

        {page && page.total > 0 && (
          <>
            <TradeTable trades={page.items} sort={query.sort} onSort={handleSort} />
            <Pagination
              offset={offset}
              pageSize={PAGE_SIZE}
              total={page.total}
              onChange={setOffset}
            />
          </>
        )}
      </Card>

      <ImportHistory state={imports} onRetry={reloadImports} />
    </PageLayout>
  )
}

export default TradesPage
