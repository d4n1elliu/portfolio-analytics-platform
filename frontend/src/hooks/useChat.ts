// Holds one conversation with the assistant, and fills in each answer as it streams.

import { useCallback, useEffect, useRef, useState } from 'react'

import { streamChat } from '../api/chat'
import { isAbortError, messageFrom } from '../api/client'
import type { ChatEvent, ChatMessage } from '../api/types'
import { applyEvent, isSendable, newMessage, toTurns } from '../lib/chat'

const COULD_NOT_ANSWER = 'The assistant could not answer. Try again.'

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [answering, setAnswering] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const request = useRef<AbortController | null>(null)

  useEffect(() => () => request.current?.abort(), [])

  const send = useCallback(
    async (text: string) => {
      if (!isSendable(text) || answering) return
      const asked = [...messages, newMessage('user', text.trim())]
      const controller = new AbortController()
      request.current = controller
      setMessages([...asked, newMessage('assistant', '')])
      setAnswering(true)
      setError(null)

      function handle(event: ChatEvent) {
        if (event.type === 'error') setError(event.message)
        else setMessages((current) => applyEvent(current, event))
      }

      try {
        await streamChat(toTurns(asked), handle, controller.signal)
      } catch (thrown) {
        if (!isAbortError(thrown)) setError(messageFrom(thrown, COULD_NOT_ANSWER))
      } finally {
        if (request.current === controller) setAnswering(false)
      }
    },
    [messages, answering],
  )

  const startOver = useCallback(() => {
    request.current?.abort()
    request.current = null
    setMessages([])
    setAnswering(false)
    setError(null)
  }, [])

  return { messages, answering, error, send, startOver }
}
