// Tests for placing trades on a price chart.

import { describe, expect, it } from 'vitest'

import type { SecurityPrice, Trade, TradeSide } from '../api/types'
import { tradeMarkers } from './tradeMarkers'

const PRICES: SecurityPrice[] = [
  { date: '2026-11-13', close: '41.000000' },
  { date: '2026-11-16', close: '42.500000' },
]

function trade(tradeDate: string, side: TradeSide = 'BUY'): Trade {
  return {
    id: 1,
    trade_date: tradeDate,
    ticker: 'BHP',
    security_name: 'BHP Group Limited',
    currency: 'AUD',
    side,
    quantity: '400.000000',
    price: '41.850000',
    fees: '29.95',
    created_at: '2026-11-16T03:00:00Z',
  }
}

describe('tradeMarkers', () => {
  it("puts a trade on its date's closing price and describes it", () => {
    expect(tradeMarkers([trade('2026-11-16', 'SELL')], PRICES)).toEqual([
      { date: '2026-11-16', value: 42.5, label: 'Sold 400 at $41.85 on 16 Nov 2026', isSell: true },
    ])
  })

  it('uses the latest earlier price for a trade on a day with none', () => {
    const [marker] = tradeMarkers([trade('2026-11-14')], PRICES)

    expect(marker.date).toBe('2026-11-13')
    expect(marker.value).toBe(41)
    expect(marker.label).toBe('Bought 400 at $41.85 on 14 Nov 2026')
  })

  it('leaves out a trade from before the first price', () => {
    expect(tradeMarkers([trade('2026-11-12')], PRICES)).toEqual([])
  })

  it('lists the markers oldest first, whatever order the trades are in', () => {
    const markers = tradeMarkers([trade('2026-11-16'), trade('2026-11-13')], PRICES)

    expect(markers.map((marker) => marker.date)).toEqual(['2026-11-13', '2026-11-16'])
  })
})
