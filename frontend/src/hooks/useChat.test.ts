// @vitest-environment jsdom
// Tests for useChat.

import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { streamChat } from '../api/chat'
import type { ChatEvent } from '../api/types'
import { useChat } from './useChat'

vi.mock('../api/chat')

function answerWith(...events: ChatEvent[]) {
  vi.mocked(streamChat).mockImplementation(async (_turns, onEvent) => {
    events.forEach(onEvent)
  })
}

function shown(messages: { role: string; text: string }[]) {
  return messages.map(({ role, text }) => ({ role, text }))
}

beforeEach(() => {
  vi.mocked(streamChat).mockReset()
})

describe('useChat', () => {
  it('adds the question and fills in the answer from the events', async () => {
    answerWith({ type: 'text', text: 'You hold ' }, { type: 'text', text: '350 BHP.' })
    const { result } = renderHook(() => useChat())

    await act(() => result.current.send('  What do I hold?  '))

    expect(shown(result.current.messages)).toEqual([
      { role: 'user', text: 'What do I hold?' },
      { role: 'assistant', text: 'You hold 350 BHP.' },
    ])
    expect(result.current.answering).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('sends the earlier turns with each new question', async () => {
    answerWith({ type: 'text', text: 'You hold 350 BHP.' })
    const { result } = renderHook(() => useChat())
    await act(() => result.current.send('What do I hold?'))

    await act(() => result.current.send('And CBA?'))

    expect(vi.mocked(streamChat).mock.calls[1][0]).toEqual([
      { role: 'user', text: 'What do I hold?' },
      { role: 'assistant', text: 'You hold 350 BHP.' },
      { role: 'user', text: 'And CBA?' },
    ])
  })

  it('shows the error an answer ends with', async () => {
    answerWith({ type: 'error', message: 'The assistant could not answer. Try again.' })
    const { result } = renderHook(() => useChat())

    await act(() => result.current.send('What do I hold?'))

    expect(result.current.error).toBe('The assistant could not answer. Try again.')
  })

  it('shows the reason when the request itself is refused', async () => {
    vi.mocked(streamChat).mockRejectedValue(new Error('You have reached the limit.'))
    const { result } = renderHook(() => useChat())

    await act(() => result.current.send('What do I hold?'))

    expect(result.current.error).toBe('You have reached the limit.')
    expect(result.current.answering).toBe(false)
  })

  it('ignores a question that is only spaces', async () => {
    const { result } = renderHook(() => useChat())

    await act(() => result.current.send('   '))

    expect(result.current.messages).toEqual([])
    expect(streamChat).not.toHaveBeenCalled()
  })

  it('cancels the answer and clears the conversation when started over', async () => {
    let signal: AbortSignal | undefined
    vi.mocked(streamChat).mockImplementation((_turns, _onEvent, given) => {
      signal = given
      return new Promise(() => {})
    })
    const { result } = renderHook(() => useChat())
    act(() => void result.current.send('What do I hold?'))
    await waitFor(() => expect(result.current.answering).toBe(true))

    act(() => result.current.startOver())

    expect(signal?.aborted).toBe(true)
    expect(result.current.messages).toEqual([])
    expect(result.current.answering).toBe(false)
  })
})
