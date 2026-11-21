// Tests for the trade query string and the trade filters.

import { describe, expect, it } from 'vitest'

import { NEWEST_FIRST, NO_TRADE_FILTERS, hasTradeFilters } from '../lib/trades'
import { tradeQueryString } from './trades'

describe('tradeQueryString', () => {
  it('leaves out the filters that are not set', () => {
    const query = { filters: NO_TRADE_FILTERS, sort: NEWEST_FIRST }

    expect(tradeQueryString(query)).toBe('sort=trade_date&order=desc')
  })

  it('sends every filter, the order and the page', () => {
    const query = {
      filters: { ticker: 'BHP', side: 'SELL', dateFrom: '2026-01-01', dateTo: '2026-06-30' },
      sort: { key: 'quantity', direction: 'ascending' },
    } as const

    expect(tradeQueryString(query, { limit: 25, offset: 50 })).toBe(
      'ticker=BHP&side=SELL&date_from=2026-01-01&date_to=2026-06-30' +
        '&sort=quantity&order=asc&limit=25&offset=50',
    )
  })
})

describe('hasTradeFilters', () => {
  it('is true once any filter is set', () => {
    expect(hasTradeFilters(NO_TRADE_FILTERS)).toBe(false)
    expect(hasTradeFilters({ ...NO_TRADE_FILTERS, dateTo: '2026-06-30' })).toBe(true)
  })
})
