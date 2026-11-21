// @vitest-environment jsdom
import { act, renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { useApiQuery } from './useApiQuery'

describe('useApiQuery', () => {
  it('is loading, then holds the data', async () => {
    const load = vi.fn().mockResolvedValue('first')
    const { result } = renderHook(() => useApiQuery(load))

    expect(result.current.state).toEqual({ status: 'loading' })
    await waitFor(() => expect(result.current.state).toEqual({ status: 'loaded', data: 'first' }))
  })

  it('holds the message of a failed request', async () => {
    const load = vi.fn().mockRejectedValue(new Error('Could not reach the API.'))
    const { result } = renderHook(() => useApiQuery(load))

    await waitFor(() =>
      expect(result.current.state).toEqual({
        status: 'error',
        message: 'Could not reach the API.',
      }),
    )
  })

  it('ignores a request that was cancelled', async () => {
    const load = vi.fn().mockRejectedValue(new DOMException('Cancelled', 'AbortError'))
    const { result } = renderHook(() => useApiQuery(load))

    await act(async () => {})

    expect(result.current.state).toEqual({ status: 'loading' })
  })

  it('cancels the request when the component is removed', () => {
    const load = vi.fn((_signal: AbortSignal) => new Promise<string>(() => {}))
    const { unmount } = renderHook(() => useApiQuery(load))

    unmount()

    expect(load.mock.calls[0][0].aborted).toBe(true)
  })

  it('goes back to loading on a reload', async () => {
    const load = vi.fn().mockResolvedValueOnce('first').mockResolvedValueOnce('second')
    const { result } = renderHook(() => useApiQuery(load))
    await waitFor(() => expect(result.current.state.status).toBe('loaded'))

    act(() => result.current.reload())

    expect(result.current.state).toEqual({ status: 'loading' })
    await waitFor(() => expect(result.current.state).toEqual({ status: 'loaded', data: 'second' }))
  })

  it('can keep the last data on screen while newer data loads', async () => {
    const load = vi.fn().mockResolvedValueOnce('first').mockResolvedValueOnce('second')
    const { result } = renderHook(() => useApiQuery(load, { keepPreviousData: true }))
    await waitFor(() => expect(result.current.state.status).toBe('loaded'))

    act(() => result.current.reload())

    expect(result.current.state).toEqual({ status: 'loaded', data: 'first' })
    expect(result.current.isRefreshing).toBe(true)
    await waitFor(() => expect(result.current.state).toEqual({ status: 'loaded', data: 'second' }))
    expect(result.current.isRefreshing).toBe(false)
  })
})
