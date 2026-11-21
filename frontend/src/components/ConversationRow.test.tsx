// @vitest-environment jsdom
// Tests for ConversationRow.

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import ConversationRow from './ConversationRow'

const CONVERSATION = { id: 'c1', title: 'What do I hold?', updated_at: '2026-11-21T03:00:00Z' }

function renderRow(open = false) {
  const onOpen = vi.fn()
  const onDelete = vi.fn()
  render(
    <ul>
      <ConversationRow
        conversation={CONVERSATION}
        open={open}
        onOpen={onOpen}
        onDelete={onDelete}
      />
    </ul>,
  )
  return { onOpen, onDelete }
}

function deleteButton() {
  return screen.getByRole('button', { name: 'Delete conversation' })
}

afterEach(cleanup)

describe('ConversationRow', () => {
  it('opens the conversation when its title is clicked', () => {
    const { onOpen } = renderRow()

    fireEvent.click(screen.getByRole('button', { name: /What do I hold\?/ }))

    expect(onOpen).toHaveBeenCalledOnce()
  })

  it('names the delete button and gives it a tooltip', () => {
    renderRow()

    expect(deleteButton().title).toBe('Delete conversation')
  })

  it('asks before deleting, without opening or deleting the conversation', () => {
    const { onOpen, onDelete } = renderRow()

    fireEvent.click(deleteButton())

    expect(screen.getByText('Delete this conversation?')).toBeTruthy()
    expect(document.activeElement).toBe(screen.getByRole('button', { name: 'Cancel' }))
    expect(onOpen).not.toHaveBeenCalled()
    expect(onDelete).not.toHaveBeenCalled()
  })

  it('deletes once confirmed', () => {
    const { onDelete } = renderRow()
    fireEvent.click(deleteButton())

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }))

    expect(onDelete).toHaveBeenCalledOnce()
  })

  it.each([
    ['Cancel is clicked', () => fireEvent.click(screen.getByRole('button', { name: 'Cancel' }))],
    ['Escape is pressed', () => fireEvent.keyDown(document.activeElement!, { key: 'Escape' })],
  ])('keeps the conversation and returns to the delete button when %s', (_how, cancel) => {
    const { onDelete } = renderRow()
    fireEvent.click(deleteButton())

    cancel()

    expect(onDelete).not.toHaveBeenCalled()
    expect(screen.queryByText('Delete this conversation?')).toBeNull()
    expect(document.activeElement).toBe(deleteButton())
  })

  it('marks the open conversation', () => {
    renderRow(true)

    const title = screen.getByRole('button', { name: /What do I hold\?/ })
    expect(title.getAttribute('aria-current')).toBe('true')
  })
})
