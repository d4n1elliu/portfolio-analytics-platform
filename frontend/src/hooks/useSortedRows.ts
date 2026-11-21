import { useMemo, useState } from 'react'

import { LOCALE } from '../config'
import { nextSort } from '../lib/sorting'
import type { SortBy, SortDirection } from '../lib/sorting'

/** What a row is sorted by. Rows with null are listed last. */
export type SortValue = string | number | null

interface SortableColumn<T> {
  header: string
  sortValue?: (row: T) => SortValue
}

/** Sort rows by one column at a time. Rows keep their order until a column is chosen. */
export function useSortedRows<T>(rows: T[], columns: SortableColumn<T>[]) {
  const [sort, setSort] = useState<SortBy<string> | null>(null)

  const sortedRows = useMemo(() => {
    const sortValue = columns.find((column) => column.header === sort?.key)?.sortValue
    if (!sort || !sortValue) return rows
    return [...rows].sort((a, b) => compare(sortValue(a), sortValue(b), sort.direction))
  }, [rows, columns, sort])

  function toggleSort(header: string) {
    setSort((current) => nextSort(current, header))
  }

  function directionOf(header: string): SortDirection | undefined {
    return sort?.key === header ? sort.direction : undefined
  }

  return { sortedRows, toggleSort, directionOf }
}

function compare(a: SortValue, b: SortValue, direction: SortDirection): number {
  // Rows with no value stay last in both directions.
  if (a === null || b === null) return a === b ? 0 : a === null ? 1 : -1

  const order =
    typeof a === 'number' && typeof b === 'number'
      ? a - b
      : String(a).localeCompare(String(b), LOCALE, { numeric: true, sensitivity: 'base' })
  return direction === 'ascending' ? order : -order
}
