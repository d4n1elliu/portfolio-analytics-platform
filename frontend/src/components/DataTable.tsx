import type { ReactNode } from 'react'

import { useSortedRows } from '../hooks/useSortedRows'
import type { SortDirection, SortValue } from '../hooks/useSortedRows'

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
}

interface DataTableProps<T> {
  columns: Column<T>[]
  rows: T[]
  /** A value that is different for every row, such as its id. */
  getRowKey: (row: T) => string | number
}

/** A table for any kind of row. The columns decide what is shown. */
function DataTable<T>({ columns, rows, getRowKey }: DataTableProps<T>) {
  const { sortedRows, toggleSort, directionOf } = useSortedRows(rows, columns)

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-y border-slate-200 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            {columns.map((column) => {
              const alignRight = column.align === 'right'
              const direction = directionOf(column.header)
              return (
                <th
                  key={column.header}
                  aria-sort={column.sortValue ? (direction ?? 'none') : undefined}
                  className={`px-6 py-3 font-medium ${alignRight ? 'text-right' : ''}`}
                >
                  {column.sortValue ? (
                    <SortButton
                      label={column.header}
                      direction={direction}
                      alignRight={alignRight}
                      onClick={() => toggleSort(column.header)}
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
          {sortedRows.map((row) => (
            <tr key={getRowKey(row)}>
              {columns.map((column) => (
                <td
                  key={column.header}
                  className={`px-6 py-3 ${column.align === 'right' ? 'text-right tabular-nums' : ''} ${column.className ?? ''}`}
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
