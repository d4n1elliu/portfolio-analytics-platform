// @vitest-environment jsdom
// Tests for useChat.

import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { getConversation, streamChat } from '../api/chat'
import type { ChatEvent } from '../api/types'
import { useChat } from './useChat'

vi.mock('../api/chat')

const STARTED: ChatEvent = { type: 'conversation', id: 'c1', title: 'What do I hold?' }

function answerWith(...events: ChatEvent[]) {
  vi.mocked(streamChat).mockImplementation(async (_question, _conversationId, onEvent) => {
    events.forEach(onEvent)
  })
}

function renderChat() {
  const onConversationUsed = vi.fn()
  const { result } = renderHook(() => useChat({ onConversationUsed }))
  return { result, onConversationUsed }
}

function shown(messages: { role: string; text: string }[]) {
  return messages.map(({ role, text }) => ({ role, text }))
}

beforeEach(() => {
  vi.mocked(streamChat).mockReset()
  vi.mocked(getConversation).mockReset()
})

describe('useChat', () => {
  it('adds the question and fills in the answer from the events', async () => {
    answerWith(STARTED, { type: 'text', text: 'You hold ' }, { type: 'text', text: '350 BHP.' })
    const { result, onConversationUsed } = renderChat()

    await act(() => result.current.send('  What do I hold?  '))

    expect(shown(result.current.messages)).toEqual([
      { role: 'user', text: 'What do I hold?' },
      { role: 'assistant', text: 'You hold 350 BHP.' },
    ])
    expect(result.current.answering).toBe(false)
    expect(result.current.conversationId).toBe('c1')
    expect(onConversationUsed).toHaveBeenCalledOnce()
  })

  it('starts a conversation, then carries it on with only the new question', async () => {
    answerWith(STARTED, { type: 'text', text: 'You hold 350 BHP.' })
    const { result } = renderChat()
    await act(() => result.current.send('What do I hold?'))

    await act(() => result.current.send('And CBA?'))

    const [first, second] = vi.mocked(streamChat).mock.calls
    expect(first.slice(0, 2)).toEqual(['What do I hold?', null])
    expect(second.slice(0, 2)).toEqual(['And CBA?', 'c1'])
  })

  it('opens a stored conversation with its answers rebuilt from their events', async () => {
    vi.mocked(getConversation).mockResolvedValue({
      id: 'c9',
      title: 'What do I hold?',
      updated_at: '2026-11-21T03:00:00Z',
      turns: [
        { role: 'user', text: 'What do I hold?' },
        { role: 'assistant', events: [{ type: 'text', text: 'You hold 350 BHP.' }] },
      ],
    })
    const { result } = renderChat()

    await act(() => result.current.open('c9'))

    expect(result.current.conversationId).toBe('c9')
    expect(shown(result.current.messages)).toEqual([
      { role: 'user', text: 'What do I hold?' },
      { role: 'assistant', text: 'You hold 350 BHP.' },
    ])
  })

  it('shows the error an answer ends with', async () => {
    answerWith({ type: 'error', message: 'The assistant could not answer. Try again.' })
    const { result } = renderChat()

    await act(() => result.current.send('What do I hold?'))

    expect(result.current.error).toBe('The assistant could not answer. Try again.')
  })

  it('shows the reason when the request itself is refused', async () => {
    vi.mocked(streamChat).mockRejectedValue(new Error('You have reached the limit.'))
    const { result } = renderChat()

    await act(() => result.current.send('What do I hold?'))

    expect(result.current.error).toBe('You have reached the limit.')
    expect(result.current.answering).toBe(false)
  })

  it('ignores a question that is only spaces', async () => {
    const { result } = renderChat()

    await act(() => result.current.send('   '))

    expect(result.current.messages).toEqual([])
    expect(streamChat).not.toHaveBeenCalled()
  })

  it('cancels the answer and clears the conversation when started over', async () => {
    let signal: AbortSignal | undefined
    vi.mocked(streamChat).mockImplementation((_question, _conversationId, _onEvent, given) => {
      signal = given
      return new Promise(() => {})
    })
    const { result } = renderChat()
    act(() => void result.current.send('What do I hold?'))
    await waitFor(() => expect(result.current.answering).toBe(true))

    act(() => result.current.startOver())

    expect(signal?.aborted).toBe(true)
    expect(result.current.messages).toEqual([])
    expect(result.current.conversationId).toBeNull()
    expect(result.current.answering).toBe(false)
  })
})
