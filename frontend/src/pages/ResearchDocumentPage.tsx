// The page for one research document. A link to a chunk highlights that chunk.

import { useLocation } from 'react-router'

import type { ResearchDocumentDetail } from '../api/types'
import NotFoundNote from '../components/NotFoundNote'
import PageLayout from '../components/PageLayout'
import ResearchDocumentView from '../components/ResearchDocumentView'
import { chunkPositionIn } from '../lib/research'
import { ROUTES } from '../routes'

const NO_DOCUMENT: ResearchDocumentDetail | null = null

function ResearchDocumentPage() {
  const { hash } = useLocation()
  const document = NO_DOCUMENT

  if (document === null) {
    return (
      <PageLayout title="Research document">
        <NotFoundNote
          message="This document could not be found."
          backTo={ROUTES.research}
          backLabel="Back to Research"
        />
      </PageLayout>
    )
  }

  return (
    <PageLayout title={document.title}>
      <ResearchDocumentView document={document} highlightedPosition={chunkPositionIn(hash)} />
    </PageLayout>
  )
}

export default ResearchDocumentPage
