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
import { ROUTES } from '../routes'

function LoginPage() {
  const { state, signIn } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const from = (useLocation().state as { from?: string } | null)?.from

  // A successful sign in changes the state, which sends the user on from here,
  // back to the page they first asked for.
  if (state.status === 'signedIn') return <Navigate to={from ?? ROUTES.holdings} replace />

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

export default LoginPage
