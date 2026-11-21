// One research document: its details, then its text as chunks.

import type { ResearchDocumentDetail } from '../api/types'
import { formatCount, formatDate, formatDateTime } from '../lib/format'
import { MUTED_TEXT } from '../lib/styles'
import Card from './Card'
import DetailsList from './DetailsList'
import ResearchChunks from './ResearchChunks'
import ResearchStatusBadge from './ResearchStatusBadge'
import TickerLink from './TickerLink'

interface ResearchDocumentViewProps {
  document: ResearchDocumentDetail
  highlightedPosition: number | null
}

function ResearchDocumentView({ document, highlightedPosition }: ResearchDocumentViewProps) {
  const { chunks } = document

  return (
    <>
      <Card title="Details">
        <DetailsList
          details={[
            { label: 'Ticker', value: <TickerLink ticker={document.ticker} /> },
            { label: 'Document date', value: formatDate(document.document_date) },
            { label: 'File', value: document.file_name },
            { label: 'Uploaded by', value: document.uploaded_by },
            { label: 'Uploaded', value: formatDateTime(document.created_at) },
            { label: 'Status', value: <ResearchStatusBadge status={document.status} /> },
          ]}
        />
      </Card>
      <Card title="Text" aside={formatCount(chunks.length, 'chunk', 'chunks')}>
        {chunks.length === 0 ? (
          <p className={MUTED_TEXT}>This document has no text to show yet.</p>
        ) : (
          <ResearchChunks chunks={chunks} highlightedPosition={highlightedPosition} />
        )}
      </Card>
    </>
  )
}

export default ResearchDocumentView
