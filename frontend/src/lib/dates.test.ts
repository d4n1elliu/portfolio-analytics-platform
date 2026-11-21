// Tests for the date helpers.

import { describe, expect, it } from 'vitest'

import { businessDaysSince, parseDate, toIsoDate } from './dates'

const FRIDAY = '2026-11-13'

describe('parseDate', () => {
  it('reads the date in the local time zone, so the day never shifts', () => {
    const date = parseDate('2026-03-16')

    expect([date.getFullYear(), date.getMonth(), date.getDate()]).toEqual([2026, 2, 16])
    expect(date.getHours()).toBe(0)
  })
})

describe('toIsoDate', () => {
  it('pads the month and day, and gives back what parseDate read', () => {
    expect(toIsoDate(new Date(2026, 2, 6, 23, 30))).toBe('2026-03-06')
    expect(toIsoDate(parseDate('2026-11-13'))).toBe('2026-11-13')
  })
})

describe('businessDaysSince', () => {
  it('is zero on the same day', () => {
    expect(businessDaysSince(FRIDAY, new Date(2026, 10, 13, 15))).toBe(0)
  })

  it('does not count the weekend', () => {
    expect(businessDaysSince(FRIDAY, new Date(2026, 10, 15))).toBe(0)
    expect(businessDaysSince(FRIDAY, new Date(2026, 10, 16))).toBe(1)
  })

  it('counts every weekday of a full week', () => {
    expect(businessDaysSince(FRIDAY, new Date(2026, 10, 20))).toBe(5)
  })
})
