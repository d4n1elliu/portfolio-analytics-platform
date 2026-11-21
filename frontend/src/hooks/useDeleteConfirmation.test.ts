// @vitest-environment jsdom
// Tests for useDeleteConfirmation.

import { act, renderHook } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { useDeleteConfirmation } from './useDeleteConfirmation'

function renderConfirmation(conversationId: string | null) {
  return renderHook(({ id }) => useDeleteConfirmation(id), { initialProps: { id: conversationId } })
}

describe('useDeleteConfirmation', () => {
  it('confirms only after being asked, and stops when cancelled', () => {
    const { result } = renderConfirmation('c1')
    expect(result.current.confirming).toBe(false)

    act(() => result.current.ask())
    expect(result.current.confirming).toBe(true)

    act(() => result.current.cancel())
    expect(result.current.confirming).toBe(false)
  })

  it('stops confirming when a different conversation is shown', () => {
    const { result, rerender } = renderConfirmation('c1')
    act(() => result.current.ask())

    rerender({ id: 'c2' })

    expect(result.current.confirming).toBe(false)
  })

  it('has nothing to confirm when no conversation is open', () => {
    const { result } = renderConfirmation(null)

    act(() => result.current.ask())

    expect(result.current.confirming).toBe(false)
  })
})
