// Tests for nextSort.

import { describe, expect, it } from 'vitest'

import { nextSort } from './sorting'

describe('nextSort', () => {
  it('starts a newly chosen key in ascending order', () => {
    expect(nextSort(null, 'ticker')).toEqual({ key: 'ticker', direction: 'ascending' })
    expect(nextSort({ key: 'price', direction: 'descending' }, 'ticker')).toEqual({
      key: 'ticker',
      direction: 'ascending',
    })
  })

  it('reverses the order each time the same key is chosen', () => {
    const descending = nextSort({ key: 'ticker', direction: 'ascending' }, 'ticker')

    expect(descending.direction).toBe('descending')
    expect(nextSort(descending, 'ticker').direction).toBe('ascending')
  })
})
