import { useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { Navigate, useLocation } from 'react-router'

import Alert from '../components/Alert'
import Button from '../components/Button'
import Card from '../components/Card'
import PageLayout from '../components/PageLayout'
import PasswordField from '../components/PasswordField'
import TextField from '../components/TextField'
import { useSignInAttempt } from '../hooks/useSignInAttempt'
import { useAuth } from '../lib/auth'
import { formatTimer } from '../lib/format'
import { MUTED_TEXT } from '../lib/styles'
import { HOME, returnPage } from '../routes'

function LoginPage() {
  const { state } = useAuth()
  const signIn = useSignInAttempt()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const passwordBox = useRef<HTMLInputElement>(null)
  const cameFrom = returnPage(useLocation().state)
  const locked = signIn.lockSecondsLeft > 0

  // A successful sign in changes the state, which sends the user on from here,
  // back to the page they first asked for.
  if (state.status === 'signedIn') return <Navigate to={cameFrom?.path ?? HOME} replace />

  async function handleSubmit(event: FormEvent) {
    event.preventDefault() // Stop the browser reloading the page.
    const signedIn = await signIn.attempt(email, password)
    if (signedIn === false) {
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
              key={signIn.failures}
              error={signIn.error}
              lockEnded={signIn.lockEnded}
              sessionExpired={state.status === 'signedOut' && state.reason === 'expired'}
              redirectedFrom={cameFrom?.label}
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
            <Button type="submit" disabled={signIn.submitting || locked}>
              {submitLabel(signIn.submitting, signIn.lockSecondsLeft)}
            </Button>
          </form>
          <p className={`mt-4 ${MUTED_TEXT}`}>
            Accounts are created by an administrator. There is no public sign-up.
          </p>
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
  error: string | null
  lockEnded: boolean
  sessionExpired: boolean
  redirectedFrom?: string
}

function SignInMessage(props: SignInMessageProps) {
  const { error, lockEnded, sessionExpired, redirectedFrom } = props

  if (lockEnded) return <Alert variant="info">You can try signing in again.</Alert>
  if (error) return <Alert variant="error">{error}</Alert>
  if (sessionExpired) {
    return <Alert variant="warning">Your session has ended. Sign in again to continue.</Alert>
  }
  if (redirectedFrom) return <Alert variant="info">Sign in to view {redirectedFrom}.</Alert>
  return null
}

export default LoginPage
