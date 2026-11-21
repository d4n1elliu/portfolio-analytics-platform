// @vitest-environment jsdom
// Tests for the view of one research document and its chunks.

import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { ResearchDocumentDetail } from '../api/types'
import ResearchDocumentView from './ResearchDocumentView'

const DOCUMENT: ResearchDocumentDetail = {
  id: 12,
  title: 'BHP iron ore outlook',
  file_name: 'bhp-outlook.pdf',
  ticker: 'BHP',
  document_date: '2026-11-13',
  chunk_count: 2,
  uploaded_by: 'Demo Analyst',
  created_at: '2026-11-14T03:00:00Z',
  chunks: [
    { id: 101, position: 1, text: 'Iron ore prices rose.' },
    { id: 102, position: 2, text: 'Costs were flat.' },
  ],
}

const scrollIntoView = vi.fn()

function renderView(document: ResearchDocumentDetail, highlightedPosition: number | null) {
  render(
    <MemoryRouter>
      <ResearchDocumentView document={document} highlightedPosition={highlightedPosition} />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  Element.prototype.scrollIntoView = scrollIntoView
})

afterEach(() => {
  cleanup()
  scrollIntoView.mockClear()
})

describe('ResearchDocumentView', () => {
  it('shows the details of the document, with its ticker as a link', () => {
    renderView(DOCUMENT, null)

    expect(screen.getByRole('link', { name: 'BHP' }).getAttribute('href')).toBe('/securities/BHP')
    expect(screen.getByText('bhp-outlook.pdf')).toBeTruthy()
    expect(screen.getByText('13 Nov 2026')).toBeTruthy()
  })

  it('lists each chunk in order with a link to itself', () => {
    renderView(DOCUMENT, null)

    const chunks = screen.getByRole('list', { name: 'Chunks' }).querySelectorAll('li')
    expect([...chunks].map((chunk) => chunk.id)).toEqual(['chunk-1', 'chunk-2'])
    expect(screen.getByRole('link', { name: 'Chunk 2' }).getAttribute('href')).toBe('#chunk-2')
    expect(screen.getByText('2 chunks')).toBeTruthy()
  })

  it('marks the highlighted chunk and scrolls to it', () => {
    renderView(DOCUMENT, 2)

    const marked = document.querySelectorAll('[aria-current="true"]')
    expect([...marked].map((chunk) => chunk.id)).toEqual(['chunk-2'])
    expect(scrollIntoView).toHaveBeenCalledOnce()
  })

  it('marks nothing and does not scroll without a highlighted chunk', () => {
    renderView(DOCUMENT, null)

    expect(document.querySelectorAll('[aria-current="true"]')).toHaveLength(0)
    expect(scrollIntoView).not.toHaveBeenCalled()
  })

  it('says so when the document has no text yet', () => {
    renderView({ ...DOCUMENT, chunk_count: 0, chunks: [] }, null)

    expect(screen.getByText('This document has no text to show yet.')).toBeTruthy()
    expect(screen.queryByRole('list', { name: 'Chunks' })).toBeNull()
  })
})
