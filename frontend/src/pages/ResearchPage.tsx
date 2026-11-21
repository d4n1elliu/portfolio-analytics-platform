// The Research page: the library of uploaded documents, and a form to add one.

import { useState } from 'react'

import type { ResearchDocument } from '../api/types'
import Card from '../components/Card'
import PageLayout from '../components/PageLayout'
import ResearchFilters from '../components/ResearchFilters'
import ResearchTable from '../components/ResearchTable'
import ResearchUploadForm from '../components/ResearchUploadForm'
import RoleNote from '../components/RoleNote'
import { useTickers } from '../hooks/useTickers'
import { useToday } from '../hooks/useToday'
import { useAuth } from '../lib/auth'
import { formatCount } from '../lib/format'
import {
  NO_RESEARCH_FILTERS,
  RESEARCH_NOT_CONNECTED,
  filterDocuments,
  hasResearchFilters,
} from '../lib/research'
import { can } from '../lib/roles'
import { MUTED_TEXT } from '../lib/styles'

const NO_DOCUMENTS: ResearchDocument[] = []

async function uploadNotConnected(): Promise<void> {
  throw new Error(RESEARCH_NOT_CONNECTED)
}

function ResearchPage() {
  const [filters, setFilters] = useState(NO_RESEARCH_FILTERS)
  const today = useToday()
  const tickers = useTickers()
  const { state: auth } = useAuth()

  const user = auth.status === 'signedIn' ? auth.user : null
  const documents = NO_DOCUMENTS
  const shown = filterDocuments(documents, filters)

  return (
    <PageLayout title="Research">
      {can(user, 'upload_research') && (
        <Card title="Upload research">
          <ResearchUploadForm tickers={tickers} today={today} upload={uploadNotConnected} />
        </Card>
      )}
      {user && !can(user, 'upload_research') && (
        <RoleNote title="Upload research" role={user.role} can="read research" cannot="upload it" />
      )}

      <Card
        title="Library"
        padded={shown.length === 0}
        aside={documents.length > 0 && formatCount(shown.length, 'document', 'documents')}
      >
        <div className={shown.length === 0 ? 'space-y-4' : 'px-6 pb-4'}>
          <ResearchFilters filters={filters} tickers={tickers} onChange={setFilters} />
          {documents.length === 0 && (
            <p className={MUTED_TEXT}>No research has been uploaded yet.</p>
          )}
          {documents.length > 0 && shown.length === 0 && hasResearchFilters(filters) && (
            <p className={MUTED_TEXT}>No documents match the filters.</p>
          )}
        </div>
        {shown.length > 0 && <ResearchTable documents={shown} />}
      </Card>
    </PageLayout>
  )
}

export default ResearchPage
