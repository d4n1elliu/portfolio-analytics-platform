// The trash icon button that starts deleting a conversation.

import type { Ref } from 'react'

import { COLOUR_TRANSITION } from '../lib/styles'
import TrashIcon from './TrashIcon'

const LABEL = 'Delete conversation'

const BASE = `flex size-8 shrink-0 items-center justify-center rounded-md focus-visible:outline-2 ${COLOUR_TRANSITION}`
const ON_LIGHT =
  'text-slate-500 hover:bg-slate-200 hover:text-red-700 focus-visible:outline-slate-900'
const ON_DARK = 'text-slate-300 hover:bg-slate-700 hover:text-white focus-visible:outline-white'

interface DeleteConversationButtonProps {
  ref?: Ref<HTMLButtonElement>
  onDark?: boolean
  onClick: () => void
}

function DeleteConversationButton({ ref, onDark = false, onClick }: DeleteConversationButtonProps) {
  return (
    <button
      ref={ref}
      type="button"
      aria-label={LABEL}
      title={LABEL}
      onClick={onClick}
      className={`${BASE} ${onDark ? ON_DARK : ON_LIGHT}`}
    >
      <TrashIcon />
    </button>
  )
}

export default DeleteConversationButton
