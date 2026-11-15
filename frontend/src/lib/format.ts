// Shared helpers so every screen shows dates, money and counts the same way.

import { DEFAULT_CURRENCY, LOCALE } from '../config'

/** Shown in place of a value that is missing. */
export const NO_VALUE = '—'

const dateFormatter = new Intl.DateTimeFormat(LOCALE, {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
})

const percentFormatter = new Intl.NumberFormat(LOCALE, {
  style: 'percent',
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
})

const quantityFormatter = new Intl.NumberFormat(LOCALE, { maximumFractionDigits: 6 })

/** Format a date-only value such as "2026-03-16" as "16 Mar 2026". */
export function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split('-').map(Number)
  // Built from its parts so the date stays in the local time zone.
  const date = new Date(year, month - 1, day)
  return Number.isNaN(date.getTime()) ? isoDate : dateFormatter.format(date)
}

/**
 * Format money, for example "$1,234.50". Pass a larger `maxDecimals` for
 * unit prices, which can be quoted in fractions of a cent. Pass `minDecimals`
 * to always show at least that many.
 */
export function formatCurrency(
  value: string | number,
  currency = DEFAULT_CURRENCY,
  maxDecimals = 2,
  minDecimals = 2,
): string {
  const amount = Number(value)
  if (Number.isNaN(amount)) return String(value)
  return new Intl.NumberFormat(LOCALE, {
    style: 'currency',
    currency,
    minimumFractionDigits: minDecimals,
    maximumFractionDigits: maxDecimals,
  }).format(amount)
}

/** Format money in short form for a chart axis, such as "$150K". */
export function formatCompactCurrency(value: number, currency = DEFAULT_CURRENCY): string {
  return new Intl.NumberFormat(LOCALE, {
    style: 'currency',
    currency,
    notation: 'compact',
  }).format(value)
}

/** Format a profit or loss with its sign, such as "+$812.59" or "-$120.00". */
export function formatProfit(value: string | number, currency = DEFAULT_CURRENCY): string {
  const amount = Number(value)
  if (Number.isNaN(amount)) return String(value)
  return new Intl.NumberFormat(LOCALE, {
    style: 'currency',
    currency,
    signDisplay: 'exceptZero',
  }).format(amount)
}

/** Format a fraction as a percentage, so 0.0886 becomes "8.9%". */
export function formatPercent(fraction: number): string {
  return percentFormatter.format(fraction)
}

/** Format a number of shares or units, for example "1,500" or "0.25". */
export function formatQuantity(value: string | number): string {
  const amount = Number(value)
  return Number.isNaN(amount) ? String(value) : quantityFormatter.format(amount)
}

/** Pick the singular or plural word for a count: "1 trade", "2 trades". */
export function formatCount(count: number, singular: string, plural: string): string {
  return `${count} ${count === 1 ? singular : plural}`
}

/** Describe which rows a page shows, for example "26–50 of 120". */
export function formatRange(offset: number, shown: number, total: number): string {
  return `${offset + 1}–${offset + shown} of ${total}`
}
