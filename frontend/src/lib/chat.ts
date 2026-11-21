// The questions offered on an empty chat, and how a new chat message is built.

import type { ChatMessage, ChatRole } from '../api/types'

export const SUGGESTED_QUESTIONS = [
  'What are my five largest holdings?',
  'How has the portfolio done this year against the benchmark?',
  'Which trades were made in BHP, and what did they realise?',
]

export const NOT_CONNECTED = 'The assistant is not connected yet, so it cannot answer.'

export function newMessage(role: ChatRole, text: string): ChatMessage {
  return { id: crypto.randomUUID(), role, text, toolCalls: [] }
}

export function isSendable(text: string): boolean {
  return text.trim() !== ''
}
