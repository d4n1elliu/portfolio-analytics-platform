// The page for one security: its position, price chart and trades.

import { useCallback, useState } from 'react'
import { useParams } from 'react-router'

import { getHolding } from '../api/holdings'
import { listSecurityPrices } from '../api/securities'
import { listTrades } from '../api/trades'
import type { Holding, TradeSortKey } from '../api/types'
import Card from '../components/Card'
import LoadError from '../components/LoadError'
import LoadState from '../components/LoadState'
import NotFoundNote from '../components/NotFoundNote'
import PageLayout from '../components/PageLayout'
import PriceChart from '../components/PriceChart'
import SecurityPosition from '../components/SecurityPosition'
import TradeTable from '../components/TradeTable'
import { SECURITY_TRADES_LIMIT } from '../config'
import { useApiQuery } from '../hooks/useApiQuery'
import { formatCount } from '../lib/format'
import { nextSort } from '../lib/sorting'
import { MUTED_TEXT } from '../lib/styles'
import { pricesAsAt } from '../lib/valuation'
import { NEWEST_FIRST, NO_TRADE_FILTERS } from '../lib/trades'
import { ROUTES } from '../routes'

function SecurityPage() {
  const ticker = (useParams().ticker ?? '').toUpperCase()

  const loadHolding = useCallback((signal: AbortSignal) => getHolding(ticker, signal), [ticker])
  const { state, reload } = useApiQuery(loadHolding)

  return (
    <PageLayout title={ticker}>
      {state.status === 'loading' && <p className={MUTED_TEXT}>Loading {ticker}…</p>}
      {state.status === 'error' && <LoadError message={state.message} onRetry={reload} />}
      {state.status === 'loaded' && state.data === null && (
        <NotFoundNote
          message={`No security has the ticker ${ticker}.`}
          backTo={ROUTES.holdings}
          backLabel="Back to Holdings"
        />
      )}
      {state.status === 'loaded' && state.data !== null && (
        <SecurityDetails key={ticker} holding={state.data} />
      )}
    </PageLayout>
  )
}

function SecurityDetails({ holding }: { holding: Holding }) {
  const { ticker, currency } = holding
  const [sort, setSort] = useState(NEWEST_FIRST)

  const loadPrices = useCallback(
    (signal: AbortSignal) => listSecurityPrices(ticker, signal),
    [ticker],
  )
  const loadTrades = useCallback(
    (signal: AbortSignal) =>
      listTrades(
        { filters: { ...NO_TRADE_FILTERS, ticker }, sort },
        { limit: SECURITY_TRADES_LIMIT, offset: 0 },
        signal,
      ),
    [ticker, sort],
  )
  const { state: prices, reload: reloadPrices } = useApiQuery(loadPrices)
  const { state: trades, reload: reloadTrades } = useApiQuery(loadTrades, {
    keepPreviousData: true,
  })
  const page = trades.status === 'loaded' ? trades.data : null

  return (
    <>
      <p className={MUTED_TEXT}>
        {holding.security_name} · {holding.sector} · {holding.asset_class} · {currency}
      </p>

      <SecurityPosition holding={holding} />

      <Card title="Closing price" aside={pricesAsAt(holding.price_date)}>
        <LoadState
          state={prices}
          onRetry={reloadPrices}
          loadingText="Loading prices…"
          emptyText="No prices are stored for this security yet."
          isEmpty={(loaded) => loaded.length === 0}
        >
          {(loaded) => (
            <PriceChart
              ticker={ticker}
              currency={currency}
              prices={loaded}
              trades={page?.items ?? []}
            />
          )}
        </LoadState>
      </Card>

      <Card
        title="Trades"
        padded={!page || page.total === 0}
        aside={page && page.total > 0 && tradeCount(page.items.length, page.total)}
      >
        <LoadState
          state={trades}
          onRetry={reloadTrades}
          loadingText="Loading trades…"
          emptyText="No trades yet."
          isEmpty={(loaded) => loaded.total === 0}
        >
          {(loaded) => (
            <TradeTable
              trades={loaded.items}
              sort={sort}
              onSort={(sortKey: TradeSortKey) => setSort(nextSort(sort, sortKey))}
            />
          )}
        </LoadState>
      </Card>
    </>
  )
}

function tradeCount(shown: number, total: number): string {
  const count = formatCount(total, 'trade', 'trades')
  return shown < total ? `Showing ${shown} of ${count}` : count
}

export default SecurityPage
