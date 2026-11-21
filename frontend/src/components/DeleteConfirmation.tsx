// Asks the user to confirm deleting a conversation, since it cannot be undone.

import { useEffect, useRef } from 'react'

import Button from './Button'

interface DeleteConfirmationProps {
  title?: string
  onCancel: () => void
  onDelete: () => void
}

function DeleteConfirmation({ title, onCancel, onDelete }: DeleteConfirmationProps) {
  const cancelButton = useRef<HTMLButtonElement>(null)

  useEffect(() => cancelButton.current?.focus(), [])

  return (
    <div
      role="group"
      aria-label="Confirm deleting the conversation"
      className="space-y-2 rounded-md border border-slate-300 px-3 py-2 text-sm"
      onKeyDown={(event) => event.key === 'Escape' && onCancel()}
    >
      <p className="font-medium">Delete this conversation?</p>
      {title !== undefined && <p className="truncate text-xs text-slate-500">{title}</p>}
      <div className="flex gap-2">
        <Button ref={cancelButton} variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button onClick={onDelete}>Delete</Button>
      </div>
    </div>
  )
}

export default DeleteConfirmation
