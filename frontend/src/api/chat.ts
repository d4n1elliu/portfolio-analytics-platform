// The API calls for conversations with the assistant, including the answer as it streams.

import { readEvents } from '../lib/chat'
import { request, requestStream } from './client'
import type { ChatEvent, Conversation, ConversationDetail } from './types'

export async function streamChat(
  question: string,
  conversationId: string | null,
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const body = { question, conversation_id: conversationId }
  const stream = await requestStream('/ai/chat', body, signal)
  const reader = stream.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) return
    const { events, rest } = readEvents(buffer + decoder.decode(value, { stream: true }))
    buffer = rest
    events.forEach(onEvent)
  }
}

export function listConversations(signal?: AbortSignal): Promise<Conversation[]> {
  return request<Conversation[]>('/ai/conversations', { signal })
}

export function getConversation(id: string, signal?: AbortSignal): Promise<ConversationDetail> {
  return request<ConversationDetail>(conversationPath(id), { signal })
}

export async function deleteConversation(id: string): Promise<void> {
  await request(conversationPath(id), { method: 'DELETE' })
}

function conversationPath(id: string): string {
  return `/ai/conversations/${encodeURIComponent(id)}`
}
