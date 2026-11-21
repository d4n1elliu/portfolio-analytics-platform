// The page for one research document. A link to a chunk highlights that chunk.

import { useCallback } from 'react'
import { useLocation, useParams } from 'react-router'

import { getResearchDocument } from '../api/research'
import LoadError from '../components/LoadError'
import NotFoundNote from '../components/NotFoundNote'
import PageLayout from '../components/PageLayout'
import ResearchDocumentView from '../components/ResearchDocumentView'
import { useApiQuery } from '../hooks/useApiQuery'
import { chunkPositionIn } from '../lib/research'
import { MUTED_TEXT } from '../lib/styles'
import { ROUTES } from '../routes'

function ResearchDocumentPage() {
  const { id = '' } = useParams()
  const { hash } = useLocation()
  const loadDocument = useCallback((signal: AbortSignal) => getResearchDocument(id, signal), [id])
  const { state, reload } = useApiQuery(loadDocument)
  const document = state.status === 'loaded' ? state.data : null

  return (
    <PageLayout title={document?.title ?? 'Research document'}>
      {state.status === 'loading' && <p className={MUTED_TEXT}>Loading the document…</p>}
      {state.status === 'error' && <LoadError message={state.message} onRetry={reload} />}
      {state.status === 'loaded' && document === null && (
        <NotFoundNote
          message="This document could not be found."
          backTo={ROUTES.research}
          backLabel="Back to Research"
        />
      )}
      {document !== null && (
        <ResearchDocumentView document={document} highlightedPosition={chunkPositionIn(hash)} />
      )}
    </PageLayout>
  )
}

export default ResearchDocumentPage
