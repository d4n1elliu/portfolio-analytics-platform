// The filters of the research library, and the rules a research upload must meet.

import type { ResearchDocument } from '../api/types'
import { RESEARCH_FILE_TYPES, RESEARCH_MAX_FILE_BYTES } from '../config'

const BYTES_IN_A_MEGABYTE = 1024 * 1024

export interface ResearchFilters {
  ticker: string
  dateFrom: string
  dateTo: string
}

export const NO_RESEARCH_FILTERS: ResearchFilters = { ticker: '', dateFrom: '', dateTo: '' }

export const RESEARCH_NOT_CONNECTED =
  'Research uploads are not connected yet, so nothing was saved.'

export interface ResearchUpload {
  file: File | null
  title: string
  ticker: string
  documentDate: string
}

export function hasResearchFilters(filters: ResearchFilters): boolean {
  return Object.values(filters).some((value) => value !== '')
}

export function filterDocuments(
  documents: ResearchDocument[],
  filters: ResearchFilters,
): ResearchDocument[] {
  return documents.filter(
    (document) =>
      (filters.ticker === '' || document.ticker === filters.ticker) &&
      (filters.dateFrom === '' || document.document_date >= filters.dateFrom) &&
      (filters.dateTo === '' || document.document_date <= filters.dateTo),
  )
}

export function uploadProblem(upload: ResearchUpload, today: string): string | null {
  const { file, title, ticker, documentDate } = upload
  if (file === null) return 'Choose a file to upload.'
  if (!hasAllowedType(file.name)) {
    return `The file must be one of ${RESEARCH_FILE_TYPES.join(', ')}.`
  }
  if (file.size > RESEARCH_MAX_FILE_BYTES) {
    return `The file is larger than ${RESEARCH_MAX_FILE_BYTES / BYTES_IN_A_MEGABYTE} MB.`
  }
  if (title.trim() === '') return 'Give the document a title.'
  if (ticker === '') return 'Choose the ticker the document is about.'
  if (documentDate === '') return 'Choose the date of the document.'
  if (documentDate > today) return 'The date of the document cannot be in the future.'
  return null
}

function hasAllowedType(fileName: string): boolean {
  return RESEARCH_FILE_TYPES.some((type) => fileName.toLowerCase().endsWith(type))
}

const CHUNK_ANCHOR_PREFIX = 'chunk-'

export function chunkAnchor(position: number): string {
  return `${CHUNK_ANCHOR_PREFIX}${position}`
}

export function chunkPositionIn(hash: string): number | null {
  const anchor = hash.replace(/^#/, '')
  if (!anchor.startsWith(CHUNK_ANCHOR_PREFIX)) return null
  const position = Number(anchor.slice(CHUNK_ANCHOR_PREFIX.length))
  return Number.isInteger(position) && position > 0 ? position : null
}
