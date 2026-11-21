// The research library table: one row for each uploaded document.

import { Link } from 'react-router'

import type { ResearchDocument } from '../api/types'
import { formatDate, formatDateTime } from '../lib/format'
import { NAME_LINK } from '../lib/styles'
import { researchDocumentPath } from '../routes'
import DataTable from './DataTable'
import type { Column } from './DataTable'
import TickerLink from './TickerLink'

const COLUMNS: Column<ResearchDocument>[] = [
  {
    header: 'Date',
    render: (document) => formatDate(document.document_date),
    className: 'whitespace-nowrap',
    sortValue: (document) => document.document_date,
  },
  {
    header: 'Title',
    render: (document) => (
      <Link to={researchDocumentPath(document.id)} className={NAME_LINK}>
        {document.title}
      </Link>
    ),
    sortValue: (document) => document.title,
  },
  {
    header: 'Ticker',
    render: (document) => <TickerLink ticker={document.ticker} />,
    sortValue: (document) => document.ticker,
  },
  { header: 'Chunks', align: 'right', render: (document) => document.chunk_count },
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
