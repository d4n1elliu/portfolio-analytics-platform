import { request } from './client'
import type { Holding } from './types'

interface HoldingsParams {
  includeClosed: boolean
  /** Date only, as "YYYY-MM-DD", for the positions at the end of that date. Leave out for today. */
  asOf?: string
}

/** Fetch the position in each security, ordered by ticker. */
export function listHoldings(params: HoldingsParams, signal?: AbortSignal): Promise<Holding[]> {
  const query = new URLSearchParams({ include_closed: String(params.includeClosed) })
  if (params.asOf) query.set('as_of', params.asOf)
  return request<Holding[]>(`/holdings?${query}`, { signal })
}
