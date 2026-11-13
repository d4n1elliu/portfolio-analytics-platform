import { request } from './client'
import type { Holding } from './types'

/** Fetch the position in each security, ordered by ticker. */
export function listHoldings(
  params: { includeClosed: boolean },
  signal?: AbortSignal,
): Promise<Holding[]> {
  const query = new URLSearchParams({ include_closed: String(params.includeClosed) })
  return request<Holding[]>(`/holdings?${query}`, { signal })
}
