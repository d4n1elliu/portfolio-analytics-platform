import type { ReactNode } from 'react'

export interface Column<T> {
  header: string
  /** Returns what to show in this column for one row. */
  render: (row: T) => ReactNode
  /** Use 'right' for numbers so their digits line up. */
  align?: 'left' | 'right'
  /** Extra classes for this column's cells. */
  className?: string
}

interface DataTableProps<T> {
  columns: Column<T>[]
  rows: T[]
  /** A value that is different for every row, such as its id. */
  getRowKey: (row: T) => string | number
}

/** A table for any kind of row. The columns decide what is shown. */
function DataTable<T>({ columns, rows, getRowKey }: DataTableProps<T>) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="border-y border-slate-200 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            {columns.map((column) => (
              <th
                key={column.header}
                className={`px-6 py-3 font-medium ${column.align === 'right' ? 'text-right' : ''}`}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((row) => (
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

export default DataTable
