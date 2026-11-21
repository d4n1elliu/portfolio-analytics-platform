import type { ReactNode } from 'react'

import { useSortedRows } from '../hooks/useSortedRows'
import type { SortValue } from '../hooks/useSortedRows'
import type { SortBy, SortDirection } from '../lib/sorting'

export interface Column<T> {
  header: string
  /** Returns what to show in this column for one row. */
  render: (row: T) => ReactNode
  /** Use 'right' for numbers so their digits line up. */
  align?: 'left' | 'right'
  /** Extra classes for this column's cells. */
  className?: string
  /** Add this to make the column sortable. Returns the value to sort a row by. */
  sortValue?: (row: T) => SortValue
  sortKey?: string
}

interface DataTableProps<T> {
  columns: Column<T>[]
  rows: T[]
  /** A value that is different for every row, such as its id. */
  getRowKey: (row: T) => string | number
  sort?: SortBy<string>
  onSort?: (sortKey: string) => void
}

// The first column stays in place when the table scrolls sideways.
const CELL_SPACING = 'px-2 py-3 first:sticky first:left-0 first:bg-white first:pl-6 last:pr-6'

const NUMBER_CELL = 'text-right tabular-nums whitespace-nowrap'

/** A table for any kind of row. The columns decide what is shown. */
function DataTable<T>({ columns, rows, getRowKey, sort, onSort }: DataTableProps<T>) {
  const local = useSortedRows(rows, columns)
  const sortedOutside = sort !== undefined && onSort !== undefined
  const shownRows = sortedOutside ? rows : local.sortedRows

  function sortIdOf(column: Column<T>): string | undefined {
    if (sortedOutside) return column.sortKey
    return column.sortValue ? column.header : undefined
  }

  function directionOf(sortId: string): SortDirection | undefined {
    if (!sortedOutside) return local.directionOf(sortId)
    return sort.key === sortId ? sort.direction : undefined
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-y border-slate-200 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            {columns.map((column) => {
              const alignRight = column.align === 'right'
              const sortId = sortIdOf(column)
              const direction = sortId === undefined ? undefined : directionOf(sortId)
              return (
                <th
                  key={column.header}
                  aria-sort={sortId === undefined ? undefined : (direction ?? 'none')}
                  className={`${CELL_SPACING} whitespace-nowrap font-medium ${alignRight ? 'text-right' : ''}`}
                >
                  {sortId !== undefined ? (
                    <SortButton
                      label={column.header}
                      direction={direction}
                      alignRight={alignRight}
                      onClick={() => (sortedOutside ? onSort(sortId) : local.toggleSort(sortId))}
                    />
                  ) : (
                    column.header
                  )}
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {shownRows.map((row) => (
            <tr key={getRowKey(row)}>
              {columns.map((column) => (
                <td
                  key={column.header}
                  className={`${CELL_SPACING} ${column.align === 'right' ? NUMBER_CELL : ''} ${column.className ?? ''}`}
                >
                  {column.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

interface SortButtonProps {
  label: string
  direction: SortDirection | undefined
  alignRight: boolean
  onClick: () => void
}

function SortButton({ label, direction, alignRight, onClick }: SortButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      // Arrow first when right-aligned, so the heading lines up with its numbers.
      className={`inline-flex items-center gap-1 uppercase tracking-wide hover:text-slate-900 ${alignRight ? 'flex-row-reverse' : ''}`}
    >
      {label}
      <span aria-hidden="true" className={direction ? '' : 'invisible'}>
        {direction === 'descending' ? '↓' : '↑'}
      </span>
    </button>
  )
}

export default DataTable
