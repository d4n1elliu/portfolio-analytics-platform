import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError, request, setSessionExpiredHandler } from './client'

function answerWith(status: number, body?: unknown, headers?: Record<string, string>) {
  const text = body === undefined ? null : JSON.stringify(body)
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => new Response(text, { status, headers })),
  )
}

async function failureOf(path: string): Promise<ApiError> {
  const error = await request(path).catch((thrown: unknown) => thrown)
  expect(error).toBeInstanceOf(ApiError)
  return error as ApiError
}

afterEach(() => setSessionExpiredHandler(null))

describe('request', () => {
  it('returns the JSON body and sends the session cookie', async () => {
    answerWith(200, [{ ticker: 'BHP' }])

    expect(await request('/holdings')).toEqual([{ ticker: 'BHP' }])
    expect(fetch).toHaveBeenCalledWith(expect.stringMatching(/\/holdings$/), {
      credentials: 'include',
    })
  })

  it('returns null for an answer with no body', async () => {
    answerWith(204)

    expect(await request('/auth/logout')).toBeNull()
  })

  it("throws the API's own message and how long to wait", async () => {
    answerWith(429, { detail: 'Too many failed sign-ins.' }, { 'Retry-After': '90' })

    const error = await failureOf('/auth/login')

    expect(error.message).toBe('Too many failed sign-ins.')
    expect(error.status).toBe(429)
    expect(error.retryAfterSeconds).toBe(90)
  })

  it('falls back to the status when the error has no message', async () => {
    answerWith(500)

    expect((await failureOf('/holdings')).message).toBe('The request failed (HTTP 500).')
  })

  it('reports an API that cannot be reached with status 0', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    expect((await failureOf('/holdings')).status).toBe(0)
  })

  it('lets a cancelled request through unchanged', async () => {
    const cancelled = new DOMException('Cancelled', 'AbortError')
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(cancelled))

    await expect(request('/holdings')).rejects.toBe(cancelled)
  })
})

describe('an expired session', () => {
  it('is reported when a data endpoint answers 401', async () => {
    const onExpired = vi.fn()
    setSessionExpiredHandler(onExpired)
    answerWith(401, { detail: 'Sign in to continue.' })

    await failureOf('/holdings')

    expect(onExpired).toHaveBeenCalledOnce()
  })

  it('is not reported by the sign in endpoints, which answer 401 for a wrong password', async () => {
    const onExpired = vi.fn()
    setSessionExpiredHandler(onExpired)
    answerWith(401, { detail: 'Incorrect email or password.' })

    await failureOf('/auth/login')

    expect(onExpired).not.toHaveBeenCalled()
  })
})
