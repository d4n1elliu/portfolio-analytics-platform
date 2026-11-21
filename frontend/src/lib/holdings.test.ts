// Tests for filtering, selecting and adding up holdings.

import { describe, expect, it } from 'vitest'

import { makeHolding } from '../testing/holdings'
import {
  NO_FILTERS,
  assetClassesOf,
  commonCurrency,
  countClosed,
  filterHoldings,
  findOversold,
  hasFilters,
  sectorsOf,
  selectByStatus,
  summariseHoldings,
  sumMoney,
} from './holdings'

const open = makeHolding({ ticker: 'BHP' })
const closed = makeHolding({ ticker: 'CBA', quantity: '0.000000' })
const oversold = makeHolding({
  ticker: 'TLS',
  quantity: '0.000000',
  oversold_quantity: '50.000000',
})

function tickers(holdings: { ticker: string }[]): string[] {
  return holdings.map((holding) => holding.ticker)
}

describe('open, closed and oversold positions', () => {
  it('hides closed positions until they are asked for', () => {
    expect(tickers(selectByStatus([open, closed], false))).toEqual(['BHP'])
    expect(tickers(selectByStatus([open, closed], true))).toEqual(['BHP', 'CBA'])
  })

  it('always lists an oversold position', () => {
    expect(tickers(selectByStatus([open, closed, oversold], false))).toEqual(['BHP', 'TLS'])
    expect(tickers(findOversold([open, closed, oversold]))).toEqual(['TLS'])
  })

  it('counts the positions that are hidden', () => {
    expect(countClosed([open, closed, oversold])).toBe(1)
  })
})

describe('filterHoldings', () => {
  const holdings = [
    makeHolding({ ticker: 'BHP', security_name: 'BHP Group Limited', sector: 'Materials' }),
    makeHolding({ ticker: 'CBA', security_name: 'Commonwealth Bank', sector: 'Financials' }),
    makeHolding({ ticker: 'VAS', security_name: 'Vanguard Shares', asset_class: 'ETF' }),
  ]

  it('searches the ticker and the name, ignoring case and outer spaces', () => {
    expect(tickers(filterHoldings(holdings, { ...NO_FILTERS, search: ' cba ' }))).toEqual(['CBA'])
    expect(tickers(filterHoldings(holdings, { ...NO_FILTERS, search: 'vanguard' }))).toEqual([
      'VAS',
    ])
  })

  it('requires every filter to match', () => {
    const filters = { search: 'b', sector: 'Financials', assetClass: 'Equity' }

    expect(tickers(filterHoldings(holdings, filters))).toEqual(['CBA'])
  })

  it('knows whether any filter is set', () => {
    expect(hasFilters(NO_FILTERS)).toBe(false)
    expect(hasFilters({ ...NO_FILTERS, search: '  ' })).toBe(false)
    expect(hasFilters({ ...NO_FILTERS, sector: 'Materials' })).toBe(true)
  })

  it('lists each sector and asset class once, in order', () => {
    expect(sectorsOf(holdings)).toEqual(['Financials', 'Materials'])
    expect(assetClassesOf(holdings)).toEqual(['Equity', 'ETF'])
  })
})

describe('totals', () => {
  it('adds money without rounding errors', () => {
    expect(sumMoney(['0.10', '0.20'])).toBe(0.3)
  })

  it('adds up the cost basis and realised profit', () => {
    const summary = summariseHoldings([
      makeHolding({ cost_basis: '4000.00', realised_pnl: '812.59' }),
      makeHolding({ cost_basis: '1000.10', realised_pnl: '-12.59' }),
    ])

    expect(summary).toEqual({ positions: 2, costBasis: 5000.1, realisedPnl: 800, currency: 'AUD' })
  })

  it('has no currency when the holdings mix them, or when there are none', () => {
    expect(commonCurrency([makeHolding(), makeHolding({ currency: 'USD' })])).toBeNull()
    expect(commonCurrency([])).toBeNull()
  })
})
