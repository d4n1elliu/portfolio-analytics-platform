import { describe, expect, it } from 'vitest'

import { makeHolding, makeUnpricedHolding } from '../testing/holdings'
import {
  countUnpriced,
  latestPriceDate,
  pricesAsAt,
  sectorAllocation,
  summariseProfit,
  summariseValuation,
  valuedHoldings,
} from './valuation'

describe('valuedHoldings', () => {
  it('leaves out a holding with no stored price', () => {
    const valued = valuedHoldings([makeHolding(), makeUnpricedHolding({ ticker: 'CBA' })])

    expect(valued.map((holding) => holding.ticker)).toEqual(['BHP'])
  })
})

describe('summariseValuation', () => {
  it('adds up the holdings and works out the return on cost', () => {
    const holdings = valuedHoldings([
      makeHolding({ cost_basis: '4000.00', market_value: '4500.00', unrealised_pnl: '500.00' }),
      makeHolding({ cost_basis: '1000.00', market_value: '900.00', unrealised_pnl: '-100.00' }),
    ])

    expect(summariseValuation(holdings)).toEqual({
      marketValue: 5400,
      unrealisedPnl: 400,
      unrealisedReturn: 0.08,
    })
  })

  it('has no return when the holdings cost nothing', () => {
    const holdings = valuedHoldings([makeHolding({ cost_basis: '0.00' })])

    expect(summariseValuation(holdings).unrealisedReturn).toBeNull()
  })
})

describe('summariseProfit', () => {
  it('counts the profit made on a closed position', () => {
    const open = makeHolding({ unrealised_pnl: '500.00', realised_pnl: '812.59' })
    const closed = makeUnpricedHolding({ quantity: '0.000000', realised_pnl: '-112.59' })

    expect(summariseProfit([open, closed])).toEqual({ realisedPnl: 700, totalPnl: 1200 })
  })

  it('adds no unrealised profit for a holding with no price', () => {
    const unpriced = makeUnpricedHolding({ realised_pnl: '10.10' })

    expect(summariseProfit([unpriced])).toEqual({ realisedPnl: 10.1, totalPnl: 10.1 })
  })
})

describe('countUnpriced', () => {
  it('counts open positions with no price, not closed ones', () => {
    const holdings = [
      makeHolding(),
      makeUnpricedHolding({ ticker: 'CBA' }),
      makeUnpricedHolding({ ticker: 'CSL', quantity: '0.000000' }),
    ]

    expect(countUnpriced(holdings)).toBe(1)
  })
})

describe('price dates', () => {
  it('finds the newest price date and skips holdings without one', () => {
    const holdings = [
      makeHolding({ price_date: '2026-11-12' }),
      makeHolding({ price_date: '2026-11-13' }),
      makeUnpricedHolding(),
    ]

    expect(latestPriceDate(holdings)).toBe('2026-11-13')
    expect(latestPriceDate([makeUnpricedHolding()])).toBeNull()
  })

  it('labels the price date, or says nothing without one', () => {
    expect(pricesAsAt('2026-11-13')).toBe('Prices as at 13 Nov 2026')
    expect(pricesAsAt(null)).toBe('')
  })
})

describe('sectorAllocation', () => {
  it('adds up each sector and lists the largest first', () => {
    const holdings = valuedHoldings([
      makeHolding({ sector: 'Materials', market_value: '1000.00' }),
      makeHolding({ sector: 'Financials', market_value: '2500.00' }),
      makeHolding({ sector: 'Materials', market_value: '1500.00' }),
    ])

    expect(sectorAllocation(holdings)).toEqual([
      { sector: 'Materials', marketValue: 2500, weight: 0.5 },
      { sector: 'Financials', marketValue: 2500, weight: 0.5 },
    ])
  })

  it('gives every sector no weight when nothing has any value', () => {
    const holdings = valuedHoldings([makeHolding({ market_value: '0.00' })])

    expect(sectorAllocation(holdings)).toEqual([{ sector: 'Materials', marketValue: 0, weight: 0 }])
  })
})
