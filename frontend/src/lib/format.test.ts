import { describe, expect, it } from 'vitest'

import {
  formatCompactCurrency,
  formatCount,
  formatCurrency,
  formatDate,
  formatDateTime,
  formatPercent,
  formatProfit,
  formatQuantity,
  formatRange,
  formatSignedPercent,
  formatTimer,
} from './format'

describe('formatDate', () => {
  it('writes a date-only value in words', () => {
    expect(formatDate('2026-03-16')).toBe('16 Mar 2026')
  })

  it('returns text that is not a date unchanged', () => {
    expect(formatDate('soon')).toBe('soon')
  })
})

describe('formatDateTime', () => {
  it("writes a moment in the reader's own time zone", () => {
    const moment = new Date(2026, 2, 16, 15, 5)

    expect(formatDateTime(moment.toISOString())).toBe('16 Mar 2026, 3:05 pm')
  })

  it('returns text that is not a moment unchanged', () => {
    expect(formatDateTime('soon')).toBe('soon')
  })
})

describe('formatCurrency', () => {
  it('shows two decimals by default', () => {
    expect(formatCurrency('1234.5')).toBe('$1,234.50')
  })

  it('shows more decimals for a unit price when asked', () => {
    expect(formatCurrency('4.385000', 'AUD', 4)).toBe('$4.385')
    expect(formatCurrency('4.385000', 'AUD', 4, 4)).toBe('$4.3850')
  })

  it('names a currency that is not the local one', () => {
    // The space is a non-breaking one, so the code and the amount stay on one line.
    expect(formatCurrency(10, 'USD')).toBe('USD\u00a010.00')
  })

  it('returns text that is not a number unchanged', () => {
    expect(formatCurrency('n/a')).toBe('n/a')
  })
})

describe('formatProfit', () => {
  it('shows the sign of a gain and of a loss, and none for zero', () => {
    expect(formatProfit('812.59')).toBe('+$812.59')
    expect(formatProfit(-120)).toBe('-$120.00')
    expect(formatProfit(0)).toBe('$0.00')
  })
})

describe('the other number formats', () => {
  it('shortens money for a chart axis', () => {
    expect(formatCompactCurrency(150000)).toBe('$150K')
  })

  it('writes a fraction as a percentage', () => {
    expect(formatPercent(0.0886)).toBe('8.9%')
    expect(formatSignedPercent(0.0886)).toBe('+8.9%')
    expect(formatSignedPercent(-0.024)).toBe('-2.4%')
  })

  it('keeps the decimals of a fractional quantity', () => {
    expect(formatQuantity('1500.000000')).toBe('1,500')
    expect(formatQuantity('0.250000')).toBe('0.25')
  })
})

describe('the text formats', () => {
  it('pads the seconds of a timer', () => {
    expect(formatTimer(642)).toBe('10:42')
    expect(formatTimer(5)).toBe('0:05')
  })

  it('picks the singular or plural word', () => {
    expect(formatCount(1, 'trade', 'trades')).toBe('1 trade')
    expect(formatCount(2, 'trade', 'trades')).toBe('2 trades')
  })

  it('describes the rows on a page', () => {
    expect(formatRange(25, 25, 120)).toBe('26–50 of 120')
  })
})
