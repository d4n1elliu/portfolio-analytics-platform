// The rules a new password must meet before it is sent to the API.

import { MIN_PASSWORD_LENGTH } from '../config'

export function newPasswordProblem(newPassword: string, confirmation: string): string | null {
  if (newPassword.length < MIN_PASSWORD_LENGTH) {
    return `The new password must be at least ${MIN_PASSWORD_LENGTH} characters.`
  }
  if (newPassword !== confirmation) return 'The two new passwords do not match.'
  return null
}
