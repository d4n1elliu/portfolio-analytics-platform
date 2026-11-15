// Helpers for date-only values such as "2026-03-16".

const SATURDAY = 6
const SUNDAY = 0

/** Read a date-only value as midnight in the local time zone. */
export function parseDate(isoDate: string): Date {
  const [year, month, day] = isoDate.split('-').map(Number)
  return new Date(year, month - 1, day)
}

/** Public holidays are counted as business days. */
export function businessDaysSince(isoDate: string, today: Date): number {
  const lastDay = new Date(today.getFullYear(), today.getMonth(), today.getDate())
  const day = parseDate(isoDate)
  let count = 0
  for (day.setDate(day.getDate() + 1); day <= lastDay; day.setDate(day.getDate() + 1)) {
    if (isWeekday(day)) count += 1
  }
  return count
}

function isWeekday(day: Date): boolean {
  return day.getDay() !== SATURDAY && day.getDay() !== SUNDAY
}
