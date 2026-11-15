import { useState } from 'react'
import type { FormEvent } from 'react'
import { Navigate, useLocation } from 'react-router'

import { messageFrom } from '../api/client'
import Alert from '../components/Alert'
import Button from '../components/Button'
import Card from '../components/Card'
import PageLayout from '../components/PageLayout'
import PasswordField from '../components/PasswordField'
import TextField from '../components/TextField'
import { useAuth } from '../lib/auth'
import { HOME, returnPage } from '../routes'

function LoginPage() {
  const { state, signIn } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const cameFrom = returnPage(useLocation().state)
  const expired = state.status === 'signedOut' && state.expired

  // A successful sign in changes the state, which sends the user on from here,
  // back to the page they first asked for.
  if (state.status === 'signedIn') return <Navigate to={cameFrom?.path ?? HOME} replace />

  async function handleSubmit(event: FormEvent) {
    event.preventDefault() // Stop the browser reloading the page.
    setSubmitting(true)
    setError(null)
    try {
      await signIn(email, password)
    } catch (error) {
      setError(messageFrom(error, 'Could not sign in.'))
      setSubmitting(false)
    }
  }

  return (
    <PageLayout>
      <div className="mx-auto mt-12 max-w-md">
        <Card title="Sign in">
          <form onSubmit={handleSubmit} className="space-y-4">
            {!error && <SignInReason expired={expired} pageName={cameFrom?.label} />}
            {error && <Alert variant="error">{error}</Alert>}
            <TextField
              label="Email"
              type="email"
              value={email}
              autoComplete="username"
              onChange={setEmail}
            />
            <PasswordField
              label="Password"
              value={password}
              autoComplete="current-password"
              onChange={setPassword}
            />
            <Button type="submit" disabled={submitting}>
              {submitting ? 'Signing in…' : 'Sign in'}
            </Button>
          </form>
        </Card>
      </div>
    </PageLayout>
  )
}

/** Says why the visitor has to sign in, when there is a reason to give. */
function SignInReason({ expired, pageName }: { expired?: boolean; pageName?: string }) {
  if (expired) {
    return <Alert variant="warning">Your session has ended. Sign in again to continue.</Alert>
  }
  if (pageName) return <Alert variant="info">Sign in to view {pageName}.</Alert>
  return null
}

export default LoginPage
