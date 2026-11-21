import type { TradeSide, TradeSortKey } from '../api/types'
import type { SortBy } from './sorting'

export interface TradeFilters {
  /** A ticker to show, or '' for all. */
  ticker: string
  /** A side to show, or '' for both. */
  side: TradeSide | ''
  /** Date only, as "YYYY-MM-DD", or '' for no limit. Both dates are included. */
  dateFrom: string
  dateTo: string
}

export const NO_TRADE_FILTERS: TradeFilters = { ticker: '', side: '', dateFrom: '', dateTo: '' }

export const NEWEST_FIRST: SortBy<TradeSortKey> = { key: 'trade_date', direction: 'descending' }

export const TRADE_SIDES: TradeSide[] = ['BUY', 'SELL']

export function hasTradeFilters(filters: TradeFilters): boolean {
  return Object.values(filters).some((value) => value !== '')
}
