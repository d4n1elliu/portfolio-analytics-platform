// The filters and default order of the trades table.

import type { TradeSide, TradeSortKey } from '../api/types'
import type { SortBy } from './sorting'

export interface TradeFilters {
  ticker: string
  side: TradeSide | ''
  dateFrom: string
  dateTo: string
}

export const NO_TRADE_FILTERS: TradeFilters = { ticker: '', side: '', dateFrom: '', dateTo: '' }

export const NEWEST_FIRST: SortBy<TradeSortKey> = { key: 'trade_date', direction: 'descending' }

export const TRADE_SIDES: TradeSide[] = ['BUY', 'SELL']

export function hasTradeFilters(filters: TradeFilters): boolean {
  return Object.values(filters).some((value) => value !== '')
}
