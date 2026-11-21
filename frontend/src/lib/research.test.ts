// Tests for the research library filters and the rules of a research upload.

import { describe, expect, it } from 'vitest'

import type { ResearchDocument } from '../api/types'
import { RESEARCH_MAX_FILE_BYTES } from '../config'
import { NO_RESEARCH_FILTERS, filterDocuments, hasResearchFilters, uploadProblem } from './research'
import type { ResearchUpload } from './research'

const TODAY = '2026-11-21'

function document(ticker: string, documentDate: string): ResearchDocument {
  return {
    id: 1,
    title: `${ticker} note`,
    file_name: 'note.pdf',
    ticker,
    document_date: documentDate,
    status: 'ready',
    uploaded_by: 'Demo Analyst',
    created_at: '2026-11-21T03:00:00Z',
  }
}

function fileNamed(name: string, size = 1000): File {
  const file = new File(['x'], name)
  Object.defineProperty(file, 'size', { value: size })
  return file
}

function upload(fields: Partial<ResearchUpload> = {}): ResearchUpload {
  return {
    file: fileNamed('bhp-note.pdf'),
    title: 'BHP note',
    ticker: 'BHP',
    documentDate: '2026-11-13',
    ...fields,
  }
}

describe('filterDocuments', () => {
  const documents = [
    document('BHP', '2026-10-01'),
    document('BHP', '2026-11-13'),
    document('CBA', '2026-11-13'),
  ]

  it('returns everything when no filter is set', () => {
    expect(filterDocuments(documents, NO_RESEARCH_FILTERS)).toEqual(documents)
  })

  it('keeps the documents that match the ticker and fall in the dates, both included', () => {
    const filters = { ticker: 'BHP', dateFrom: '2026-11-13', dateTo: '2026-11-13' }

    expect(filterDocuments(documents, filters)).toEqual([documents[1]])
  })

  it('knows whether any filter is set', () => {
    expect(hasResearchFilters(NO_RESEARCH_FILTERS)).toBe(false)
    expect(hasResearchFilters({ ...NO_RESEARCH_FILTERS, ticker: 'BHP' })).toBe(true)
  })
})

describe('uploadProblem', () => {
  it('accepts a complete upload', () => {
    expect(uploadProblem(upload(), TODAY)).toBeNull()
  })

  it('accepts each allowed file type, whatever the capital letters', () => {
    for (const name of ['note.PDF', 'note.md', 'note.txt']) {
      expect(uploadProblem(upload({ file: fileNamed(name) }), TODAY)).toBeNull()
    }
  })

  it.each([
    [{ file: null }, 'Choose a file to upload.'],
    [{ file: fileNamed('note.docx') }, 'The file must be one of .pdf, .md, .txt.'],
    [
      { file: fileNamed('note.pdf', RESEARCH_MAX_FILE_BYTES + 1) },
      'The file is larger than 10 MB.',
    ],
    [{ title: '  ' }, 'Give the document a title.'],
    [{ ticker: '' }, 'Choose the ticker the document is about.'],
    [{ documentDate: '' }, 'Choose the date of the document.'],
    [{ documentDate: '2026-11-22' }, 'The date of the document cannot be in the future.'],
  ])('refuses %o', (fields, problem) => {
    expect(uploadProblem(upload(fields), TODAY)).toBe(problem)
  })
})
