import { useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { Navigate, useLocation } from 'react-router'

import { ApiError, messageFrom } from '../api/client'
import Alert from '../components/Alert'
import Button from '../components/Button'
import Card from '../components/Card'
import PageLayout from '../components/PageLayout'
import PasswordField from '../components/PasswordField'
import TextField from '../components/TextField'
import { useCountdown } from '../hooks/useCountdown'
import { useAuth } from '../lib/auth'
import { formatTimer } from '../lib/format'
import { HOME, returnPage } from '../routes'

function LoginPage() {
  const { state, signIn } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [attempts, setAttempts] = useState(0)
  const passwordBox = useRef<HTMLInputElement>(null)
  // Set at once, unlike state, so a second submit in the same instant is ignored.
  const inFlight = useRef(false)
  // After too many failures the API refuses sign-ins for a while.
  const [lockSecondsLeft, startLock] = useCountdown()
  const [wasLocked, setWasLocked] = useState(false)
  const locked = lockSecondsLeft > 0
  const lockEnded = wasLocked && !locked
  const cameFrom = returnPage(useLocation().state)
  const expired = state.status === 'signedOut' && state.reason === 'expired'

  // A successful sign in changes the state, which sends the user on from here,
  // back to the page they first asked for.
  if (state.status === 'signedIn') return <Navigate to={cameFrom?.path ?? HOME} replace />

  async function handleSubmit(event: FormEvent) {
    event.preventDefault() // Stop the browser reloading the page.
    if (inFlight.current || locked) return

    inFlight.current = true
    setSubmitting(true)
    try {
      await signIn(email, password)
    } catch (error) {
      // The last error stays on screen until this one replaces it, so the
      // card does not shrink and grow on every attempt.
      setError(messageFrom(error, 'Could not sign in.'))
      const wait = error instanceof ApiError ? error.retryAfterSeconds : null
      if (wait !== null) startLock(wait)
      setWasLocked(wait !== null)
      setAttempts((count) => count + 1)
      setSubmitting(false)
      inFlight.current = false
      // The email is kept. The password is retyped.
      setPassword('')
      passwordBox.current?.focus()
    }
  }

  return (
    <PageLayout>
      <div className="mx-auto mt-12 max-w-md">
        <Card title="Sign in">
          <form onSubmit={handleSubmit} className="space-y-4">
            <SignInMessage
              // A new key makes screen readers announce the same error again.
              key={attempts}
              error={lockEnded ? null : error}
              lockEnded={lockEnded}
              expired={expired}
              pageName={cameFrom?.label}
            />
            <TextField
              label="Email"
              type="email"
              value={email}
              autoComplete="username"
              onChange={setEmail}
              autoFocus
            />
            <PasswordField
              label="Password"
              value={password}
              autoComplete="current-password"
              onChange={setPassword}
              inputRef={passwordBox}
            />
            <Button type="submit" disabled={submitting || locked}>
              {submitLabel(submitting, lockSecondsLeft)}
            </Button>
          </form>
        </Card>
      </div>
    </PageLayout>
  )
}

function submitLabel(submitting: boolean, lockSecondsLeft: number): string {
  if (lockSecondsLeft > 0) return `Try again in ${formatTimer(lockSecondsLeft)}`
  return submitting ? 'Signing in…' : 'Sign in'
}

interface SignInMessageProps {
  /** Why the last sign in failed. */
  error: string | null
  /** True once a lockout is over. */
  lockEnded: boolean
  /** True when the visitor's session ended while they were signed in. */
  expired: boolean
  /** The page that sent the visitor here, if one did. */
  pageName?: string
}

/** The one message above the form: the latest error, or why the visitor has to sign in. */
function SignInMessage({ error, lockEnded, expired, pageName }: SignInMessageProps) {
  if (error) return <Alert variant="error">{error}</Alert>
  if (lockEnded) return <Alert variant="info">You can try signing in again.</Alert>
  if (expired) {
    return <Alert variant="warning">Your session has ended. Sign in again to continue.</Alert>
  }
  if (pageName) return <Alert variant="info">Sign in to view {pageName}.</Alert>
  return null
}

export default LoginPage
