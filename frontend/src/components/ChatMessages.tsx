// The messages of a conversation: the user's on the right, the assistant's on the left with its tools.

import type { ChatMessage } from '../api/types'
import ToolCalls from './ToolCalls'

const BUBBLE = 'w-fit max-w-[85%] space-y-2 rounded-lg px-4 py-3 text-sm whitespace-pre-wrap'
const USER_BUBBLE = 'ml-auto bg-slate-900 text-white'
const ASSISTANT_BUBBLE = 'border border-slate-200 bg-slate-50'

function ChatMessages({ messages }: { messages: ChatMessage[] }) {
  return (
    <ol aria-label="Conversation" className="space-y-3">
      {messages.map((message) => (
        <li
          key={message.id}
          className={`${BUBBLE} ${message.role === 'user' ? USER_BUBBLE : ASSISTANT_BUBBLE}`}
        >
          <ToolCalls toolCalls={message.toolCalls} />
          {message.text !== '' && <p>{message.text}</p>}
        </li>
      ))}
    </ol>
  )
}

export default ChatMessages
