import { ApiError, request } from './client'
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

const NOT_FOUND = 404

export async function getHolding(ticker: string, signal?: AbortSignal): Promise<Holding | null> {
  try {
    return await request<Holding>(`/holdings/${encodeURIComponent(ticker)}`, { signal })
  } catch (error) {
    if (error instanceof ApiError && error.status === NOT_FOUND) return null
    throw error
  }
}
