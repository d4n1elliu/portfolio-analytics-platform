// The research an answer drew on, each linking to the exact chunk it came from.

import { Link } from 'react-router'

import type { ChatSource } from '../api/types'
import { formatDate } from '../lib/format'
import { TEXT_LINK } from '../lib/styles'
import { researchDocumentPath } from '../routes'

function AnswerSources({ sources }: { sources: ChatSource[] }) {
  if (sources.length === 0) return null

  return (
    <ol aria-label="Sources" className="space-y-1 border-t border-slate-200 pt-2 text-xs">
      {sources.map((source) => (
        <li key={source.source}>
          [{source.source}]{' '}
          <Link to={researchDocumentPath(source.document_id, source.chunk)} className={TEXT_LINK}>
            {source.title}
          </Link>{' '}
          <span className="text-slate-500">
            {source.ticker} · {formatDate(source.document_date)} · chunk {source.chunk}
          </span>
        </li>
      ))}
    </ol>
  )
}

export default AnswerSources
