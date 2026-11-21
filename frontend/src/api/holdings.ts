import { request, requestOrNull } from './client'
import type { Holding } from './types'

interface HoldingsParams {
  includeClosed: boolean
  asOf?: string
}

/** Fetch the position in each security, ordered by ticker. */
export function listHoldings(params: HoldingsParams, signal?: AbortSignal): Promise<Holding[]> {
  const query = new URLSearchParams({ include_closed: String(params.includeClosed) })
  if (params.asOf) query.set('as_of', params.asOf)
  return request<Holding[]>(`/holdings?${query}`, { signal })
}

export function getHolding(ticker: string, signal?: AbortSignal): Promise<Holding | null> {
  return requestOrNull<Holding>(`/holdings/${encodeURIComponent(ticker)}`, { signal })
}
