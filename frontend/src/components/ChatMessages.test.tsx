// @vitest-environment jsdom
// Tests for ChatMessages and the tools shown with an answer.

import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import type { ChatMessage } from '../api/types'
import ChatMessages from './ChatMessages'

const QUESTION: ChatMessage = { id: '1', role: 'user', text: 'What do I hold?', toolCalls: [] }

const ANSWER: ChatMessage = {
  id: '2',
  role: 'assistant',
  text: 'You hold 350 BHP.',
  toolCalls: [
    { id: 'a', name: 'list_holdings', input: 'open positions', output: 'BHP 350', status: 'done' },
    { id: 'b', name: 'get_performance', input: 'year to date', output: null, status: 'running' },
  ],
}

afterEach(cleanup)

describe('ChatMessages', () => {
  it('shows each message in order', () => {
    render(<ChatMessages messages={[QUESTION, ANSWER]} />)

    const shown = screen.getAllByRole('listitem').map((item) => item.textContent)
    expect(shown[0]).toBe('What do I hold?')
    expect(shown[1]).toContain('You hold 350 BHP.')
  })

  it('names each tool an answer used, with its status', () => {
    render(<ChatMessages messages={[ANSWER]} />)

    const tools = screen.getByRole('list', { name: 'Tools used' })
    expect(tools.textContent).toContain('list_holdingsDone')
    expect(tools.textContent).toContain('get_performanceRunning')
  })

  it('shows what a tool got back only once it has answered', () => {
    render(<ChatMessages messages={[ANSWER]} />)

    expect(screen.getAllByText('Got back')).toHaveLength(1)
    expect(screen.getByText('BHP 350')).toBeTruthy()
  })

  it('shows no tools list for a message that used none', () => {
    render(<ChatMessages messages={[QUESTION]} />)

    expect(screen.queryByRole('list', { name: 'Tools used' })).toBeNull()
  })
})
