import { useRef, useState } from 'react'

import { ApiError, messageFrom } from '../api/client'
import { useAuth } from '../lib/auth'
import { useCountdown } from './useCountdown'

export function useSignInAttempt() {
  const { signIn } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [failures, setFailures] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  // Set at once, unlike state, so a second attempt in the same instant is ignored.
  const inFlight = useRef(false)
  // After too many failures the API refuses sign-ins for a while.
  const [lockSecondsLeft, startLock] = useCountdown()
  const [wasLocked, setWasLocked] = useState(false)
  const locked = lockSecondsLeft > 0

  /** Returns true if signed in, false if it failed, and null if the attempt was ignored. */
  async function attempt(email: string, password: string): Promise<boolean | null> {
    if (inFlight.current || locked) return null

    inFlight.current = true
    setSubmitting(true)
    try {
      await signIn(email, password)
      return true
    } catch (error) {
      // The last error stays until this one replaces it, so the form does
      // not shrink and grow on every attempt.
      setError(messageFrom(error, 'Could not sign in.'))
      const wait = error instanceof ApiError ? error.retryAfterSeconds : null
      if (wait !== null) startLock(wait)
      setWasLocked(wait !== null)
      setFailures((count) => count + 1)
      return false
    } finally {
      setSubmitting(false)
      inFlight.current = false
    }
  }

  return {
    attempt,
    submitting,
    error,
    failures,
    lockSecondsLeft,
    lockEnded: wasLocked && !locked,
  }
}
