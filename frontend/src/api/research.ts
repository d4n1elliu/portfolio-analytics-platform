// The API calls for research documents.

import type { ResearchUpload } from '../lib/research'
import { postForm, request, requestOrNull } from './client'
import type { ResearchDocument, ResearchDocumentDetail } from './types'

export function listResearchDocuments(signal?: AbortSignal): Promise<ResearchDocument[]> {
  return request<ResearchDocument[]>('/research/documents', { signal })
}

export function getResearchDocument(
  id: string,
  signal?: AbortSignal,
): Promise<ResearchDocumentDetail | null> {
  const path = `/research/documents/${encodeURIComponent(id)}`
  return requestOrNull<ResearchDocumentDetail>(path, { signal })
}

export async function uploadResearchDocument(upload: ResearchUpload): Promise<void> {
  if (upload.file === null) return
  await postForm('/research/documents', {
    file: upload.file,
    title: upload.title.trim(),
    ticker: upload.ticker,
    document_date: upload.documentDate,
  })
}
