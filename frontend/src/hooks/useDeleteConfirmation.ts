// Tracks whether the user is being asked to confirm deleting one conversation.

import { useCallback, useEffect, useRef, useState } from 'react'

export function useDeleteConfirmation(conversationId: string | null) {
  const [askedAbout, setAskedAbout] = useState<string | null>(null)
  const deleteButton = useRef<HTMLButtonElement>(null)
  const focusDeleteNext = useRef(false)
  const confirming = askedAbout !== null && askedAbout === conversationId

  useEffect(() => {
    if (!confirming && focusDeleteNext.current) {
      focusDeleteNext.current = false
      deleteButton.current?.focus()
    }
  }, [confirming])

  const ask = useCallback(() => setAskedAbout(conversationId), [conversationId])
  const cancel = useCallback(() => {
    focusDeleteNext.current = true
    setAskedAbout(null)
  }, [])

  return { confirming, deleteButton, ask, cancel }
}
