// Holds the messages of one conversation with the assistant.

import { useCallback, useState } from 'react'

import type { ChatMessage } from '../api/types'
import { NOT_CONNECTED, isSendable, newMessage } from '../lib/chat'

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [error, setError] = useState<string | null>(null)

  const send = useCallback((text: string) => {
    if (!isSendable(text)) return
    setMessages((current) => [...current, newMessage('user', text.trim())])
    setError(NOT_CONNECTED)
  }, [])

  const startOver = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return { messages, error, send, startOver }
}
