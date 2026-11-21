// @vitest-environment jsdom
// Tests for DataTable, sorting its own rows or showing rows sorted outside it.

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import DataTable from './DataTable'
import type { Column } from './DataTable'

interface Row {
  ticker: string
  quantity: number
}

const ROWS: Row[] = [
  { ticker: 'CBA', quantity: 10 },
  { ticker: 'BHP', quantity: 30 },
  { ticker: 'VAS', quantity: 20 },
]

const COLUMNS: Column<Row>[] = [
  { header: 'Ticker', render: (row) => row.ticker, sortValue: (row) => row.ticker },
  { header: 'Quantity', render: (row) => row.quantity, sortKey: 'quantity' },
]

function shownTickers(): string[] {
  return screen.getAllByRole('row').flatMap((row) => row.querySelector('td')?.textContent ?? [])
}

function heading(name: string): HTMLElement {
  return screen.getByRole('columnheader', { name: new RegExp(name) })
}

afterEach(cleanup)

describe('a table that sorts its own rows', () => {
  it('sorts by a column with a sortValue when its heading is clicked', () => {
    render(<DataTable columns={COLUMNS} rows={ROWS} getRowKey={(row) => row.ticker} />)
    expect(shownTickers()).toEqual(['CBA', 'BHP', 'VAS'])

    fireEvent.click(screen.getByRole('button', { name: /Ticker/ }))

    expect(shownTickers()).toEqual(['BHP', 'CBA', 'VAS'])
    expect(heading('Ticker').getAttribute('aria-sort')).toBe('ascending')
  })

  it('has no button for a column that only has a sortKey', () => {
    render(<DataTable columns={COLUMNS} rows={ROWS} getRowKey={(row) => row.ticker} />)

    expect(screen.queryByRole('button', { name: /Quantity/ })).toBeNull()
  })
})

describe('a table whose rows are sorted outside it', () => {
  it('keeps the order given and reports the sortKey that was clicked', () => {
    const onSort = vi.fn()
    render(
      <DataTable
        columns={COLUMNS}
        rows={ROWS}
        getRowKey={(row) => row.ticker}
        sort={{ key: 'quantity', direction: 'descending' }}
        onSort={onSort}
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: /Quantity/ }))

    expect(onSort).toHaveBeenCalledWith('quantity')
    expect(shownTickers()).toEqual(['CBA', 'BHP', 'VAS'])
    expect(heading('Quantity').getAttribute('aria-sort')).toBe('descending')
    expect(screen.queryByRole('button', { name: /Ticker/ })).toBeNull()
  })
})
