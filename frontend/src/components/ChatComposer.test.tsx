// @vitest-environment jsdom
// Tests for ChatComposer.

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import ChatComposer from './ChatComposer'

function renderComposer(text: string) {
  const onSend = vi.fn()
  const onChange = vi.fn()
  render(<ChatComposer text={text} onChange={onChange} onSend={onSend} />)
  return { onSend, onChange, box: screen.getByLabelText('Your question') }
}

afterEach(cleanup)

describe('ChatComposer', () => {
  it('sends the question and empties the box when Enter is pressed', () => {
    const { onSend, onChange, box } = renderComposer('What do I hold?')

    fireEvent.keyDown(box, { key: 'Enter' })

    expect(onSend).toHaveBeenCalledWith('What do I hold?')
    expect(onChange).toHaveBeenCalledWith('')
  })

  it('does not send when Shift is held, so a new line can be typed', () => {
    const { onSend, box } = renderComposer('What do I hold?')

    fireEvent.keyDown(box, { key: 'Enter', shiftKey: true })

    expect(onSend).not.toHaveBeenCalled()
  })

  it('sends when the button is clicked', () => {
    const { onSend } = renderComposer('What do I hold?')

    fireEvent.click(screen.getByRole('button', { name: 'Send' }))

    expect(onSend).toHaveBeenCalledWith('What do I hold?')
  })

  it('cannot send an empty question', () => {
    const { onSend, box } = renderComposer('   ')

    fireEvent.keyDown(box, { key: 'Enter' })

    expect(onSend).not.toHaveBeenCalled()
    expect(screen.getByRole('button', { name: 'Send' })).toHaveProperty('disabled', true)
  })
})
