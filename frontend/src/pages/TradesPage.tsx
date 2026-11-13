import { useCallback, useState } from 'react'

import { listSecurities } from '../api/securities'
import { TRADE_CSV_COLUMNS, importTrades, listTrades } from '../api/trades'
import Alert from '../components/Alert'
import Button from '../components/Button'
import Card from '../components/Card'
import CsvImportForm from '../components/CsvImportForm'
import PageLayout from '../components/PageLayout'
import Pagination from '../components/Pagination'
import TradeTable from '../components/TradeTable'
import { PAGE_SIZE } from '../config'
import { useApiQuery } from '../hooks/useApiQuery'
import { formatRange } from '../lib/format'

function TradesPage() {
  const [offset, setOffset] = useState(0)

  const loadTrades = useCallback(
    (signal: AbortSignal) => listTrades({ limit: PAGE_SIZE, offset }, signal),
    [offset],
  )
  const { state: trades, reload: reloadTrades } = useApiQuery(loadTrades)
  const { state: securities } = useApiQuery(listSecurities)

  function handleImported() {
    // New trades can fall anywhere in date order, so return to the first page.
    setOffset(0)
    reloadTrades()
  }

  const page = trades.status === 'loaded' ? trades.data : null

  return (
    <PageLayout title="Trades">
      <Card title="Import trades">
        <CsvImportForm
          upload={importTrades}
          singular="trade"
          plural="trades"
          onImported={handleImported}
        >
          <div className="space-y-1 text-sm text-slate-600">
            <p>
              Upload a CSV file with the columns{' '}
              <code className="rounded bg-slate-100 px-1 py-0.5 text-xs">
                {TRADE_CSV_COLUMNS.join(', ')}
              </code>
              .
            </p>
            {securities.status === 'loaded' && (
              <p>
                Known tickers: {securities.data.map((security) => security.ticker).join(', ')}.
              </p>
            )}
          </div>
        </CsvImportForm>
      </Card>

      <Card
        title="Trades"
        padded={false}
        aside={
          page && page.total > 0 && formatRange(page.offset, page.items.length, page.total)
        }
      >
        {trades.status === 'loading' && (
          <p className="px-6 pb-6 text-sm text-slate-500">Loading trades…</p>
        )}

        {trades.status === 'error' && (
          <div className="space-y-3 px-6 pb-6">
            <Alert variant="error">{trades.message}</Alert>
            <Button variant="secondary" onClick={reloadTrades}>
              Try again
            </Button>
          </div>
        )}

        {page && page.total === 0 && (
          <p className="px-6 pb-6 text-sm text-slate-500">
            No trades yet. Import a CSV file to get started.
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
