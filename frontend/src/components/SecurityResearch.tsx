// A card on the page for one security, listing the research notes about it.

import { useCallback } from 'react'
import { Link } from 'react-router'

import { listResearchDocuments } from '../api/research'
import { useApiQuery } from '../hooks/useApiQuery'
import { formatCount, formatDate } from '../lib/format'
import { NAME_LINK } from '../lib/styles'
import { researchDocumentPath } from '../routes'
import Card from './Card'
import LoadState from './LoadState'

function SecurityResearch({ ticker }: { ticker: string }) {
  const loadNotes = useCallback(
    (signal: AbortSignal) => listResearchDocuments(ticker, signal),
    [ticker],
  )
  const { state, reload } = useApiQuery(loadNotes)
  const notes = state.status === 'loaded' ? state.data : null

  return (
    <Card title="Research" aside={notes && formatCount(notes.length, 'note', 'notes')}>
      <LoadState
        state={state}
        onRetry={reload}
        loadingText="Loading research…"
        emptyText="No research has been uploaded about this security."
        isEmpty={(loaded) => loaded.length === 0}
      >
        {(loaded) => (
          <ul className="space-y-2 text-sm">
            {loaded.map((note) => (
              <li key={note.id} className="flex flex-wrap items-baseline justify-between gap-x-4">
                <Link to={researchDocumentPath(note.id)} className={NAME_LINK}>
                  {note.title}
                </Link>
                <span className="text-slate-500">{formatDate(note.document_date)}</span>
              </li>
            ))}
          </ul>
        )}
      </LoadState>
    </Card>
  )
}

export default SecurityResearch
