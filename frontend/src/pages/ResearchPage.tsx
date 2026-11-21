// The Research page: the library of uploaded documents, and a form to add one.

import { useState } from 'react'

import { listResearchDocuments, uploadResearchDocument } from '../api/research'
import Card from '../components/Card'
import LoadError from '../components/LoadError'
import PageLayout from '../components/PageLayout'
import ResearchFilters from '../components/ResearchFilters'
import ResearchTable from '../components/ResearchTable'
import ResearchUploadForm from '../components/ResearchUploadForm'
import RoleNote from '../components/RoleNote'
import { useApiQuery } from '../hooks/useApiQuery'
import { useTickers } from '../hooks/useTickers'
import { useToday } from '../hooks/useToday'
import { useAuth } from '../lib/auth'
import { formatCount } from '../lib/format'
import { NO_RESEARCH_FILTERS, filterDocuments } from '../lib/research'
import type { ResearchUpload } from '../lib/research'
import { can } from '../lib/roles'
import { MUTED_TEXT } from '../lib/styles'

function loadEveryDocument(signal: AbortSignal) {
  return listResearchDocuments(undefined, signal)
}

function ResearchPage() {
  const [filters, setFilters] = useState(NO_RESEARCH_FILTERS)
  const today = useToday()
  const tickers = useTickers()
  const { state: auth } = useAuth()
  const { state, reload } = useApiQuery(loadEveryDocument, { keepPreviousData: true })

  const user = auth.status === 'signedIn' ? auth.user : null
  const documents = state.status === 'loaded' ? state.data : null
  const shown = documents ? filterDocuments(documents, filters) : []

  async function upload(details: ResearchUpload) {
    await uploadResearchDocument(details)
    reload()
  }

  return (
    <PageLayout title="Research">
      {can(user, 'upload_research') && (
        <Card title="Upload research">
          <ResearchUploadForm tickers={tickers} today={today} upload={upload} />
        </Card>
      )}
      {user && !can(user, 'upload_research') && (
        <RoleNote title="Upload research" role={user.role} can="read research" cannot="upload it" />
      )}

      <Card
        title="Library"
        padded={shown.length === 0}
        aside={documents && formatCount(shown.length, 'document', 'documents')}
      >
        <div className={shown.length === 0 ? 'space-y-4' : 'px-6 pb-4'}>
          <ResearchFilters filters={filters} tickers={tickers} onChange={setFilters} />
          {state.status === 'loading' && <p className={MUTED_TEXT}>Loading research…</p>}
          {state.status === 'error' && <LoadError message={state.message} onRetry={reload} />}
          {documents?.length === 0 && (
            <p className={MUTED_TEXT}>No research has been uploaded yet.</p>
          )}
          {documents && documents.length > 0 && shown.length === 0 && (
            <p className={MUTED_TEXT}>No documents match the filters.</p>
          )}
        </div>
        {shown.length > 0 && <ResearchTable documents={shown} />}
      </Card>
    </PageLayout>
  )
}

export default ResearchPage
