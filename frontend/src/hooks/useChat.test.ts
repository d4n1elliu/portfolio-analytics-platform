// @vitest-environment jsdom
// Tests for useChat.

import { act, renderHook } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { NOT_CONNECTED } from '../lib/chat'
import { useChat } from './useChat'

describe('useChat', () => {
  it('adds the question, trimmed, and says the assistant is not connected', () => {
    const { result } = renderHook(() => useChat())

    act(() => result.current.send('  What do I hold?  '))

    expect(result.current.messages.map(({ role, text }) => ({ role, text }))).toEqual([
      { role: 'user', text: 'What do I hold?' },
    ])
    expect(result.current.error).toBe(NOT_CONNECTED)
  })

  it('ignores a question that is only spaces', () => {
    const { result } = renderHook(() => useChat())

    act(() => result.current.send('   '))

    expect(result.current.messages).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('clears the conversation when started over', () => {
    const { result } = renderHook(() => useChat())
    act(() => result.current.send('What do I hold?'))

    act(() => result.current.startOver())

    expect(result.current.messages).toEqual([])
    expect(result.current.error).toBeNull()
  })
})
