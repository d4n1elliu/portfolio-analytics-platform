// Tests for what a signed-in user is allowed to do.

import { describe, expect, it } from 'vitest'

import type { Permission, User } from '../api/types'
import { allowedActions, can } from './roles'

function user(permissions: Permission[]): User {
  return {
    email: 'pm@example.com',
    name: 'Demo PM',
    role: 'portfolio_manager',
    permissions,
    ai_enabled: false,
  }
}

describe('can', () => {
  it('is true only for a permission the user holds', () => {
    expect(can(user(['export_trades']), 'export_trades')).toBe(true)
    expect(can(user(['export_trades']), 'import_trades')).toBe(false)
  })

  it('is false when nobody is signed in', () => {
    expect(can(null, 'export_trades')).toBe(false)
  })
})

describe('allowedActions', () => {
  it('always starts with viewing, then names each permission', () => {
    expect(allowedActions(user([]))).toBe('View everything')
    expect(allowedActions(user(['export_trades', 'import_trades']))).toBe(
      'View everything, Export trades, Import trades',
    )
  })
})
