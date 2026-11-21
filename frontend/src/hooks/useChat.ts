// Holds one conversation with the assistant, and fills in each answer as it streams.

import { useCallback, useEffect, useRef, useState } from 'react'

import { getConversation, streamChat } from '../api/chat'
import { isAbortError, messageFrom } from '../api/client'
import type { ChatEvent, ChatMessage } from '../api/types'
import { applyEvent, isSendable, messagesFromTurns, newMessage } from '../lib/chat'

const COULD_NOT_ANSWER = 'The assistant could not answer. Try again.'
const COULD_NOT_OPEN = 'The conversation could not be opened.'

interface UseChatOptions {
  onConversationUsed: () => void
}

export function useChat({ onConversationUsed }: UseChatOptions) {
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [answering, setAnswering] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const request = useRef<AbortController | null>(null)

  useEffect(() => () => request.current?.abort(), [])

  const show = useCallback((id: string | null, shown: ChatMessage[]) => {
    request.current?.abort()
    request.current = null
    setConversationId(id)
    setMessages(shown)
    setAnswering(false)
    setError(null)
  }, [])

  const startOver = useCallback(() => show(null, []), [show])

  const open = useCallback(
    async (id: string) => {
      show(id, [])
      try {
        const conversation = await getConversation(id)
        setMessages(messagesFromTurns(conversation.turns))
      } catch (thrown) {
        setError(messageFrom(thrown, COULD_NOT_OPEN))
      }
    },
    [show],
  )

  const send = useCallback(
    async (text: string) => {
      if (!isSendable(text) || answering) return
      const question = text.trim()
      const controller = new AbortController()
      request.current = controller
      setMessages((current) => [
        ...current,
        newMessage('user', question),
        newMessage('assistant', ''),
      ])
      setAnswering(true)
      setError(null)

      function handle(event: ChatEvent) {
        if (event.type === 'error') setError(event.message)
        else if (event.type === 'conversation') setConversationId(event.id)
        else setMessages((current) => applyEvent(current, event))
      }

      try {
        await streamChat(question, conversationId, handle, controller.signal)
      } catch (thrown) {
        if (!isAbortError(thrown)) setError(messageFrom(thrown, COULD_NOT_ANSWER))
      } finally {
        if (request.current === controller) setAnswering(false)
        onConversationUsed()
      }
    },
    [answering, conversationId, onConversationUsed],
  )

  return { conversationId, messages, answering, error, send, open, startOver }
}
