// Tests for the rules a new password must meet.

import { describe, expect, it } from 'vitest'

import { newPasswordProblem } from './passwords'

describe('newPasswordProblem', () => {
  it('accepts a long enough password typed the same twice', () => {
    expect(newPasswordProblem('a new test password', 'a new test password')).toBeNull()
  })

  it('refuses a password that is too short', () => {
    expect(newPasswordProblem('short', 'short')).toBe(
      'The new password must be at least 12 characters.',
    )
  })

  it('refuses two passwords that differ', () => {
    expect(newPasswordProblem('a new test password', 'a new test passwor')).toBe(
      'The two new passwords do not match.',
    )
  })
})
