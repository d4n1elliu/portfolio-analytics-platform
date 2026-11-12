import { request, uploadFile } from './client'
import type { ImportResult, Page, Trade } from './types'

/** Columns of the trades CSV, in the order the backend documents them. */
export const TRADE_CSV_COLUMNS = ['trade_date', 'ticker', 'side', 'quantity', 'price', 'fees']

/** Fetch one page of trades, newest first. */
export function listTrades(
  params: { limit: number; offset: number },
  signal?: AbortSignal,
): Promise<Page<Trade>> {
  const query = new URLSearchParams({
    limit: String(params.limit),
    offset: String(params.offset),
  })
  return request<Page<Trade>>(`/trades?${query}`, { signal })
}

/** Upload a CSV of trades. Either every row is saved or none are. */
export function importTrades(file: File): Promise<ImportResult> {
  return uploadFile<ImportResult>('/trades/import', file)
}
