// @vitest-environment jsdom
// Tests for useSortedRows.

import { act, renderHook } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { useSortedRows } from './useSortedRows'

interface Row {
  ticker: string
  weight: number | null
}

const ROWS: Row[] = [
  { ticker: 'CBA', weight: 0.5 },
  { ticker: 'VAS', weight: null },
  { ticker: 'BHP', weight: 0.2 },
  { ticker: 'bhp10', weight: 0.3 },
]

const COLUMNS = [
  { header: 'Ticker', sortValue: (row: Row) => row.ticker },
  { header: 'Weight', sortValue: (row: Row) => row.weight },
  { header: 'Notes' },
]

function sortedBy(...headers: string[]) {
  const { result } = renderHook(() => useSortedRows(ROWS, COLUMNS))
  for (const header of headers) act(() => result.current.toggleSort(header))
  return result.current
}

function tickers(rows: Row[]): string[] {
  return rows.map((row) => row.ticker)
}

describe('useSortedRows', () => {
  it('keeps the given order until a column is chosen', () => {
    expect(sortedBy().sortedRows).toBe(ROWS)
  })

  it('sorts text ignoring case, and reverses on the second click', () => {
    expect(tickers(sortedBy('Ticker').sortedRows)).toEqual(['BHP', 'bhp10', 'CBA', 'VAS'])
    expect(tickers(sortedBy('Ticker', 'Ticker').sortedRows)).toEqual(['VAS', 'CBA', 'bhp10', 'BHP'])
  })

  it('keeps rows with no value last in both directions', () => {
    expect(tickers(sortedBy('Weight').sortedRows)).toEqual(['BHP', 'bhp10', 'CBA', 'VAS'])
    expect(tickers(sortedBy('Weight', 'Weight').sortedRows)).toEqual(['CBA', 'bhp10', 'BHP', 'VAS'])
  })

  it('reports the direction of the sorted column only', () => {
    const sorted = sortedBy('Weight', 'Weight')

    expect(sorted.directionOf('Weight')).toBe('descending')
    expect(sorted.directionOf('Ticker')).toBeUndefined()
  })

  it('leaves the rows alone for a column that cannot be sorted', () => {
    expect(sortedBy('Notes').sortedRows).toBe(ROWS)
  })
})
