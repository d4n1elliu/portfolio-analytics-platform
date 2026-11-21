// One conversation in the list: its title and date, and a delete button that asks first.

import type { Conversation } from '../api/types'
import { useDeleteConfirmation } from '../hooks/useDeleteConfirmation'
import { formatDateTime } from '../lib/format'
import { COLOUR_TRANSITION } from '../lib/styles'
import DeleteConfirmation from './DeleteConfirmation'
import DeleteConversationButton from './DeleteConversationButton'

const ROW = `flex items-center gap-1 rounded-md pr-1 ${COLOUR_TRANSITION}`
const TITLE =
  'min-w-0 flex-1 rounded-md px-3 py-2 text-left text-sm focus-visible:outline-2 focus-visible:-outline-offset-2'

const OPEN = { row: 'bg-slate-900 text-white', title: 'focus-visible:outline-white' }
const NOT_OPEN = { row: 'hover:bg-slate-100', title: 'focus-visible:outline-slate-900' }

interface ConversationRowProps {
  conversation: Conversation
  open: boolean
  onOpen: () => void
  onDelete: () => void
}

function ConversationRow({ conversation, open, onOpen, onDelete }: ConversationRowProps) {
  const { confirming, deleteButton, ask, cancel } = useDeleteConfirmation(conversation.id)

  if (confirming) {
    return (
      <li>
        <DeleteConfirmation title={conversation.title} onCancel={cancel} onDelete={onDelete} />
      </li>
    )
  }

  const colours = open ? OPEN : NOT_OPEN
  return (
    <li className={`${ROW} ${colours.row}`}>
      <button
        type="button"
        aria-current={open ? 'true' : undefined}
        onClick={onOpen}
        className={`${TITLE} ${colours.title}`}
      >
        <span className="block truncate font-medium">{conversation.title}</span>
        <span className="block text-xs opacity-70">{formatDateTime(conversation.updated_at)}</span>
      </button>
      <DeleteConversationButton ref={deleteButton} onDark={open} onClick={ask} />
    </li>
  )
}

export default ConversationRow
