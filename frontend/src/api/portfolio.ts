import { request } from './client'
import type { PortfolioHistoryPoint, PortfolioPerformance } from './types'

/** Fetch the value of the portfolio on each priced date, oldest first. */
export function listPortfolioHistory(signal?: AbortSignal): Promise<PortfolioHistoryPoint[]> {
  return request<PortfolioHistoryPoint[]>('/portfolio/history', { signal })
}

/** Fetch the time-weighted return of the portfolio over each period. */
export function getPortfolioPerformance(signal?: AbortSignal): Promise<PortfolioPerformance> {
  return request<PortfolioPerformance>('/portfolio/performance', { signal })
}
