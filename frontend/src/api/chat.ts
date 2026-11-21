// The API call that asks the assistant a question and reads its answer as it streams.

import { readEvents } from '../lib/chat'
import { requestStream } from './client'
import type { ChatEvent, ChatTurn } from './types'

export async function streamChat(
  turns: ChatTurn[],
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const stream = await requestStream('/ai/chat', { messages: turns }, signal)
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
