import { describe, expect, it, vi } from 'vitest'

import { listHoldings } from './holdings'

/** The path and query of the one request that was made. */
function requestedPath(): string {
  const url = new URL(vi.mocked(fetch).mock.calls[0][0] as string)
  return url.pathname + url.search
}

describe('listHoldings', () => {
  it('asks for a date only when one is given', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response('[]')),
    )

    await listHoldings({ includeClosed: true, asOf: '' })
    expect(requestedPath()).toBe('/holdings?include_closed=true')

    vi.mocked(fetch).mockClear()
    await listHoldings({ includeClosed: false, asOf: '2026-06-30' })
    expect(requestedPath()).toBe('/holdings?include_closed=false&as_of=2026-06-30')
  })
})
