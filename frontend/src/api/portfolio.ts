import { request } from './client'
import type { PortfolioHistoryPoint } from './types'

/** Fetch the value of the portfolio on each priced date, oldest first. */
export function listPortfolioHistory(signal?: AbortSignal): Promise<PortfolioHistoryPoint[]> {
  return request<PortfolioHistoryPoint[]>('/portfolio/history', { signal })
}
