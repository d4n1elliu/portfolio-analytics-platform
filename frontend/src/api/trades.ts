import type { SortBy } from '../lib/sorting'
import type { TradeFilters } from '../lib/trades'
import { request, requestFile, uploadFile } from './client'
import type { ImportBatch, ImportResult, Page, Trade, TradeSortKey } from './types'

/** Columns of the trades CSV, in the order the backend documents them. */
export const TRADE_CSV_COLUMNS = ['trade_date', 'ticker', 'side', 'quantity', 'price', 'fees']

/** Which trades to ask for, and in what order. */
export interface TradeQuery {
  filters: TradeFilters
  sort: SortBy<TradeSortKey>
}

interface PageParams {
  limit: number
  offset: number
}

/** The query string for a trade query. A filter that is not set is left out. */
export function tradeQueryString(query: TradeQuery, page?: PageParams): string {
  const { filters, sort } = query
  const params = {
    ticker: filters.ticker,
    side: filters.side,
    date_from: filters.dateFrom,
    date_to: filters.dateTo,
    sort: sort.key,
    order: sort.direction === 'ascending' ? 'asc' : 'desc',
    limit: page ? String(page.limit) : '',
    offset: page ? String(page.offset) : '',
  }
  const set = Object.entries(params).filter(([, value]) => value !== '')
  return new URLSearchParams(set).toString()
}

/** Fetch one page of the trades that match. */
export function listTrades(
  query: TradeQuery,
  page: PageParams,
  signal?: AbortSignal,
): Promise<Page<Trade>> {
  return request<Page<Trade>>(`/trades?${tradeQueryString(query, page)}`, { signal })
}

/** Fetch every trade that matches as a CSV file. */
export function exportTrades(query: TradeQuery): Promise<Blob> {
  return requestFile(`/trades/export?${tradeQueryString(query)}`)
}

/** Upload a CSV of trades. Either every row is saved or none are. */
export function importTrades(file: File): Promise<ImportResult> {
  return uploadFile<ImportResult>('/trades/import', file)
}

/** Fetch the latest imports, newest first. */
export function listImports(limit: number, signal?: AbortSignal): Promise<Page<ImportBatch>> {
  return request<Page<ImportBatch>>(`/trades/imports?limit=${limit}`, { signal })
}
