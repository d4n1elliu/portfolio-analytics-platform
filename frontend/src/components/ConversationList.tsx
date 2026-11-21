// The user's past conversations with the assistant, and a button to start a new one.

import type { Conversation } from '../api/types'
import type { QueryState } from '../hooks/useApiQuery'
import Button from './Button'
import ConversationRow from './ConversationRow'
import LoadState from './LoadState'

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
              <ConversationRow
                key={conversation.id}
                conversation={conversation}
                open={conversation.id === openId}
                onOpen={() => onOpen(conversation.id)}
                onDelete={() => onDelete(conversation.id)}
              />
            ))}
          </ul>
        )}
      </LoadState>
    </nav>
  )
}

export default ConversationList
