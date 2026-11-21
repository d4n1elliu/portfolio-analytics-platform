// The user's past conversations with the assistant. One can be opened, deleted or started.

import type { Conversation } from '../api/types'
import type { QueryState } from '../hooks/useApiQuery'
import { formatDateTime } from '../lib/format'
import { COLOUR_TRANSITION, FOCUS_OUTLINE } from '../lib/styles'
import Button from './Button'
import LoadState from './LoadState'

const ROW = `w-full rounded-md px-3 py-2 text-left text-sm ${COLOUR_TRANSITION} ${FOCUS_OUTLINE}`
const OPEN = 'bg-slate-900 text-white'
const NOT_OPEN = 'hover:bg-slate-100'

interface ConversationListProps {
  state: QueryState<Conversation[]>
  openId: string | null
  onRetry: () => void
  onOpen: (id: string) => void
  onDelete: (id: string) => void
  onStartNew: () => void
}

function ConversationList(props: ConversationListProps) {
  const { state, openId, onRetry, onOpen, onDelete, onStartNew } = props

  return (
    <nav aria-label="Conversations" className="space-y-3">
      <Button variant="secondary" className="w-full" onClick={onStartNew}>
        New conversation
      </Button>
      <LoadState
        state={state}
        onRetry={onRetry}
        loadingText="Loading conversations…"
        emptyText="No conversations yet."
        isEmpty={(loaded) => loaded.length === 0}
      >
        {(loaded) => (
          <ul className="space-y-1">
            {loaded.map((conversation) => (
              <li key={conversation.id} className="flex items-start gap-1">
                <button
                  type="button"
                  aria-current={conversation.id === openId ? 'true' : undefined}
                  onClick={() => onOpen(conversation.id)}
                  className={`${ROW} ${conversation.id === openId ? OPEN : NOT_OPEN}`}
                >
                  <span className="block truncate font-medium">{conversation.title}</span>
                  <span className="block text-xs opacity-70">
                    {formatDateTime(conversation.updated_at)}
                  </span>
                </button>
                <Button
                  variant="secondary"
                  aria-label={`Delete the conversation ${conversation.title}`}
                  onClick={() => onDelete(conversation.id)}
                >
                  Delete
                </Button>
              </li>
            ))}
          </ul>
        )}
      </LoadState>
    </nav>
  )
}

export default ConversationList
