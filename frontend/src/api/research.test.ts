// Tests for the research API calls.

import { describe, expect, it, vi } from 'vitest'

import { getResearchDocument, uploadResearchDocument } from './research'

function answerWith(status: number, body: unknown) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => new Response(JSON.stringify(body), { status })),
  )
}

describe('getResearchDocument', () => {
  it('returns nothing for an id no document has', async () => {
    answerWith(404, { detail: 'No research document has this id.' })

    expect(await getResearchDocument('999')).toBeNull()
  })

  it('still throws any other error', async () => {
    answerWith(500, null)

    await expect(getResearchDocument('1')).rejects.toThrow('The request failed (HTTP 500).')
  })
})

describe('uploadResearchDocument', () => {
  it('sends the file with its title, ticker and date as form fields', async () => {
    answerWith(201, { id: 1 })
    const file = new File(['# BHP'], 'bhp.md')

    await uploadResearchDocument({
      file,
      title: '  BHP outlook ',
      ticker: 'BHP',
      documentDate: '2026-10-12',
    })

    const form = vi.mocked(fetch).mock.calls[0][1]?.body as FormData
    expect(form.get('title')).toBe('BHP outlook')
    expect(form.get('ticker')).toBe('BHP')
    expect(form.get('document_date')).toBe('2026-10-12')
    expect((form.get('file') as File).name).toBe('bhp.md')
  })
})
