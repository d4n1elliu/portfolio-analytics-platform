import type { GrowthPoint, PerformancePeriod, PeriodReturn } from '../api/types'

export const PERIOD_LABELS: Record<PerformancePeriod, string> = {
  '1m': '1 month',
  '3m': '3 months',
  ytd: 'Year to date',
  '1y': '1 year',
  inception: 'Since inception',
}

export interface ReturnSeries {
  dates: string[]
  /** The return from the start of the period to each date, as a fraction. */
  returns: number[]
}

/** The return on each date of a period, for a chart. Empty when the period has no return. */
export function returnSeries(growth: GrowthPoint[], period: PeriodReturn): ReturnSeries {
  const start = period.start_date
  if (start === null) return { dates: [], returns: [] }

  const points = growth.filter((point) => point.date >= start)
  // Since inception is measured from before the first date, so its first
  // day counts. Every other period starts at zero on its start date.
  const base = period.period === 'inception' ? 1 : Number(points[0].portfolio)
  return {
    dates: points.map((point) => point.date),
    returns: points.map((point) => Number(point.portfolio) / base - 1),
  }
}
