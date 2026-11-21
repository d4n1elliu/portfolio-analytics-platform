// A form that changes the signed-in user's password.

import { useState } from 'react'
import type { FormEvent } from 'react'

import { changePassword } from '../api/auth'
import { messageFrom } from '../api/client'
import { newPasswordProblem } from '../lib/passwords'
import Alert from './Alert'
import Button from './Button'
import PasswordField from './PasswordField'

type FormState =
  | { status: 'idle' }
  | { status: 'saving' }
  | { status: 'saved' }
  | { status: 'error'; message: string }

function ChangePasswordForm() {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [state, setState] = useState<FormState>({ status: 'idle' })

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const problem = newPasswordProblem(newPassword, confirmation)
    if (problem !== null) {
      setState({ status: 'error', message: problem })
      return
    }

    setState({ status: 'saving' })
    try {
      await changePassword(currentPassword, newPassword)
      setCurrentPassword('')
      setNewPassword('')
      setConfirmation('')
      setState({ status: 'saved' })
    } catch (error) {
      setState({ status: 'error', message: messageFrom(error, 'The password was not changed.') })
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-md space-y-4">
      {state.status === 'saved' && (
        <Alert variant="success">
          Your password has been changed. You have been signed out everywhere else.
        </Alert>
      )}
      {state.status === 'error' && <Alert variant="error">{state.message}</Alert>}
      <PasswordField
        label="Current password"
        value={currentPassword}
        autoComplete="current-password"
        onChange={setCurrentPassword}
      />
      <PasswordField
        label="New password"
        value={newPassword}
        autoComplete="new-password"
        onChange={setNewPassword}
      />
      <PasswordField
        label="New password again"
        value={confirmation}
        autoComplete="new-password"
        onChange={setConfirmation}
      />
      <Button type="submit" disabled={state.status === 'saving'}>
        {state.status === 'saving' ? 'Saving…' : 'Change password'}
      </Button>
    </form>
  )
}

export default ChangePasswordForm
