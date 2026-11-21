import { request } from './client'
import type { Security, SecurityPrice } from './types'

/** Fetch every security, ordered by ticker. */
export function listSecurities(signal?: AbortSignal): Promise<Security[]> {
  return request<Security[]>('/securities', { signal })
}

/** Fetch the closing prices of one security, oldest first. */
export function listSecurityPrices(ticker: string, signal?: AbortSignal): Promise<SecurityPrice[]> {
  return request<SecurityPrice[]>(`/securities/${encodeURIComponent(ticker)}/prices`, { signal })
}
