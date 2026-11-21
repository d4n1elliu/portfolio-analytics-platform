// Tests for the return series shown on the performance chart.

import { describe, expect, it } from 'vitest'

import type { GrowthPoint, PeriodReturn } from '../api/types'
import { excessReturn, returnSeries } from './performance'

const GROWTH: GrowthPoint[] = [
  { date: '2026-11-11', portfolio: '1.100000', benchmark: null },
  { date: '2026-11-12', portfolio: '1.210000', benchmark: '1.000000' },
  { date: '2026-11-13', portfolio: '1.331000', benchmark: '1.050000' },
]

function rounded(values: number[]): number[] {
  return values.map((value) => Number(value.toFixed(6)))
}

function period(fields: Partial<PeriodReturn>): PeriodReturn {
  return {
    period: '1m',
    portfolio_return: '0.100000',
    start_date: '2026-11-12',
    benchmark_return: '0.050000',
    ...fields,
  }
}

describe('returnSeries', () => {
  it('starts a period at zero on its start date', () => {
    const series = returnSeries(GROWTH, period({}))

    expect(series.dates).toEqual(['2026-11-12', '2026-11-13'])
    expect(rounded(series.returns)).toEqual([0, 0.1])
    expect(rounded(series.benchmarkReturns)).toEqual([0, 0.05])
  })

  it('counts the first day when measured since inception', () => {
    const series = returnSeries(GROWTH, period({ period: 'inception', start_date: '2026-11-11' }))

    expect(rounded(series.returns)).toEqual([0.1, 0.21, 0.331])
  })

  it('has no benchmark line when the benchmark has no price at the start', () => {
    const series = returnSeries(GROWTH, period({ period: 'inception', start_date: '2026-11-11' }))

    expect(series.benchmarkReturns).toEqual([])
  })

  it('is empty when the period has no return', () => {
    const empty = { dates: [], returns: [], benchmarkReturns: [] }

    expect(returnSeries(GROWTH, period({ portfolio_return: null, start_date: null }))).toEqual(
      empty,
    )
    expect(returnSeries(GROWTH, undefined)).toEqual(empty)
  })
})

describe('excessReturn', () => {
  it('is how far the portfolio is above the benchmark', () => {
    expect(excessReturn(period({}))).toBeCloseTo(0.05)
    expect(excessReturn(period({ portfolio_return: '0.010000' }))).toBeCloseTo(-0.04)
  })

  it('is missing when either return is', () => {
    expect(excessReturn(period({ benchmark_return: null }))).toBeNull()
    expect(excessReturn(period({ portfolio_return: null }))).toBeNull()
    expect(excessReturn(undefined)).toBeNull()
  })
})
