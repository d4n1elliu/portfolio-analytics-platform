// How a conversation with the assistant is built up from the events its answer streams.

import type { ChatEvent, ChatMessage, ChatRole, ChatTurn, ToolCall } from '../api/types'

export const SUGGESTED_QUESTIONS = [
  'What are my five largest holdings?',
  'How has the portfolio done this year against the benchmark?',
  'Which trades were made in BHP, and what did they realise?',
]

const EVENT_PREFIX = 'data: '
const EVENT_SEPARATOR = '\n\n'

export function newMessage(role: ChatRole, text: string): ChatMessage {
  return { id: crypto.randomUUID(), role, text, toolCalls: [] }
}

export function isSendable(text: string): boolean {
  return text.trim() !== ''
}

export function toTurns(messages: ChatMessage[]): ChatTurn[] {
  return messages.filter((message) => message.text !== '').map(({ role, text }) => ({ role, text }))
}

export function readEvents(buffer: string): { events: ChatEvent[]; rest: string } {
  const blocks = buffer.split(EVENT_SEPARATOR)
  const rest = blocks.pop() ?? ''
  const events = blocks
    .filter((block) => block.startsWith(EVENT_PREFIX))
    .map((block) => JSON.parse(block.slice(EVENT_PREFIX.length)) as ChatEvent)
  return { events, rest }
}

export function applyEvent(messages: ChatMessage[], event: ChatEvent): ChatMessage[] {
  const answer = messages.at(-1)
  if (!answer || answer.role !== 'assistant') return messages
  return [...messages.slice(0, -1), answerAfter(answer, event)]
}

function answerAfter(answer: ChatMessage, event: ChatEvent): ChatMessage {
  switch (event.type) {
    case 'text':
      return { ...answer, text: answer.text + event.text }
    case 'tool_call':
      return { ...answer, toolCalls: [...answer.toolCalls, startedToolCall(event)] }
    case 'tool_result':
      return {
        ...answer,
        toolCalls: answer.toolCalls.map((toolCall) =>
          toolCall.id === event.id
            ? { ...toolCall, output: event.output, status: event.failed ? 'failed' : 'done' }
            : toolCall,
        ),
      }
    default:
      return answer
  }
}

function startedToolCall(event: Extract<ChatEvent, { type: 'tool_call' }>): ToolCall {
  return {
    id: event.id,
    name: event.name,
    input: describeInput(event.input),
    output: null,
    status: 'running',
  }
}

export function describeInput(input: Record<string, unknown>): string {
  const given = Object.entries(input).filter(([, value]) => value !== null && value !== undefined)
  if (given.length === 0) return 'Everything, with no filters'
  return given.map(([name, value]) => `${name}: ${String(value)}`).join(', ')
}
