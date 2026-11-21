import { describe, expect, it, vi } from 'vitest'

import { getHolding, listHoldings } from './holdings'

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

describe('getHolding', () => {
  it('returns nothing for a ticker no security has', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response('{"detail":"Not found"}', { status: 404 })),
    )

    expect(await getHolding('XYZ')).toBeNull()
    expect(requestedPath()).toBe('/holdings/XYZ')
  })

  it('still throws any other error', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response(null, { status: 500 })),
    )

    await expect(getHolding('BHP')).rejects.toThrow('The request failed (HTTP 500).')
  })
})
