import { describe, expect, it } from 'vitest'

import type { GrowthPoint } from '../api/types'
import { returnSeries } from './performance'

const GROWTH: GrowthPoint[] = [
  { date: '2026-11-11', portfolio: '1.100000' },
  { date: '2026-11-12', portfolio: '1.210000' },
  { date: '2026-11-13', portfolio: '1.331000' },
]

function rounded(values: number[]): number[] {
  return values.map((value) => Number(value.toFixed(6)))
}

describe('returnSeries', () => {
  it('starts a period at zero on its start date', () => {
    const series = returnSeries(GROWTH, {
      period: '1m',
      portfolio_return: '0.100000',
      start_date: '2026-11-12',
    })

    expect(series.dates).toEqual(['2026-11-12', '2026-11-13'])
    expect(rounded(series.returns)).toEqual([0, 0.1])
  })

  it('counts the first day when measured since inception', () => {
    const series = returnSeries(GROWTH, {
      period: 'inception',
      portfolio_return: '0.331000',
      start_date: '2026-11-11',
    })

    expect(rounded(series.returns)).toEqual([0.1, 0.21, 0.331])
  })

  it('is empty when the period has no return', () => {
    const noReturn = { period: '1y', portfolio_return: null, start_date: null } as const

    expect(returnSeries(GROWTH, noReturn)).toEqual({ dates: [], returns: [] })
    expect(returnSeries(GROWTH, undefined)).toEqual({ dates: [], returns: [] })
  })
})
