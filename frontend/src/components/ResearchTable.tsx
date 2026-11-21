// The research library table: one row for each uploaded document.

import type { ResearchDocument, ResearchStatus } from '../api/types'
import { formatDate, formatDateTime } from '../lib/format'
import Badge from './Badge'
import type { BadgeTone } from './Badge'
import DataTable from './DataTable'
import type { Column } from './DataTable'
import TickerLink from './TickerLink'

const STATUS_LABELS: Record<ResearchStatus, string> = {
  processing: 'Processing',
  ready: 'Ready',
  failed: 'Failed',
}

const STATUS_TONES: Record<ResearchStatus, BadgeTone> = {
  processing: 'neutral',
  ready: 'positive',
  failed: 'negative',
}

const COLUMNS: Column<ResearchDocument>[] = [
  {
    header: 'Date',
    render: (document) => formatDate(document.document_date),
    className: 'whitespace-nowrap',
    sortValue: (document) => document.document_date,
  },
  {
    header: 'Title',
    render: (document) => document.title,
    className: 'font-medium',
    sortValue: (document) => document.title,
  },
  {
    header: 'Ticker',
    render: (document) => <TickerLink ticker={document.ticker} />,
    sortValue: (document) => document.ticker,
  },
  {
    header: 'Status',
    render: (document) => (
      <Badge tone={STATUS_TONES[document.status]}>{STATUS_LABELS[document.status]}</Badge>
    ),
  },
  {
    header: 'Uploaded by',
    render: (document) => document.uploaded_by,
    className: 'text-slate-600',
  },
  {
    header: 'Uploaded',
    render: (document) => formatDateTime(document.created_at),
    className: 'whitespace-nowrap',
  },
]

function ResearchTable({ documents }: { documents: ResearchDocument[] }) {
  return <DataTable columns={COLUMNS} rows={documents} getRowKey={(document) => document.id} />
}

export default ResearchTable
