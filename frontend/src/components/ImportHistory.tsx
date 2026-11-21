// A card listing the latest trade imports.

import type { ImportBatch, Page } from '../api/types'
import type { QueryState } from '../hooks/useApiQuery'
import { formatCount, formatDateTime } from '../lib/format'
import Card from './Card'
import DataTable from './DataTable'
import type { Column } from './DataTable'
import LoadState from './LoadState'

const COLUMNS: Column<ImportBatch>[] = [
  {
    header: 'Imported',
    render: (batch) => formatDateTime(batch.created_at),
    className: 'whitespace-nowrap',
  },
  { header: 'File', render: (batch) => batch.file_name, className: 'font-medium' },
  { header: 'Trades', align: 'right', render: (batch) => batch.row_count },
  { header: 'Imported by', render: (batch) => batch.imported_by, className: 'text-slate-600' },
]

interface ImportHistoryProps {
  state: QueryState<Page<ImportBatch>>
  onRetry: () => void
}

function ImportHistory({ state, onRetry }: ImportHistoryProps) {
  const imports = state.status === 'loaded' ? state.data : null
  const hasRows = imports !== null && imports.total > 0

  return (
    <Card title="Import history" padded={!hasRows} aside={imports && countOf(imports)}>
      <LoadState
        state={state}
        onRetry={onRetry}
        loadingText="Loading imports…"
        emptyText="No files have been imported yet."
        isEmpty={(loaded) => loaded.total === 0}
      >
        {(loaded) => (
          <DataTable columns={COLUMNS} rows={loaded.items} getRowKey={(batch) => batch.id} />
        )}
      </LoadState>
    </Card>
  )
}

function countOf(imports: Page<ImportBatch>): string {
  const count = formatCount(imports.total, 'import', 'imports')
  return imports.items.length < imports.total ? `Latest ${imports.items.length} of ${count}` : count
}

export default ImportHistory
