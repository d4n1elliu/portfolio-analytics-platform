// The box a question is typed into. Enter sends it, and Shift+Enter starts a new line.

import type { FormEvent, KeyboardEvent } from 'react'

import { isSendable } from '../lib/chat'
import { FOCUS_OUTLINE, TEXT_BOX } from '../lib/styles'
import Button from './Button'

interface ChatComposerProps {
  text: string
  onChange: (text: string) => void
  onSend: (text: string) => void
}

function ChatComposer({ text, onChange, onSend }: ChatComposerProps) {
  function send() {
    if (!isSendable(text)) return
    onSend(text)
    onChange('')
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    send()
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== 'Enter' || event.shiftKey) return
    event.preventDefault()
    send()
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-3">
      <textarea
        aria-label="Your question"
        rows={2}
        value={text}
        placeholder="Ask about the portfolio"
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        className={`${TEXT_BOX} resize-none py-2 ${FOCUS_OUTLINE}`}
      />
      <Button type="submit" disabled={!isSendable(text)}>
        Send
      </Button>
    </form>
  )
}

export default ChatComposer
